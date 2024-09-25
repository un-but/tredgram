import sqlite3
from aiogram.types import Message

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
    cur.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        id INTEGER PRIMARY KEY,
                        acceptable_time INTEGER
                    )
                """)
    set_acceptable_time(0)
    # cur.execute("INSERT INTO settings (acceptable_time) VALUES (0)")
    con.commit()
    con.close()


def add_new_user_to_db(message: Message):
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    values = (message.from_user.username, message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.language_code, 0)
    cur.execute("INSERT INTO users (username, user_id, first_name, last_name, language, is_blocked) VALUES (?, ?, ?, ?, ?, ?)", values)
    con.commit()
    con.close()


# Message_id is from the channel, not the chat with the user
def add_new_message_to_db(message: Message, message_id):
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    values = (message_id, message.from_user.id, message.date.timestamp())
    cur.execute("INSERT INTO messages (message_id, user_id, message_time) VALUES (?, ?, ?)", values)
    con.commit()
    con.close()
    

def get_acceptable_time():
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    acceptable_time = cur.execute("SELECT acceptable_time FROM settings WHERE id = 1").fetchone()[0]
    con.close()
    return acceptable_time


def set_acceptable_time(value):
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    cur.execute("INSERT INTO settings (acceptable_time) VALUES (?)", (value,))
    con.commit()
    con.close()
    
def check_for_user_existence(user_id) -> None:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    result = cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()
    con.close()
    # Return True if exist
    return True if result else False


def check_user_for_blocking(user_id) -> None:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    result = cur.execute("SELECT is_blocked FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
    con.close()
    # Return True if blocked
    return True if result else False


# Checking for 15 minutes left since the last message
def check_time_for_sending(message: Message) -> None:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    last_message_time = cur.execute("SELECT message_time FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT 1", (message.from_user.id,)).fetchone()[0]
    con.close()
    return True if message.date.timestamp() - last_message_time > 900 else False


def get_user_info_by_message_id(message: Message) -> tuple:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    user_id = cur.execute("SELECT user_id FROM messages WHERE message_id = ?", (message.text.split("/")[5],)).fetchone()[0]
    result = cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()[0]
    con.close()
    return result

def set_block_value(message: Message, is_for_block: int) -> None:
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    if message.text.isdigit():
        cur.execute("UPDATE users SET is_blocked = ? WHERE user_id = ?", (is_for_block, message.text))
    else:
        cur.execute("UPDATE users SET is_blocked = ? WHERE username = ?", (is_for_block, message.text.replace("@", "")))
    con.commit()
    con.close()
    
def delete_user_info(message: Message):
    con = sqlite3.connect("users_data.db")
    cur = con.cursor()
    if message.text.isdigit():
        user_id = int(message.text)
    else:
        user_id = cur.execute("SELECT user_id FROM users WHERE username = ?", (message.text.replace("@", ""),)).fetchone()[0]
    cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    cur.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
    con.commit()
    con.close()
