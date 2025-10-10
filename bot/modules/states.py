from aiogram.fsm.state import State, StatesGroup

class CreateGameStates(StatesGroup):
    waiting_for_session_id = State()


class StartGameStates(StatesGroup):
    waiting_for_session_id = State()


class DeleteSessionStates(StatesGroup):
    waiting_for_session_id = State()
    
class ConfirmLeaveStates(StatesGroup):
    waiting_for_confirmation = State()