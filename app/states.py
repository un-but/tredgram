from aiogram.fsm.state import StatesGroup, State

class NextMessageHandler(StatesGroup):
    next_step = State()

class MessageInfo(StatesGroup):
    next_step = State()
    
class ProhibitSending(StatesGroup):
    next_step = State()

class BlockOrUnblock(StatesGroup):
    block_value = State()

class DeleteUserInfo(StatesGroup):
    next_step = State()