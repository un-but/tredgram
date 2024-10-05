import sqlite3
from aiogram.types import Message


def check_for_user_existence(user_id) -> bool:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    is_exist = cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()
    con.close()
    return bool(is_exist)


def check_user_for_ban(user_id) -> bool:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    is_banned = cur.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
    con.close()
    return bool(is_banned)


# Checking for 15 minutes left since the last message
def check_time_for_sending(message: Message) -> bool:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    last_message_time = cur.execute(
        "SELECT message_time FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT 1", (message.from_user.id,)
    ).fetchone()[0]
    con.close()
    return message.date.timestamp() - last_message_time > 900


def get_user_info_by_message_id(message: Message) -> tuple | None:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    try:
        user_id = cur.execute("SELECT user_id FROM messages WHERE message_id = ?", (message.text.split("/")[4],)).fetchone()[0]
        user_info = cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()[0]
    except IndexError:
        return None
    else:
        return user_info
    finally:
        con.close()


def get_prohibit_sending_time() -> int:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    prohibit_sending_time = cur.execute("SELECT prohibit_sending_time FROM globals WHERE id = 1").fetchone()[0]
    con.close()
    return prohibit_sending_time
