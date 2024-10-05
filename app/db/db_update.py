import sqlite3
from aiogram.types import Message


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
