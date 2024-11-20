import aiosqlite
from aiogram.types import Message, User


async def init_db(bot: User) -> None:
    async with aiosqlite.connect("users_data.db") as db:
        await db.execute("""
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
        await db.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY,
                        message_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        message_time INTEGER NOT NULL
                    )
                    """)
        await db.execute("""
                    CREATE TABLE IF NOT EXISTS globals (
                        id INTEGER PRIMARY KEY,
                        prohibit_sending_time INTEGER,
                        bot_id INTEGER,
                        bot_name TEXT,
                        bot_username TEXT
                    )
                    """)

        bot_info: User = await bot.get_me()
        async with db.execute("SELECT * FROM globals") as cur:
            if not await cur.fetchall():
                await db.execute(
                    "INSERT INTO globals (prohibit_sending_time, bot_id, bot_name, bot_username) VALUES (?, ?, ?, ?)",
                    (0, bot_info.id, bot_info.first_name, bot_info.username),
                )
        await db.commit()


async def add_new_user_to_db(message: Message) -> None:
    async with aiosqlite.connect("users_data.db") as db:
        values = (
            "@" + message.from_user.username,
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.last_name,
            message.from_user.language_code,
            0,
        )
        await db.execute(
            "INSERT INTO users (username, user_id, first_name, last_name, language, is_banned) VALUES (?, ?, ?, ?, ?, ?)",
            values,
        )
        await db.commit()


async def add_new_message_to_db(message: Message, channel_message_id: int) -> None:
    async with aiosqlite.connect("users_data.db") as db:
        values = (channel_message_id, message.from_user.id, message.date.timestamp())
        await db.execute("INSERT INTO messages (message_id, user_id, message_time) VALUES (?, ?, ?)", values)
        await db.commit()
