import sqlite3

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
    

def get_acceptable_time():
    con = sqlite3.connect("user_data.db")
    cur = con.cursor()
    cur.execute("SELECT acceptable_time FROM settings WHERE id = 1").fetchone()[0]
    con.close()
