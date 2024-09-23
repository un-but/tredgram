import os
import datetime

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from db import *

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
   
 
# Here are functions that handle user messages.
@router.message(F.content_type.in_(prohibited_types))
async def prohibited_messages_handler(message: Message) -> None:
    message.answer("Отправка сообщений этого типа запрещена")


@router.message(F.content_type.in_(allowed_types))
async def allowed_messages_handler(message: Message) -> None:
    create_db()
    result = check_message(message)
    if result:
        message.answer(result)
    else:
        channel_message = message.copy_to(channel_id)
        add_new_message_to_db(message, channel_message.message_id)
        message.answer("Ваше сообщение успешно отправлено")


async def check_message(message) -> str:
    acceptable_time = get_acceptable_time()
    if message.date < acceptable_time:
        return f"Администратор заблокировал отправку сообщений до {datetime.fromtimestamp(acceptable_time).strftime("%H:%M:%S %d/%m/%Y")}"
    elif not await check_for_user_existence(message.from_user.id):
        add_new_user_to_db(message)
    elif await check_user_for_blocking(message.from_user.id):
        return "Вы были заблокированы администратором. Если Вы считаете, что блокировка несправедлива, то пишите @username"
    elif not await check_time_for_sending(message):
        return "С отправки сообщения должно пройти 15 минут, подождите ещё"


async def check_for_user_existence(user_id) -> None:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    result = cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()
    con.close()
    # Return True if exist
    return True if result else False


async def check_user_for_blocking(user_id) -> None:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    result = cur.execute("SELECT is_blocked FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
    con.close()
    # Return True if blocked
    return True if result else False


# Checking for 15 minutes left since the last message
async def check_time_for_sending(message: Message) -> None:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    last_message_time = cur.execute("SELECT message_time FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT 1", (message.from_user.id,)).fetchone()[0]
    con.close()
    return True if message.date - last_message_time > 900 else False
