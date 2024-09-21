import sqlite3
from datetime import datetime
import os

import telebot
from telebot import types


token = os.getenv("TOKEN")
channel_id = int(os.getenv("CHANNEL_ID"))
admin_id = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(token)

allowed_types = ["text", "photo", "video", "audio", "voice", "sticker", "animation", "video_note", "poll"]
prohibited_types = ["document", "invoice", "dice", "location", "venue", "contact"]

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

# Designed to store the time of the ban on sending messages
acceptable_time = 0


@bot.message_handler(commands=["start"])
def welcome(message):
    if message.from_user.id == admin_id:
        create_admin_panel(message)
    else:
        start_message = bot.send_message(message.chat.id, welcome_message, parse_mode="Markdown")
        bot.pin_chat_message(message.chat.id, start_message.message_id)


# ================= Admin Functions =================
# Here are functions that handle admin messages.
def create_admin_panel(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("ℹ️ Информация о сообщении"), types.KeyboardButton("🚫 Запретить публикацию на время"))
    markup.row(types.KeyboardButton("👮 Заблокировать/Разблокировать"), types.KeyboardButton("☠ Удалить пользователя из БД"))
    bot.send_message(message.chat.id, "Братишка, я тебе админку принес💩🍽", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "ℹ️ Информация о сообщении")
def message_info_button(message):
    msg = bot.send_message(message.chat.id, "Введите URL сообщения:")
    bot.register_next_step_handler(msg, get_info_about_user_by_id)

def get_info_about_user_by_id(message):
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    # Getting message_id from url
    user_id = cur.execute("SELECT user_id FROM messages WHERE message_id = ?", (message.text.split("/")[5],)).fetchone()[0]
    result = cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()[0]
    con.commit()
    con.close()
    bot.send_message(message.chat.id, (f"Ник - {"@" + str(result[1])}\n"
                                       f"ID - {result[2]}\n"
                                       f"Имя - {str(result[3]) + " " + str(result[4])}\n"
                                       f"Язык - {result[5]}\n"
                                       f"Блокировка - {True if result[6] == 1 else False}").replace("None", ""))

@bot.message_handler(func=lambda message: message.text == "🚫 Запретить публикацию на время")
def prohibit_sending_messages_button(message):
    msg = bot.send_message(message.chat.id, "Введите время блокировки в минутах (0 для отмены; умножьте на 60/1440 для указания часов/дней):")
    bot.register_next_step_handler(msg, block_sending_for_minutes)

def block_sending_for_minutes(message):
    global acceptable_time
    # Change acceptable_time value to actual time + chosen time (can be mathematical expression)
    acceptable_time = message.date + eval(message.text) * 60
    bot.send_message(message.chat.id, f"Запрет на отправку сообщений будет действовать до {datetime.fromtimestamp(acceptable_time).strftime("%H:%M:%S %d/%m/%Y")}")

@bot.message_handler(func=lambda message: message.text == "👮 Заблокировать/Разблокировать")
def block_or_unblock_button(message):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("❌ Заблокировать", callback_data="block"), types.InlineKeyboardButton("✅ Разблокировать", callback_data="unblock"))
    bot.send_message(message.chat.id, "Выберите действие", reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: callback.data in ["block", "unblock"])
def callback_block_or_unblock_handler(callback):
    msg = bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text="Введите ник или id пользователя:")
    bot.register_next_step_handler(msg, lambda msg: block_or_unblock_user(msg, 1 if callback.data == "block" else 0))

def block_or_unblock_user(message, is_blocked):
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    if message.text.isdigit():
        cur.execute("UPDATE users SET is_blocked = ? WHERE user_id = ?", (is_blocked, message.text))
    else:
        cur.execute("UPDATE users SET is_blocked = ? WHERE username = ?", (is_blocked, message.text.replace("@", "")))
    con.commit()
    con.close()
    notification = "Пользователь успешно заблокирован" if is_blocked == 1 else "Пользователь успешно разблокирован"
    bot.send_message(message.chat.id, notification)

@bot.message_handler(func=lambda message: message.text == "☠ Удалить пользователя из БД")
def delete_all_info_button(message):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("✅ Да", callback_data="delete_agree"), types.InlineKeyboardButton("❌ Нет", callback_data="delete_disagree"))
    bot.send_message(message.chat.id, "Вы уверены", reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: callback.data == "delete_disagree")
def answer_delete_disagree(callback):
    bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text="Удаление всей информации о пользователе отменено")

@bot.callback_query_handler(func=lambda callback: callback.data == "delete_agree")
def get_id_for_deleting_info(callback):
    msg = bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text="Введите ник или id пользователя:")
    bot.register_next_step_handler(msg, delete_all_info_about_user)

def delete_all_info_about_user(message):
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


# ================= User Functions =================
# Here are functions that handle user messages.
@bot.message_handler(content_types=prohibited_types)
def prohibited_messages_handler(message):
    bot.send_message(message.chat.id, "Отправка сообщений этого типа запрещена")

@bot.message_handler(content_types=allowed_types)
def allowed_messages_handler(message):
    create_db()
    result = check_message(message)
    if result:
        bot.send_message(message.chat.id, result)
    else:
        channel_message = bot.copy_message(channel_id, message.chat.id, message.message_id)
        add_new_message_to_db(message, channel_message.message_id)
        bot.send_message(message.chat.id, "Ваше сообщение успешно отправлено")

def check_message(message):
    if message.date < acceptable_time:
        return f"Администратор заблокировал отправку сообщений до {datetime.fromtimestamp(acceptable_time).strftime("%H:%M:%S %d/%m/%Y")}"
    elif not check_for_user_existence(message.from_user.id):
        add_new_user_to_db(message)
    elif check_user_for_blocking(message.from_user.id):
        return "Вы были заблокированы администратором. Если Вы считаете, что блокировка несправедлива, то пишите @username"
    elif not check_time_for_sending(message):
        return "С отправки сообщения должно пройти 15 минут, подождите ещё"

def check_for_user_existence(user_id):
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    result = cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()
    con.close()
    # Return True if exist
    return True if result else False

def check_user_for_blocking(user_id):
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    result = cur.execute("SELECT is_blocked FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
    con.close()
    # Return True if blocked
    return True if result == 1 else False

# Checking for 15 minutes left since the last message
def check_time_for_sending(message):
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    last_message_time = cur.execute("SELECT message_time FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT 1", (message.from_user.id,)).fetchone()[0]
    con.close()
    return True if message.date - last_message_time > 900 else False


# ================= Secondary Functions =================
# Here are the secondary functions used in the main code.
def create_db():
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    cur.execute("""
                   CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    user_id INTEGER NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    language TEXT,
                    is_blocked INTEGER NOT NULL
                   )""")
    cur.execute("""
                   CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY,
                    message_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    message_time INTEGER NOT NULL
                   )""")
    con.commit()
    con.close()

def add_new_user_to_db(message):
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    values = (message.from_user.username, message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.language_code, 0)
    cur.execute("INSERT INTO users (username, user_id, first_name, last_name, language, is_blocked) VALUES (?, ?, ?, ?, ?, ?)", values)
    con.commit()
    con.close()

# Message_id is from the channel, not the chat with the user
def add_new_message_to_db(message, message_id):
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    values = (message_id, message.from_user.id, message.date)
    cur.execute("INSERT INTO messages (message_id, user_id, message_time) VALUES (?, ?, ?)", values)
    con.commit()
    con.close()


# Start bot
if __name__ == "__main__":
    bot.infinity_polling(none_stop=True)
