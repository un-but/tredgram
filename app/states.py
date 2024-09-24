from aiogram.fsm.state import StatesGroup, State

class NextMessageHandler(StatesGroup):
    next_step = State()
