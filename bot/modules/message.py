from global_modules.db.baseclass import BaseClass
from modules.db import db

class Message(BaseClass):
    """ Пример орм класса для работы с сообщениями пользователей
    """

    __tablename__ = "messages"
    __unique_id__ = "id"
    __db_object__ = db

    def __init__(self, _id: int = 0):
        self.id: int = _id
        self.user_id: int = 0

    def create(self, _id: int, user_id: int):
        self.id = _id
        self.user_id = user_id

        self.save_to_base()
        self.reupdate()
        return self