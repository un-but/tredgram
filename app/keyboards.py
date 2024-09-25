from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

admin_panel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ℹ️ Информация о сообщении"), KeyboardButton(text="🚫 Запретить публикацию на время")],
        [KeyboardButton(text="👮 Заблокировать/Разблокировать"), KeyboardButton(text="☠ Удалить пользователя из БД")]
        ],
    input_field_placeholder="Выберите действие в меню",
    resize_keyboard=True,
    is_persistent=True
)

block_or_unblock_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Заблокировать", callback_data="block"), InlineKeyboardButton(text="✅ Разблокировать", callback_data="unblock")
        ]
    ]
)

delete_user_from_db_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да", callback_data="delete_agree"), InlineKeyboardButton(text="❌ Нет", callback_data="delete_disagree")]
    ]
)