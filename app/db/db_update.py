from __future__ import annotations

import aiosqlite


async def set_prohibit_sending_time(value: float) -> None:
    async with aiosqlite.connect("users_data.db") as db:
        await db.execute("UPDATE globals SET prohibit_sending_time = ?", (value,))
        await db.commit()


async def set_is_banned_value(username_or_id: str, is_banned: int) -> True | False:
    async with aiosqlite.connect("users_data.db") as db:
        if username_or_id.isdigit():
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (username_or_id,)) as cur:
                if await cur.fetchall():
                    await db.execute("UPDATE users SET is_banned = ? WHERE user_id = ?", (is_banned, username_or_id))
                else:
                    return False
        else:
            async with db.execute("SELECT * FROM users WHERE username = ?", (username_or_id,)) as cur:
                if await cur.fetchall():
                    await db.execute("UPDATE users SET is_banned = ? WHERE username = ?", (is_banned, username_or_id))
                else:
                    return False
        await db.commit()
        return True
