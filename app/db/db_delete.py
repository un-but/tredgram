import sqlite3
from aiogram.types import Message


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
