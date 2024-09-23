from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

admin_panel = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ℹ️ Информация о сообщении"),KeyboardButton(text="🚫 Запретить публикацию на время")],
        [KeyboardButton(text="👮 Заблокировать/Разблокировать"), KeyboardButton(text="☠ Удалить пользователя из БД")]
        ],
    input_field_placeholder="Выберите действие в меню",
    resize_keyboard=True,
    is_persistent=True
)

block_or_unblock = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Заблокировать", callback_data="block"),
            InlineKeyboardButton(text="✅ Разблокировать", callback_data="unblock")
        ]
    ]
)