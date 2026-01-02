"""Main file with webhook."""

import asyncio
import logging
import logging.config

from aiogram import Bot, Dispatcher
from aiogram.utils.i18n import ConstI18nMiddleware, I18n
from tredgram.bot.routers import handlers
from tredgram.schemas import config

logging.config.fileConfig("logconfig.ini")
logger = logging.getLogger("tredgram")


async def start_long_polling() -> None:
    bot = Bot(token=config.bot.tg_token.get_secret_value())
    dp = Dispatcher()

    i18n = I18n(path="locales", default_locale="ru", domain="messages")

    dp.include_router(handlers.router)
    dp.update.middleware(
        ConstI18nMiddleware(locale="ru", i18n=i18n),  # Replace when add new languages
    )

    logger.info("Polling has been started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_long_polling())
