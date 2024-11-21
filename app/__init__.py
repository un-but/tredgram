from aiogram import Router

from . import admin_handlers, user_handlers

main_router = Router()

main_router.include_routers(
    admin_handlers.router,
    user_handlers.router,
)
