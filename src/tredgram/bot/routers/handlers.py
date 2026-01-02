from __future__ import annotations

import asyncio
import io
import logging
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import openai
import pandas as pd
from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, Message
from aiogram.utils.i18n import gettext as _
from aiohttp import BasicAuth, ClientSession
from common import config
from db import QAModel, UserModel, session_maker
from httpx import AsyncClient
from sqlalchemy import select

logger = logging.getLogger("virtual_assistant")
clear_text_pattern = re.compile(r"【.*?†.*?】")

router = Router()
openai_client = openai.AsyncOpenAI(
    api_key=config.openai_api_key.get_secret_value(),
    http_client=AsyncClient(proxy=config.proxy.get_secret_value(), timeout=60),
)


class WaitingState(StatesGroup):
    waiting = State()


@router.message(WaitingState.waiting)
async def waiting_message(message: Message) -> None:
    await message.answer(
        _("please wait message"),
        parse_mode="HTML",
    )


@router.message(Command("observe"))
async def send_info_for_observer(message: Message, command: CommandObject) -> None:
    if not (
        message.chat.id == config.observer_tg_id
        or command.args == config.observer_password.get_secret_value()
    ):
        logger.warning("User @%s tried to become observer", message.from_user.username)
        await message.answer(
            _("incorrect message"),
            parse_mode="HTML",
        )
        return

    logger.info(
        "Report generation for observer @%s started", message.from_user.username
    )
    async with session_maker() as db:
        now = datetime.now(ZoneInfo("Europe/Moscow")).replace(tzinfo=None)
        yesterday = now - timedelta(days=1)

        # Last's day question and answers
        qas = await db.scalars(
            select(QAModel).where(
                (QAModel.sended_at >= yesterday) & (QAModel.sended_at < now),
            ),
        )

        qas_array = [(qa.question, qa.answer) for qa in qas.all()]
        df_qas = pd.DataFrame(qas_array, columns=["Вопросы", "Ответы"])
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer) as writer:
            df_qas.to_excel(writer, index=False)
        buffer.seek(0)

        await message.answer_document(
            BufferedInputFile(buffer.getvalue(), filename="Статистика.xlsx"),
        )


@router.message(CommandStart())
async def start_handler(message: Message, command: CommandObject) -> None:
    logger.info(
        "New start command from @%s with hash id '%s'",
        message.from_user.username,
        command.args,
    )
    async with session_maker() as db:
        if not await db.get(UserModel, message.from_user.id):
            async with (
                ClientSession(
                    auth=BasicAuth(
                        config.herbalife_username.get_secret_value(),
                        config.herbalife_passwd.get_secret_value(),
                    ),
                ) as session,
                session.get(
                    f"https://leads.herbalife.ru/api/v1/consultant/?filter[hashId]={command.args}",
                    headers={"Token": config.herbalife_token.get_secret_value()},
                ) as res,
            ):
                data = await res.json()

                try:
                    consultant = data["data"]["consultants"][0]
                except (KeyError, IndexError):
                    logger.warning(
                        "User @%s failed authentication", message.from_user.username
                    )
                    await message.answer(
                        _("not authenticated"),
                        parse_mode="HTML",
                    )
                    return

                user = UserModel(
                    id=message.from_user.id,
                    username="@" + message.from_user.username
                    if message.from_user.username
                    else None,
                    tg_name=message.from_user.full_name,
                    hash_id=command.args,
                    external_id=consultant["external_id"],
                    name=f"{consultant['name']} {consultant['last_name']}",
                    phone=consultant.get("phone"),
                    email=consultant.get("email"),
                )
                logger.info(
                    "User has been created with fields:\n\nID: %s\nUsername: %s\nTelegram name: %s\n\n"
                    "Hash ID: %s\nExternal ID: %s\nName: %s\nPhone: %s\nEmail: %s\nThread ID: %s\n",
                    user.id, user.username, user.tg_name, user.hash_id,
                    user.external_id, user.name, user.phone, user.email,
                )  # fmt: skip

                db.add(user)
                await db.commit()
        else:
            logger.info("User %s already log in", message.from_user.id)

        await message.answer(
            _("start message"),
            parse_mode="HTML",
        )


@router.message(F.text)
async def answer_handler(message: Message, state: FSMContext) -> None:
    async with session_maker() as db:
        user = await db.get(UserModel, message.from_user.id)

        if not user:
            await message.answer(
                _("not authenticated"),
                parse_mode="HTML",
            )
            return

        caching_time = datetime.now(ZoneInfo("Europe/Moscow")).replace(
            tzinfo=None
        ) - timedelta(days=config.cache_ttl_days)
        qa_scalars = await db.scalars(
            select(QAModel).where(
                (QAModel.question == message.text)
                & (QAModel.sended_at >= caching_time),
            ),
        )

        if qas := qa_scalars.all():
            new_qa = QAModel(
                tg_id=message.from_user.id,
                question=qas[0].question,
                answer=qas[0].answer,
            )

            db.add(new_qa)
            await db.commit()

            await message.answer(qas[0].answer)
            return

        await state.set_state(WaitingState.waiting)
        answer_message = await message.answer(
            _("message while waiting"), parse_mode="HTML"
        )
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        # Sending answer
        try:
            thread = await openai_client.beta.threads.create()
            await openai_client.beta.threads.messages.create(
                thread.id,
                content=message.text,
                role="user",
            )

            run = await openai_client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=config.assistant_id,
            )

            # Answer waiting
            for unprocessed_var in range(50):
                await asyncio.sleep(2)

                run = await openai_client.beta.threads.runs.retrieve(
                    run.id, thread_id=thread.id
                )
                messages = await openai_client.beta.threads.messages.list(thread.id)

                if run.status == "completed":
                    answer = re.sub(
                        clear_text_pattern, "", messages.data[0].content[0].text.value
                    )
                    logger.info(
                        "The assistant answered user %s's question '%s' like this:\n\n--------%s\n--------",
                        user.username, message.text, answer
                    )  # fmt: skip

                    new_qa = QAModel(
                        tg_id=message.from_user.id,
                        question=message.text,
                        answer=answer,
                    )

                    db.add(new_qa)
                    await db.commit()

                    await answer_message.delete()
                    await message.answer(answer)
                elif run.status == "failed":
                    logger.error(
                        "The assistant could not respond to the message '%s' from %s",
                        message.text,
                        user.username,
                    )
                    await answer_message.edit_text(
                        _("AI answer error message"),
                        parse_mode="HTML",
                    )
                else:
                    continue

                await openai_client.beta.threads.delete(thread.id)
                break
            else:  # If there is no response
                logger.error(
                    "The assistant could not respond to the message '%s' from %s",
                    message.text,
                    user.username,
                )
                await answer_message.edit_text(
                    _("AI answer error message"),
                    parse_mode="HTML",
                )
        except openai.APIConnectionError:
            logger.critical("No connection to ChatGPT!")
            await message.bot.send_message(
                config.observer_tg_id, _("no openai connection")
            )
            await message.answer(
                _("no openai connection"),
                parse_mode="HTML",
            )

    await state.clear()


@router.message()
async def incorrect_message_handler(message: Message) -> None:
    await message.answer(
        _("incorrect message"),
        parse_mode="HTML",
    )
