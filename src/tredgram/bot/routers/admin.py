from datetime import datetime

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from app.db import db_delete, db_read, db_update
from app.keyboards import (
    admin_panel_keyboard,
    ban_or_unban_inline_keyboard,
    delete_user_info_keyboard,
)
from app.states import Ban_Or_Unban, DeleteUserInfo, MessageInfo, ProhibitSending
from constants import ADMINS_ID

router = Router()

is_admin = F.from_user.id.in_(ADMINS_ID)


@router.message(is_admin, CommandStart())
async def create_admin_panel(message: Message) -> None:
    await message.answer(
        "Братишка, я тебе админку принес💩🍽",
        reply_markup=admin_panel_keyboard,
    )


@router.message(is_admin & F.text == "ℹ️ Информация о сообщении")
async def info_button_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(MessageInfo.next_step)
    await message.answer(
        "Введите URL сообщения:",
    )


@router.message(MessageInfo.next_step)
async def send_info_about_user(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_info = await db_read.get_user_info_by_message_id(message)
    if user_info:
        await message.answer(
            (
                f"Ник - {user_info[1]!s}\n"
                f"ID - {user_info[2]}\n"
                f"Имя - {str(user_info[3]) + ' ' + str(user_info[4])}\n"
                f"Язык - {user_info[5]}\n"
                f"Блокировка - {user_info[6] == 1}"
            ).replace("None", ""),
        )
    else:
        await message.answer(
            "Вы ввели некорректный url, нажмите на нужную кнопку и повторите ввод.\n"
            "Чтобы получить id сообщения, вы должны открыть канал, нажать на сообщение, скопировать его id и отправить боту.",
        )


@router.message(is_admin & F.text == "🚫 Запретить публикацию на время")
async def prohibit_sending_button_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(ProhibitSending.next_step)
    await message.answer(
        'Введите время блокировки в формате "4s", где 4 это количество, а s это единица измерения времени (s - секунды, m - минуты, h - часы, d - дни):',
    )


@router.message(ProhibitSending.next_step)
async def prohibit_sending_for_minutes(message: Message, state: FSMContext) -> None:
    await state.clear()
    literals = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    seconds = message.text[:-1]
    literal = message.text[-1]
    if seconds.isdigit() and literal in literals:
        prohibit_sending_time = message.date.timestamp() + int(seconds) * literals[literal]
        await db_update.set_prohibit_sending_time(prohibit_sending_time)
        await message.answer(
            f"Запрет на отправку сообщений будет действовать до {datetime.fromtimestamp(prohibit_sending_time).strftime('%H:%M:%S %d.%m.%Y')}.",
        )
    else:
        await message.answer(
            "Вы ввели некорректное время, нажмите на кнопку еще раз и попробуйте заново.",
        )


@router.message(is_admin & F.text == "👮 Управление блокировками")
async def ban_control_button_handler(message: Message) -> None:
    await message.answer(
        "Выберите действие",
        reply_markup=ban_or_unban_inline_keyboard,
    )


@router.callback_query(F.data.in_({"ban", "unban"}))
async def ban_or_unban_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    ban_value = int(callback.data == "ban")
    await state.set_state(Ban_Or_Unban.ban_value)
    await state.update_data(ban_value=ban_value)
    await callback.message.edit_text(
        text="Введите ник или id пользователя:",
    )


@router.message(Ban_Or_Unban.ban_value)
async def ban_or_unban_user(message: Message, state: FSMContext) -> None:
    is_banned = (await state.get_data())["ban_value"]
    await state.clear()
    if await db_update.set_is_banned_value(message.text, is_banned):
        await message.answer(
            "Пользователь успешно заблокирован"
            if is_banned == 1
            else "Пользователь успешно разблокирован",
        )
    else:
        await message.answer(
            "Вы ввели неправильный ник или id пользователя, нажмите на кнопку еще раз и введите заново.",
        )


@router.message(is_admin & F.text == "☠ Удалить пользователя из БД")
async def delete_user_info_button_handler(message: Message) -> None:
    await message.answer(
        "Вы уверены?",
        reply_markup=delete_user_info_keyboard,
    )


@router.callback_query(F.data == "delete_user_info_disagree")
async def delete_user_info_disagree_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Удаление всей информации о пользователе отменено",
    )


@router.callback_query(F.data == "delete_user_info_agree")
async def delete_user_info_agree_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(DeleteUserInfo.next_step)
    await callback.message.edit_text(
        "Введите ник или id пользователя:",
    )


@router.message(DeleteUserInfo.next_step)
async def delete_user_info(message: Message, state: FSMContext) -> None:
    await state.clear()
    if await db_delete.delete_user_info_from_db(message.text):
        await message.answer(
            "Все сохраненные данные о пользователе удалены.",
        )
    else:
        await message.answer(
            "Вы ввели неправильный ник или id пользователя, нажмите на кнопку еще раз и введите заново.",
        )


@router.message(is_admin)
async def incorrect_message_handler(message: Message) -> None:
    await message.answer(
        "Вы отправили некорректное сообщение, выберите один из пунктов меню и следуйте дальнейшим указаниям",
    )
