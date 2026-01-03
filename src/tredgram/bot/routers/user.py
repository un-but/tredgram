from __future__ import annotations

from datetime import datetime

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.i18n import gettext as po
from tredgram.db.dal import UserDAL

router = Router()

prohibited_types = {"document", "invoice", "dice", "location", "venue", "contact"}


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(po("start message"))


@router.message(F.content_type.in_(prohibited_types))
async def prohibited_messages_handler(message: Message) -> None:
    await message.answer("Отправка сообщений этого типа запрещена")


@router.message()
async def allowed_messages_handler(message: Message) -> None:
    if result := await check_message(message):
        await message.answer(result)
    else:
        channel_message = await message.copy_to(CHANNEL_ID)
        await db_create.add_new_message_to_db(message, channel_message.message_id)
        await message.answer("Ваше сообщение успешно отправлено")


async def check_message(message: Message) -> str | None:
    if not await db_read.check_for_user_existence(message.from_user.id):
        await db_create.add_new_user_to_db(message)
    elif message.date.timestamp() < await db_read.get_prohibit_sending_time():
        return f"Администратор заблокировал отправку сообщений до {datetime.fromtimestamp(await db_read.get_prohibit_sending_time()).strftime('%H:%M:%S %d.%m.%Y')}"
    elif await db_read.check_user_for_ban(message.from_user.id):
        return "Вы были заблокированы администратором. Если Вы считаете, что блокировка несправедлива, то пишите @username"
    elif not await db_read.check_time_for_sending(message):
        return "С отправки сообщения должно пройти 15 минут, подождите ещё"

    return None
