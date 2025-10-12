import asyncio
from global_modules.db.baseclass import BaseClass
from modules.json_database import just_db
from modules.websocket_manager import websocket_manager
from modules.validation import validate_username
from modules.logs import game_logger

class User(BaseClass):

    __tablename__ = "users"
    __unique_id__ = "id"
    __db_object__ = just_db

    def __init__(self, _id: int = 0):
        self.id: int = _id
        self.username: str = ""
        self.company_id: int = 0
        self.session_id: str = ""

    def create(self, _id: int, 
               username: str, 
               session_id: str):
        from game.session import session_manager
        session = session_manager.get_session(session_id)

        if not session or not session.can_user_connect():
            game_logger.warning(f"Попытка создания пользователя в неверной сессии ({session_id}) или на неверном этапе.")
            raise ValueError("Неверная сессия или регистрация запрещена на данном этапе.")

        self.id = _id

        with_this_name = just_db.find_one("users", 
                                          username=username, 
                                          session_id=session_id)
        if with_this_name:
            game_logger.warning(f"Попытка создать пользователя с занятым именем '{username}' в сессии {session_id}.")
            raise ValueError(f"Имя пользователя '{username}' уже занято в этой сессии.")

        username = validate_username(username)
        self.username = username

        self.session_id = session_id

        self.save_to_base()
        self.reupdate()

        game_logger.info(f"Создан новый пользователь: {self.username} ({self.id}) в сессии {self.session_id}.")

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-create_user",
            "data": {
                'session_id': self.session_id,
                'user': self.to_dict()
            }
        }))
        return self

    def create_company(self, name: str):
        from game.company import Company
        from game.session import session_manager
        session = session_manager.get_session(self.session_id)

        if self.company_id != 0:
            game_logger.warning(f"Пользователь {self.username} ({self.id}) уже в компании, но пытается создать новую.")
            raise ValueError("Пользователь уже находится в компании.")

        if not session: 
            game_logger.error(f"Пользователь {self.username} ({self.id}) не в действительной сессии при попытке создать компанию.")
            raise ValueError("Пользователь не в действительной сессии.")

        if not session.can_add_company():
            game_logger.warning(f"Пользователь {self.username} ({self.id}) не может создать компанию на данном этапе в сессии {self.session_id}.")
            raise ValueError("Невозможно добавить компанию на данном этапе.")

        company = Company().create(name=name, 
                                   session_id=self.session_id)

        self.company_id = company.id

        self.save_to_base()
        self.reupdate()
        game_logger.info(f"Пользователь {self.username} ({self.id}) создал компанию '{name}' ({company.id}) в сессии {self.session_id}.")
        return company

    def add_to_company(self, secret_code: int):
        from game.company import Company
        if self.company_id != 0:
            game_logger.warning(f"Пользователь {self.username} ({self.id}) уже в компании, но пытается войти в другую.")
            raise ValueError("Пользователь уже находится в компании.")

        company: Company = just_db.find_one("companies", 
                    to_class=Company, 
                    secret_code=secret_code) # type: ignore
        if not company: 
            game_logger.warning(f"Пользователь {self.username} ({self.id}) не смог найти компанию с кодом {secret_code}.")
            raise ValueError("Компания с этим секретным кодом не найдена.")

        if company.can_user_enter() is False:
            game_logger.warning(f"Компания '{company.name}' ({company.id}) закрыта для входа, но пользователь {self.username} ({self.id}) пытается войти.")
            raise ValueError("Компания в данный момент не принимает новых пользователей.")

        self.company_id = company.id
        self.save_to_base()
        self.reupdate()

        game_logger.info(f"Пользователь {self.username} ({self.id}) присоединился к компании '{company.name}' ({company.id}).")

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-user_added_to_company",
            "data": {
                "company_id": self.company_id,
                "user_id": self.id
            }
        }))
        return company

    def delete(self):
        just_db.delete(self.__tablename__, id=self.id)
        
        try:
            self.leave_from_company()
        except Exception: pass

        game_logger.info(f"Пользователь {self.username} ({self.id}) удален.")

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-user_deleted",
            "data": {
                "user_id": self.id
            }
        }))
        return True

    def leave_from_company(self):
        from game.company import Company
        if self.company_id == 0:
            game_logger.warning(f"Пользователь {self.username} ({self.id}) пытается покинуть компанию, не находясь в ней.")
            raise ValueError("Пользователь не находится в компании.")

        old_company_id = self.company_id
        self.company_id = 0
        self.save_to_base()
        self.reupdate()

        company = Company(_id=old_company_id).reupdate()
        game_logger.info(f"Пользователь {self.username} ({self.id}) покинул компанию {old_company_id}.")

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-user_left_company",
            "data": {
                "company_id": old_company_id,
                "user_id": self.id
            }
        }))

        if company and len(company.users) == 0:
            company.delete()

        return True

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "company_id": self.company_id,
            "session_id": self.session_id
        }