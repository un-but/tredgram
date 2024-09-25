import os
import sqlite3
import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboards import *
from app.states import *
from app.db import *

router = Router()
    
admin_id = int(os.getenv("ADMIN_ID"))
is_admin = F.from_user.id == admin_id
acceptable_time = 0


@router.message(is_admin, Command("start"))
async def create_admin_panel(message: Message) -> None:
    await message.answer("Братишка, я тебе админку принес💩🍽", reply_markup=admin_panel_keyboard)


@router.message(is_admin & F.text == "ℹ️ Информация о сообщении")
async def message_info_button(message: Message, state: FSMContext) -> None:
    await state.set_state(MessageInfo.next_step)
    await message.answer("Введите URL сообщения:")


@router.message(MessageInfo.next_step)
async def send_info_about_user_by_id(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_info = get_user_info_by_message_id(message)
    await message.answer((f"Ник - {"@" + str(user_info[1])}\n"
                          f"ID - {user_info[2]}\n"
                          f"Имя - {str(user_info[3]) + " " + str(user_info[4])}\n"
                          f"Язык - {user_info[5]}\n"
                          f"Блокировка - {True if user_info[6] == 1 else False}").replace("None", "")
    )


@router.message(is_admin & F.text == "🚫 Запретить публикацию на время")
async def prohibit_sending_messages_button(message: Message, state: FSMContext) -> None:
    await state.set_state(ProhibitSending.next_step)
    await message.answer("Введите время блокировки в минутах (0 для отмены; умножьте на 60/1440 для указания часов/дней):")


@router.message(ProhibitSending.next_step)
async def block_sending_for_minutes(message: Message, state: FSMContext) -> None:
    await state.clear()
    global acceptable_time
    # Change acceptable_time value to actual time + chosen time (can be mathematical expression)
    set_acceptable_time(message.date + eval(message.text) * 60)
    await message.answer(f"Запрет на отправку сообщений будет действовать до {datetime.fromtimestamp(acceptable_time).strftime("%H:%M:%S %d/%m/%Y")}")


@router.message(is_admin & F.text == "👮 Заблокировать/Разблокировать")
async def block_or_unblock_button(message: Message) -> None:
    await message.answer("Выберите действие", reply_markup=block_or_unblock_keyboard)


@router.callback_query(F.data.in_({"block", "unblock"}))
async def callback_block_or_unblock_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(BlockOrUnblock.block_value)
    next_step = 1 if callback.data == "block" else 0
    await state.update_data(next_step=next_step)
    # [WARNING] Возможна ошибка, так как не указано какое сообщение редактировать и я не знаю как редактируется callback
    await callback.message.edit_text(text="Введите ник или id пользователя:")


@router.message(BlockOrUnblock.block_value)
async def block_or_unblock_user(message: Message, state: FSMContext) -> None:
    block_value = await state.get_data()["block_value"]
    await state.clear()
    set_block_value(message, block_value)
    await message.answer("Пользователь успешно заблокирован" if block_value == 1 else "Пользователь успешно разблокирован")


@router.message(is_admin & F.text == "☠ Удалить пользователя из БД")
async def delete_all_info_button(message: Message) -> None:
    markup = delete_user_from_db_keyboard
    await message.answer("Вы уверены?", reply_markup=markup)


@router.callback_query(F.data == "delete_disagree")
async def answer_delete_disagree(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Удаление всей информации о пользователе отменено")


@router.callback_query(F.data == "delete_agree")
async def get_id_for_deleting_info(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(DeleteUserInfo.next_step)
    await callback.message.edit_text("Введите ник или id пользователя:")


@router.message(DeleteUserInfo.next_step)
async def delete_all_info_about_user(message: Message, state: FSMContext) -> None:
    await state.clear()
    delete_user_info(message)
    message.answer("Все сохраненные данные о пользователе удалены")
