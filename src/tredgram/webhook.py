"""Main file with webhook."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.utils.i18n import ConstI18nMiddleware, I18n
from fastapi import FastAPI, Request
from tredgram.bot.routers import handlers
from tredgram.schemas import SuccessResponse, config

logger = logging.getLogger("virtual_assistant")
bot = Bot(token=config.bot.tg_token.get_secret_value())
dp = Dispatcher()

i18n = I18n(path="locales", default_locale="ru", domain="messages")

dp.include_router(handlers.router)
dp.update.middleware(
    ConstI18nMiddleware(locale="ru", i18n=i18n),  # Replace when add new languages
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await bot.set_webhook(config.bot.webhook_url.get_secret_value())
    logger.info("Webhook started with URL: %s", config.bot.webhook_url.get_secret_value())

    yield

    await bot.delete_webhook()
    await bot.session.close()


app = FastAPI(lifespan=lifespan)


@app.post("/")
async def webhook_handler(request: Request) -> SuccessResponse:
    update = Update.model_validate(await request.json())
    logger.info("New telegram request with data %s", update)

    await dp.feed_update(bot, update)
    return SuccessResponse()
