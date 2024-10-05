from aiogram.fsm.state import StatesGroup, State

class MessageInfo(StatesGroup):
    next_step = State()

class ProhibitSending(StatesGroup):
    next_step = State()

class Ban_Or_Unban(StatesGroup):
    ban_value = State()

class DeleteUserInfo(StatesGroup):
    next_step = State()
