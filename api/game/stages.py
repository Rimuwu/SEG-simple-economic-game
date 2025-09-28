from modules.sheduler import scheduler
from datetime import datetime, timedelta
from global_modules.load_config import ALL_CONFIGS, Settings


settings: Settings = ALL_CONFIGS['settings']

GAME_TIME = settings.time_on_game_stage * 60
CHANGETURN_TIME = settings.time_on_change_stage * 60

async def stage_game_updater(session_id: str):
    """ Фнукция для цикличного обновления стадии игры
    """
    from game.session import SessionStages, session_manager
    session = session_manager.get_session(session_id)

    if not session: return 0
    if session.stage == SessionStages.CellSelect.value or session.stage == SessionStages.ChangeTurn.value:
        session.update_stage(SessionStages.Game)
        scheduler.schedule_task(
            stage_game_updater, 
            datetime.now() + timedelta(seconds=GAME_TIME),
            kwargs={"session_id": session_id}
        )

    elif session.stage == SessionStages.Game.value:
        if session.step >= session.max_steps:
            session.update_stage(SessionStages.End)
            return 0

        session.update_stage(SessionStages.ChangeTurn)
        scheduler.schedule_task(
            stage_game_updater, 
            datetime.now() + timedelta(seconds=CHANGETURN_TIME),
            kwargs={"session_id": session_id}
        )

async def leave_from_prison(session_id: str, company_id: int):
    """ Фнукция для выхода из тюрьмы по времени
    """
    from game.company import Company
    from game.session import session_manager

    session = session_manager.get_session(session_id)
    if not session: return 0

    company = Company(company_id).reupdate()
    if not company: return 0

    company.leave_prison()
    return 1
