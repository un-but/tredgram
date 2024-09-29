from datetime import datetime

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from constants import ADMINS_ID
from app.keyboards import *
from app.states import *
from app.db import *

router = Router()

is_admin = F.from_user.id.in_(ADMINS_ID)


@router.message(is_admin, CommandStart())
async def create_admin_panel(message: Message) -> None:
    await message.answer(
        "Братишка, я тебе админку принес💩🍽",
        reply_markup=admin_panel_keyboard
    )


@router.message(is_admin & F.text == "ℹ️ Информация о сообщении")
async def info_button_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(MessageInfo.next_step)
    await message.answer(
        "Введите URL сообщения:"
    )


@router.message(MessageInfo.next_step)
async def send_info_about_user(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_info = get_user_info_by_message_id(message)
    await message.answer((f"Ник - {"@" + str(user_info[1])}\n"
                          f"ID - {user_info[2]}\n"
                          f"Имя - {str(user_info[3]) + " " + str(user_info[4])}\n"
                          f"Язык - {user_info[5]}\n"
                          f"Блокировка - {True if user_info[6] == 1 else False}").replace("None", "")
    )


@router.message(is_admin & F.text == "🚫 Запретить публикацию на время")
async def prohibit_sending_button_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(ProhibitSending.next_step)
    await message.answer(
        "Введите время блокировки в минутах (0 для отмены; умножьте на 60/1440 для указания часов/дней):"
    )


@router.message(ProhibitSending.next_step)
async def prohibit_sending_for_minutes(message: Message, state: FSMContext) -> None:
    await state.clear()
    # Change acceptable_time value to actual time + chosen time (can be mathematical expression)
    prohibit_sending_time = message.date.timestamp() + eval(message.text) * 60
    set_prohibit_sending_time(prohibit_sending_time)
    await message.answer(
        f"Запрет на отправку сообщений будет действовать до {datetime.fromtimestamp(prohibit_sending_time).strftime("%H:%M:%S %d.%m.%Y")}"
    )


@router.message(is_admin & F.text == "👮 Управление блокировками")
async def ban_control_button_handler(message: Message) -> None:
    await message.answer(
        "Выберите действие",
        reply_markup=ban_or_unban_inline_keyboard
    )


@router.callback_query(F.data.in_({"ban", "unban"}))
async def bun_or_unban_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    ban_value = 1 if callback.data == "ban" else 0
    await state.set_state(Ban_Or_Unban.ban_value)
    await state.update_data(ban_value=ban_value)
    await callback.message.edit_text(
        text="Введите ник или id пользователя:"
    )


@router.message(Ban_Or_Unban.ban_value)
async def ban_or_unban_user(message: Message, state: FSMContext) -> None:
    is_banned = (await state.get_data())["ban_value"]
    await state.clear()
    set_is_banned_value(message.text, is_banned)
    await message.answer(
        "Пользователь успешно заблокирован" if is_banned == 1 else "Пользователь успешно разблокирован"
    )


@router.message(is_admin & F.text == "☠ Удалить пользователя из БД")
async def delete_user_info_button_handler(message: Message) -> None:
    await message.answer(
        "Вы уверены?",
        reply_markup=delete_user_info_keyboard
    )


@router.callback_query(F.data == "delete_user_info_disagree")
async def delete_user_info_agree_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Удаление всей информации о пользователе отменено"
    )


@router.callback_query(F.data == "delete_user_info_agree")
async def delete_user_info_agree_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(DeleteUserInfo.next_step)
    await callback.message.edit_text(
        "Введите ник или id пользователя:"
    )


@router.message(DeleteUserInfo.next_step)
async def delete_user_info(message: Message, state: FSMContext) -> None:
    await state.clear()
    delete_user_info_from_db(message)
    await message.answer(
        "Все сохраненные данные о пользователе удалены"
    )
