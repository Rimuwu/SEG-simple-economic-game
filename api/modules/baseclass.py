from modules import websocket_manager
from modules.json_database import just_db

class BaseClass:
    """ Базовый класс для всех классов, которые будут сохраняться в JSONDatabase
    """
    __tablename__: str = "base"
    __unique_id__: str = "id"  # Поле, которое будет использоваться как уникальный идентификатор

    def load_from_base(self, data: dict):
        """ Загружает данные из словаря в атрибуты объекта.
        """
        if data is None: return None
        for key, value in data.items(): setattr(self, key, value)

    def save_to_base(self) -> dict:
        """ Сохраняет текущие атрибуты объекта в базу данных.
        """
        # Фильтруем данные, исключая атрибуты, начинающиеся с _
        data_to_save = {key: value for key, value in self.__dict__.items() if not key.startswith('_')}

        if just_db.find_one(self.__tablename__, 
                **{self.__unique_id__: 
                    self.__dict__[self.__unique_id__]}
                            ) is None:
            just_db.insert(self.__tablename__, data_to_save)
            return

        just_db.update(self.__tablename__, 
                {self.__unique_id__: 
                    self.__dict__[self.__unique_id__]},
                data_to_save
                       )

    def reupdate(self):
        """ Обновляет атрибуты объекта из базы данных.
        """
        self.load_from_base(
            just_db.find_one(self.__tablename__, 
                **{self.__unique_id__: 
                    self.__dict__[self.__unique_id__]}
                            )
        )
        return self

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.__dict__})>"

    def update(self, **kwargs):
        """ Обновляет атрибуты объекта из переданных ключевых словарей.
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save_to_base()
        self.reupdate()
        return self