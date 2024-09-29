from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

admin_panel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ℹ️ Информация о сообщении"), KeyboardButton(text="🚫 Запретить публикацию на время")],
        [KeyboardButton(text="👮 Управление блокировками"), KeyboardButton(text="☠ Удалить пользователя из БД")]
        ],
    input_field_placeholder="Выберите действие в меню",
    resize_keyboard=True,
    is_persistent=True
)

ban_or_unban_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Заблокировать", callback_data="ban"), InlineKeyboardButton(text="✅ Разблокировать", callback_data="unban")
        ]
    ]
)

delete_user_info_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да", callback_data="delete_user_info_agree"), InlineKeyboardButton(text="❌ Нет", callback_data="delete_user_info_disagree")]
    ]
)