import os
import datetime

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.db import *

router = Router()

welcome_message = """
🙋Приветствую Вас в моем боте, который разработан для канала ["Название канала"](ссылка на канал)!
Начиная пользоваться им Вы принимаете [Условия Использования](ссылка на условия использования telegraph).
Для тех, кто не хочет их читать, краткое содержание.
За все публикации несете ответственность ТОЛЬКО ВЫ.
Запрещено отправлять (может карается удалением сообщения и баном):
1. Бессмысленные или повторяющиеся по смыслу сообщения
2. Порнографические материалы   
3. Реклама без моего согласия
4. Сообщения нарушающие законодательство РФ
Все другие вопросы либо уже указаны в [Условиях Использования](ссылка на условия использования telegraph).
"""

allowed_types = {"text", "photo", "video", "audio", "voice", "sticker", "animation", "video_note", "poll"}
prohibited_types = {"document", "invoice", "dice", "location", "venue", "contact"}

channel_id = int(os.getenv("CHANNEL_ID"))


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(welcome_message)
   
 
@router.message(F.content_type.in_(prohibited_types))
async def prohibited_messages_handler(message: Message) -> None:
    await message.answer("Отправка сообщений этого типа запрещена")


@router.message(F.content_type.in_(allowed_types))
async def allowed_messages_handler(message: Message) -> None:
    create_db()
    result = check_message(message)
    if result:
        await message.answer(result)
    else:
        channel_message = await message.copy_to(channel_id)
        add_new_message_to_db(message, channel_message.message_id)
        await message.answer("Ваше сообщение успешно отправлено")


def check_message(message: Message) -> str | None:
    acceptable_time = get_acceptable_time()
    if message.date.timestamp() < acceptable_time:
        return f"Администратор заблокировал отправку сообщений до {datetime.fromtimestamp(acceptable_time).strftime("%H:%M:%S %d/%m/%Y")}"
    elif not check_for_user_existence(message.from_user.id):
        add_new_user_to_db(message)
    elif check_user_for_blocking(message.from_user.id):
        return "Вы были заблокированы администратором. Если Вы считаете, что блокировка несправедлива, то пишите @username"
    elif not check_time_for_sending(message):
        return "С отправки сообщения должно пройти 15 минут, подождите ещё"
