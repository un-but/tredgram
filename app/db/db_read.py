import aiosqlite
from aiogram.types import Message


async def check_for_user_existence(user_id) -> bool:
    async with aiosqlite.connect("users_data.db") as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            return bool(await cur.fetchall())


async def check_user_for_ban(user_id) -> bool:
    async with aiosqlite.connect("users_data.db") as db:
        async with db.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)) as cur:
            return bool((await cur.fetchone())[0])


# Checking for 15 minutes left since the last message
async def check_time_for_sending(message: Message) -> bool:
    async with aiosqlite.connect("users_data.db") as db:
        async with db.execute(
            "SELECT message_time FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT 1", (message.from_user.id,)
        ) as cur:
            return message.date.timestamp() - (await cur.fetchone())[0] > 900


async def get_user_info_by_message_id(message: Message) -> tuple | None:
    async with aiosqlite.connect("users_data.db") as db:
        try:
            async with db.execute("SELECT user_id FROM messages WHERE message_id = ?", (message.text.split("/")[4],)) as cur:
                user_id = (await cur.fetchone())[0]
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
                user_info = (await cur.fetchall())[0]
        except IndexError:
            return None
        return user_info


async def get_prohibit_sending_time() -> int:
    async with aiosqlite.connect("users_data.db") as db:
        async with db.execute("SELECT prohibit_sending_time FROM globals WHERE id = 1") as cur:
            return (await cur.fetchone())[0]
