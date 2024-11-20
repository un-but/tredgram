from aiogram.fsm.state import State, StatesGroup


class MessageInfo(StatesGroup):
    next_step = State()

class ProhibitSending(StatesGroup):
    next_step = State()

class Ban_Or_Unban(StatesGroup):
    ban_value = State()

class DeleteUserInfo(StatesGroup):
    next_step = State()
