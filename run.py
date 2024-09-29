import asyncio
import logging
import os

from aiogram import Bot, Dispatcher

from constants import TOKEN
from app import admin_handlers, user_handlers

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main() -> None:
    dp.include_routers(admin_handlers.router, user_handlers.router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
