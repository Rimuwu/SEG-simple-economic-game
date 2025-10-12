from oms import Page
from aiogram.types import Message
from modules.ws_client import get_session_event, get_session
from global_modules.load_config import ALL_CONFIGS, Events


EVENTS: Events = ALL_CONFIGS["events"]


class AboutTurnPage(Page):
    __page_name__ = "about-turn-page"
    
    async def content_worker(self):
        data = self.scene.get_data("scene")
        session_id = data.get("session")
        session = await get_session(session_id)
        step = session.get("step")
        max_steps = session.get("max_steps")
        event = await get_session_event(session_id)
        if event["event"] is not None:
            data_event = EVENTS.get(event["event"])
            name_event = data_event.get("name")
            decs_event = data_event.get("description")
            duration_data = data_event.get("duration")
            min_duration_event = duration_event.get("min")
            max_duration_event = duration_event.get("max")
            duration_event = max_duration_event - min_duration_event + 1
            return f"{name_event}\n" +\
                    f"{decs_event}\n" +\
                    f"{duration_event}\n" +\
                    f"{min_duration_event}\n" +\
                    f"{max_duration_event}\n" +\
                    f"{step}\n" +\
                    f"{max_steps}\n"
            