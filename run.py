import asyncio
import logging

from aiogram import Bot, Dispatcher

from app import main_router
from app.db.db_create import init_db
from constants import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main() -> None:
    await init_db(bot)
    dp.include_router(main_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Exit")
