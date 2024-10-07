import aiosqlite


async def delete_user_info_from_db(username_or_id: str) -> True | False:
    async with aiosqlite.connect("users_data.db") as db:
        if username_or_id.isdigit():
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (username_or_id,)) as cur:
                if await cur.fetchall():
                    user_id = int(username_or_id)
                else:
                    return False
        else:
            async with db.execute("SELECT user_id FROM users WHERE username = ?", (username_or_id,)) as cur:
                if user_id := await cur.fetchone():
                    user_id = user_id[0]
                else:
                    return False
        await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        await db.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
        await db.commit()
        return True
