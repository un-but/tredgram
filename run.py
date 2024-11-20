import asyncio
import logging

from aiogram import Bot, Dispatcher

from app import admin_handlers, user_handlers
from app.db.db_create import init_db
from constants import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main() -> None:
    await init_db(bot)
    dp.include_routers(admin_handlers.router, user_handlers.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Exit")
