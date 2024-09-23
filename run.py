import asyncio
import logging
import os

from aiogram import Bot, Dispatcher

from app.admin_handlers import router as admin_router
from app.user_handlers import router as user_router

token = os.getenv("TOKEN")
channel_id = int(os.getenv("CHANNEL_ID"))
admin_id = int(os.getenv("ADMIN_ID"))

bot = Bot(token=token)
dp = Dispatcher()


async def main() -> None:
    dp.include_routers(admin_router, user_router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")