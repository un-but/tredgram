import os
import sqlite3
import datetime

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards import admin_panel_keyboard, block_or_unblock_keyboard
from states import NextMessageHandler

router = Router()
    
admin_id = int(os.getenv("ADMIN_ID"))
is_admin = F.from_user.id == admin_id
acceptable_time = 0


@router.message(is_admin & CommandStart())
async def create_admin_panel(message: Message) -> None:
    message.answer("Братишка, я тебе админку принес💩🍽", reply_markup=admin_panel_keyboard)


@router.message(is_admin & F.text == "ℹ️ Информация о сообщении")
async def message_info_button(message: Message, state: FSMContext) -> None:
    await state.set_state(NextMessageHandler.next_step)
    await message.answer("Введите URL сообщения:")


@router.message(NextMessageHandler.next_step)
async def send_info_about_user_by_id(message: Message) -> None:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    # Getting message_id from url
    user_id = cur.execute("SELECT user_id FROM messages WHERE message_id = ?", (message.text.split("/")[5],)).fetchone()[0]
    result = cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()[0]
    con.commit()
    con.close()
    await message.answer((f"Ник - {"@" + str(result[1])}\n"
                          f"ID - {result[2]}\n"
                          f"Имя - {str(result[3]) + " " + str(result[4])}\n"
                          f"Язык - {result[5]}\n"
                          f"Блокировка - {True if result[6] == 1 else False}").replace("None", "")
    )


@router.message(is_admin & F.text == "🚫 Запретить публикацию на время")
async def prohibit_sending_messages_button(message: Message, state: FSMContext) -> None:
    await state.set_state(NextMessageHandler.next_step)
    await message.answer("Введите время блокировки в минутах (0 для отмены; умножьте на 60/1440 для указания часов/дней):")


@router.message(NextMessageHandler.next_step)
async def block_sending_for_minutes(message: Message) -> None:
    global acceptable_time
    # Change acceptable_time value to actual time + chosen time (can be mathematical expression)
    acceptable_time = message.date + eval(message.text) * 60
    await message.answer(f"Запрет на отправку сообщений будет действовать до {datetime.fromtimestamp(acceptable_time).strftime("%H:%M:%S %d/%m/%Y")}")


@router.message(is_admin & F.text == "👮 Заблокировать/Разблокировать")
async def block_or_unblock_button(message: Message) -> None:
    await message.answer("Выберите действие", reply_markup=block_or_unblock_keyboard)


@router.callback_query(F.data.in_({"block", "unblock"}))
async def callback_block_or_unblock_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(NextMessageHandler.next_step)
    next_step = True if callback.data == "block" else False
    await state.update_data(next_step=next_step)
    # [WARNING] Возможна ошибка, так как не указано какое сообщение редактировать и я не знаю как редактируется callback
    await callback.message.edit_text(text="Введите ник или id пользователя:")


@router.message(NextMessageHandler.next_step)
async def block_or_unblock_user(message: Message, state: FSMContext) -> None:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    is_for_block = state.get_data()["next_step"]
    if message.text.isdigit():
        cur.execute("UPDATE users SET is_blocked = ? WHERE user_id = ?", (is_for_block, message.text))
    else:
        cur.execute("UPDATE users SET is_blocked = ? WHERE username = ?", (is_for_block, message.text.replace("@", "")))
    con.commit()
    con.close()
    message.answer("Пользователь успешно заблокирован" if is_for_block == 1 else "Пользователь успешно разблокирован")


@bot.message_handler(func=lambda message: message.text == "☠ Удалить пользователя из БД")
async def delete_all_info_button(message) -> None:
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("✅ Да", callback_data="delete_agree"), types.InlineKeyboardButton("❌ Нет", callback_data="delete_disagree"))
    bot.send_message(message.chat.id, "Вы уверены", reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: callback.data == "delete_disagree")
async def answer_delete_disagree(callback) -> None:
    bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text="Удаление всей информации о пользователе отменено")


@bot.callback_query_handler(func=lambda callback: callback.data == "delete_agree")
async def get_id_for_deleting_info(callback) -> None:
    msg = bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text="Введите ник или id пользователя:")
    bot.register_next_step_handler(msg, delete_all_info_about_user)


async def delete_all_info_about_user(message) -> None:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    if message.text.isdigit():
        user_id = message.text
    else:
        user_id = cur.execute("SELECT user_id FROM users WHERE username = ?", (message.text.replace("@", ""),)).fetchone()[0]
    cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    cur.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
    con.commit()
    con.close()
    bot.send_message(message.chat.id, "Все сохраненные данные о пользователе удалены")
