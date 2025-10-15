import asyncio
from global_modules.db.baseclass import BaseClass
from modules.db import just_db
from modules.websocket_manager import websocket_manager
from modules.validation import validate_username

class User(BaseClass):

    __tablename__ = "users"
    __unique_id__ = "id"
    __db_object__ = just_db

    def __init__(self, _id: int = 0):
        self.id: int = _id
        self.username: str = ""
        self.company_id: int = 0
        self.session_id: str = ""

    async def create(self, _id: int, 
               username: str, 
               session_id: str):
        from game.session import session_manager
        session = session_manager.get_session(session_id)

        if not session or not await session.can_user_connect():
            raise ValueError("Неверная сессия или регистрация запрещена на данном этапе.")

        self.id = _id

        with_this_name = await just_db.find_one("users", 
                                          username=username, 
                                          session_id=session_id)
        if with_this_name:
            raise ValueError(f"Имя пользователя '{username}' уже занято в этой сессии.")

        username = validate_username(username)
        self.username = username

        self.session_id = session_id

        await self.insert()

        await websocket_manager.broadcast({
            "type": "api-create_user",
            "data": {
                'session_id': self.session_id,
                'user': self.to_dict()
            }
        })
        return self

    async def create_company(self, name: str):
        from game.company import Company
        from game.session import session_manager
        session = await session_manager.get_session(self.session_id)

        if self.company_id != 0:
            raise ValueError("Пользователь уже находится в компании.")

        if not session: 
            raise ValueError("Пользователь не в действительной сессии.")

        company = await Company().create(name=name, 
                                   session_id=self.session_id
                                   )
        if not await session.can_add_company():
            raise ValueError("Невозможно добавить компанию на данном этапе.")

        self.company_id = company.id

        await self.save_to_base()
        return company

    async def add_to_company(self, secret_code: int):
        from game.company import Company
        if self.company_id != 0:
            raise ValueError("Пользователь уже находится в компании.")

        company: Company = just_db.find_one("companies", 
                    to_class=Company, 
                    secret_code=secret_code) # type: ignore
        if not company: 
            raise ValueError("Компания с этим секретным кодом не найдена.")

        if await company.can_user_enter() is False:
            raise ValueError("Компания в данный момент не принимает новых пользователей.")

        self.company_id = company.id
        await self.save_to_base()

        await websocket_manager.broadcast({
            "type": "api-user_added_to_company",
            "data": {
                "company_id": self.company_id,
                "user_id": self.id
            }
        })
        return company

    async def delete(self):
        await just_db.delete(self.__tablename__, id=self.id)

        try:
            await self.leave_from_company()
        except Exception: pass

        await websocket_manager.broadcast({
            "type": "api-user_deleted",
            "data": {
                "user_id": self.id
            }
        })
        return True

    async def leave_from_company(self):
        from game.company import Company
        if self.company_id == 0:
            raise ValueError("Пользователь не находится в компании.")

        old_company_id = self.company_id
        self.company_id = 0
        await self.save_to_base()

        company = Company(_id=old_company_id).reupdate()

        await websocket_manager.broadcast({
            "type": "api-user_left_company",
            "data": {
                "company_id": old_company_id,
                "user_id": self.id
            }
        })

        if company and len(await company.users) == 0:
            await company.delete()

        return True

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "company_id": self.company_id,
            "session_id": self.session_id
        }