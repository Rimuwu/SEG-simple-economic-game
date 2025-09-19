import random
from modules.json_database import db_sessions
from modules.generate import generate_code

class Session:
    _instances = {}  # Словарь для хранения экземпляров по session_id
    
    def __new__(cls, session_id: str = None):
        # Если session_id не передан, создаем новый
        if session_id is None:
            session_id = generate_code(32, use_letters=True, use_numbers=True, use_uppercase=True)
        
        # Если экземпляр для данного session_id уже существует, возвращаем его
        if session_id in cls._instances:
            return cls._instances[session_id]
        
        # Создаем новый экземпляр и сохраняем его
        instance = super(Session, cls).__new__(cls)
        cls._instances[session_id] = instance
        instance._initialized = False
        return instance
    
    def __init__(self, session_id: str = None):
        # Предотвращаем повторную инициализацию
        if self._initialized:
            return

        self._initialized = True

        if session_id is None:
            self.start()
        else:
            self.session_id = session_id
            self.load()


    @classmethod
    def get_instance(cls, session_id: str):
        """Получить экземпляр по session_id (если существует)"""
        return cls._instances.get(session_id)
    
    @classmethod
    def remove_instance(cls, session_id: str):
        """Удалить экземпляр из кэша"""
        if session_id in cls._instances:
            del cls._instances[session_id]

    @classmethod
    def get_all_instances(cls):
        """Получить все активные экземпляры"""
        return cls._instances.copy()


    def load(self):
        data = db_sessions.find_one('sessions', **{'session_id': self.session_id})
        if data is None:
            raise ValueError(f"Session with id {self.session_id} does not exist.")
        else:
            for key, value in data.items():
                setattr(self, key, value)

    def save_data(self):

        # Фильтруем данные, исключая атрибуты, начинающиеся с _
        data_to_save = {key: value for key, value in self.__dict__.items() if not key.startswith('_')}
        if db_sessions.find_one('sessions', session_id=self.session_id) is None:
            db_sessions.insert('sessions', data_to_save)
            return

        db_sessions.update('sessions', data_to_save, **{'session_id': self.session_id})

    def start(self):
        self.session_id = generate_code(32, use_letters=True, use_numbers=True, use_uppercase=True)
        self.save_data()