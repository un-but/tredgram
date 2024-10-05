import asyncio
import sqlite3
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import User

from constants import TOKEN
from app import admin_handlers, user_handlers

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def init_db():
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
                """)
    cur.execute("""
                   CREATE TABLE IF NOT EXISTS messages (
                       id INTEGER PRIMARY KEY,
                       message_id INTEGER NOT NULL,
                       user_id INTEGER NOT NULL,
                       message_time INTEGER NOT NULL
                   )
                """)
    cur.execute("""
                   CREATE TABLE IF NOT EXISTS globals (
                       id INTEGER PRIMARY KEY,
                       prohibit_sending_time INTEGER,
                       bot_id INTEGER,
                       bot_name TEXT,
                       bot_username TEXT
                   )
                """)

    bot_info: User = await bot.get_me()
    if not cur.execute("SELECT * FROM globals").fetchall():
        cur.execute(
            "INSERT INTO globals (prohibit_sending_time, bot_id, bot_name, bot_username) VALUES (?, ?, ?, ?)",
            (0, bot_info.id, bot_info.first_name, bot_info.username)
        )
    con.commit()
    con.close()


async def main() -> None:
    await init_db()
    dp.include_routers(admin_handlers.router, user_handlers.router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
