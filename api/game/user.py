import asyncio
from global_modules.db.baseclass import BaseClass
from modules.json_database import just_db
from modules.websocket_manager import websocket_manager

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
            raise ValueError("Invalid or inactive session for user connection.")

        self.id = _id

        with_this_name = just_db.find_one("users", username=username, session_id=session_id)
        if with_this_name:
            raise ValueError(f"Username '{username}' is already taken in this session.")
        self.username = username

        self.session_id = session_id

        self.save_to_base()
        self.reupdate()

        asyncio.create_task(websocket_manager.broadcast({
            "type": "api-create_user",
            "data": {
                'session_id': self.session_id,
                'user': self.__dict__
            }
        }))
        return self

    def create_company(self, name: str):
        from game.company import Company
        from game.session import session_manager
        session = session_manager.get_session(self.session_id)

        if self.company_id != 0:
            raise ValueError("User is already in a company.")

        if not session: 
            raise ValueError("User is not in a valid session.")

        company = Company().create(name=name, 
                                   session_id=self.session_id)
        if not session.can_add_company():
            raise ValueError("Cannot add company at this stage.")

        self.company_id = company.id

        self.save_to_base()
        self.reupdate()
        return company

    def add_to_company(self, secret_code: int):
        from game.company import Company
        if self.company_id != 0:
            raise ValueError("User is already in a company.")

        company: Company = just_db.find_one("companies", 
                    to_class=Company, secret_code=secret_code)
        if not company: 
            raise ValueError("Company with this secret code not found.")

        if company.can_user_enter() is False:
            raise ValueError("Company is not accepting new users at the moment.")

        self.company_id = company.id
        self.save_to_base()
        self.reupdate()

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
            raise ValueError("User is not in a company.")

        old_company_id = self.company_id
        self.company_id = 0
        self.save_to_base()
        self.reupdate()

        company = Company(_id=old_company_id).reupdate()

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