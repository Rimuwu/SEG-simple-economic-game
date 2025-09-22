from aiogram.fsm.state import State, StatesGroup

class CreateGameStates(StatesGroup):
    waiting_for_session_id = State()


class CreateUserStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_session_id = State()


class CreateCompanyStates(StatesGroup):
    waiting_for_company_name = State()


class JoinCompanyStates(StatesGroup):
    waiting_for_secret_code = State()