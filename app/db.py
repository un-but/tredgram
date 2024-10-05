import sqlite3
from aiogram.types import Message


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


def add_new_message_to_db(message: Message, channel_message_id: int):
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    values = (channel_message_id, message.from_user.id, message.date.timestamp())
    cur.execute("INSERT INTO messages (message_id, user_id, message_time) VALUES (?, ?, ?)", values)
    con.commit()
    con.close()


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


def set_prohibit_sending_time(value) -> None:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    cur.execute("UPDATE globals SET prohibit_sending_time = ?", (value,))
    con.commit()
    con.close()


def set_is_banned_value(username_or_id: str, is_banned: int) -> True | False:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    # TODO переписать, чтобы в блоке try была ошибка
    try:
        if username_or_id.isdigit():
            cur.execute("SELECT * FROM users WHERE user_id = ?", (username_or_id,)).fetchall()[0] # error call
            cur.execute("UPDATE users SET is_banned = ? WHERE user_id = ?", (is_banned, username_or_id))
        else:
            cur.execute("SELECT * FROM users WHERE user_id = ?", (username_or_id.replace("@", ""),)).fetchall()[0] # error call
            cur.execute("UPDATE users SET is_banned = ? WHERE username = ?", (is_banned, username_or_id.replace("@", "")))
    except IndexError:
        return False
    else:
        return True
    finally:
        con.commit()
        con.close()


def delete_user_info_from_db(username_or_id: str) -> True | False:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    try:
        if username_or_id.isdigit():
            cur.execute("SELECT * FROM users WHERE user_id = ?", (username_or_id,)).fetchall()[0] # error call
            user_id = int(username_or_id)
        else:
            user_id = cur.execute("SELECT user_id FROM users WHERE username = ?", (username_or_id.replace("@", ""),)).fetchall()[0]
        cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        cur.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
    except IndexError:
        return False
    else:
        return True
    finally:
        con.commit()
        con.close()
