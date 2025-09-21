from typing import Optional
from global_modules.db.json_database import JSONDatabase

class BaseClass:
    """ Базовый класс для всех классов, которые будут сохраняться в JSONDatabase
    """
    __tablename__: str = "base" # Имя таблицы в базе данных
    __unique_id__: str = "id"  # Поле, которое будет использоваться как уникальный идентификатор
    __db_object__: JSONDatabase  # Экземпляр JSONDatabase, должен быть установлен в подклассе

    def load_from_base(self, data: Optional[dict]):
        """ Загружает данные из словаря в атрибуты объекта.
        """
        if data is None: return None
        for key, value in data.items(): setattr(self, key, value)

    def save_to_base(self):
        """ Сохраняет текущие атрибуты объекта в базу данных.
        """
        # Фильтруем данные, исключая атрибуты, начинающиеся с _
        data_to_save = {key: value for key, value in self.__dict__.items() if not key.startswith('_')}

        if self.__db_object__.find_one(self.__tablename__, 
                **{self.__unique_id__: 
                    self.__dict__[self.__unique_id__]}
                            ) is None:
            self.__db_object__.insert(self.__tablename__, data_to_save)
            return

        self.__db_object__.update(self.__tablename__, 
                {self.__unique_id__: 
                    self.__dict__[self.__unique_id__]},
                data_to_save
                       )

    def reupdate(self):
        """ Обновляет атрибуты объекта из базы данных.
        """
        self.load_from_base(
            self.__db_object__.find_one(self.__tablename__, 
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