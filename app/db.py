import sqlite3
from aiogram.types import Message

def init_db():
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
                       is_banned INTEGER NOT NULL
                   )
                """) # Объединить имя и фамилию в одно значение name
    cur.execute("""
                   CREATE TABLE IF NOT EXISTS messages (
                       id INTEGER PRIMARY KEY,
                       message_id INTEGER NOT NULL,
                       user_id INTEGER NOT NULL,
                       message_time INTEGER NOT NULL
                   )
                """)
    cur.execute("""
                   CREATE TABLE IF NOT EXISTS settings (
                       id INTEGER PRIMARY KEY,
                       prohibit_sending_time INTEGER
                   )
                """)
    if not cur.execute("SELECT prohibit_sending_time FROM settings").fetchall():
        cur.execute("INSERT INTO settings (prohibit_sending_time) VALUES (0)")
    con.commit()
    con.close()


def add_new_user_to_db(message: Message):
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    values = (
        message.from_user.username,
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.last_name,
        message.from_user.language_code,
        0
    )
    cur.execute(
        "INSERT INTO users (username, user_id, first_name, last_name, language, is_banned) VALUES (?, ?, ?, ?, ?, ?)",
        values
    )
    con.commit()
    con.close()


# TODO bad comment
# Message_id is from the channel, not the chat with the user
def add_new_message_to_db(message: Message, message_id: int):
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    values = (message_id, message.from_user.id, message.date.timestamp())
    cur.execute("INSERT INTO messages (message_id, user_id, message_time) VALUES (?, ?, ?)", values)
    con.commit()
    con.close()
    

def check_for_user_existence(user_id) -> bool:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    is_exist = cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()
    con.close()
    return True if is_exist else False


def check_user_for_ban(user_id) -> bool:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    is_banned = cur.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
    con.close()
    return True if is_banned else False


# Checking for 15 minutes left since the last message
def check_time_for_sending(message: Message) -> bool:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    last_message_time = cur.execute("SELECT message_time FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT 1", (message.from_user.id,)).fetchone()[0]
    con.close()
    return True if message.date.timestamp() - last_message_time > 900 else False


def get_user_info_by_message_id(message: Message) -> tuple:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    user_id = cur.execute("SELECT user_id FROM messages WHERE message_id = ?", (message.text.split("/")[4],)).fetchone()[0]
    user_info = cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()[0]
    con.close()
    return user_info


def get_prohibit_sending_time() -> int:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    prohibit_sending_time = cur.execute("SELECT prohibit_sending_time FROM settings WHERE id = 1").fetchone()[0]
    con.close()
    return prohibit_sending_time


def set_prohibit_sending_time(value) -> None:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    cur.execute("UPDATE settings SET prohibit_sending_time = ?", (value,))
    con.commit()
    con.close()


# TODO возможно стоит написать set_is_banned_value
def set_is_banned_value(username_or_id: str, is_banned: int) -> None:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    if username_or_id.isdigit():
        cur.execute("UPDATE users SET is_banned = ? WHERE user_id = ?", (is_banned, username_or_id))
    else:
        cur.execute("UPDATE users SET is_banned = ? WHERE username = ?", (is_banned, username_or_id.replace("@", "")))
    con.commit()
    con.close()
    
    
def delete_user_info_from_db(message: Message):
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    if message.text.isdigit():
        user_id = int(message.text)
    else:
        user_id = cur.execute("SELECT user_id FROM users WHERE username = ?", (message.text.replace("@", ""),)).fetchone()[0]
    # TODO возможно стоит объединить эти две команды в одну
    cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    cur.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
    con.commit()
    con.close()
