from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def get_admin_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="ℹ️ Информация о сообщении"),
                KeyboardButton(text="🚫 Запретить публикацию на время"),
            ],
            [
                KeyboardButton(text="👮 Управление блокировками"),
                KeyboardButton(text="☠ Удалить пользователя из БД"),
            ],
        ],
        input_field_placeholder="Выберите действие в меню",
        resize_keyboard=True,
        is_persistent=True,
    )


def get_ban_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ Заблокировать", callback_data="ban"),
                InlineKeyboardButton(text="✅ Разблокировать", callback_data="unban"),
            ],
        ],
    )


def get_user_delete_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data="delete_user_info_agree"),
                InlineKeyboardButton(text="❌ Нет", callback_data="delete_user_info_disagree"),
            ],
        ],
    )
