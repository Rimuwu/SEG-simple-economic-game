import random
from global_modules.models.cells import CellType, Cells
from modules.json_database import just_db
from modules.generate import generate_code
from enum import Enum
from modules.baseclass import BaseClass
from global_modules.load_config import ALL_CONFIGS
from collections import Counter
from global_modules.logs import main_logger

cells: Cells = ALL_CONFIGS['cells']
cells_types = cells.types

class SessionStages(Enum):
    WaitWebConnect = "WaitWebConnect" # Ждём пока появится сайт для работы
    FreeUserConnect = "FreeUserConnect" # Подключаем пользователей
    CellSelect = "CellSelect" # Выбираем клетки
    Game = "Game" # Ход
    ChangeTurn = "ChangeTurn" # Смена хода
    End = "End" # Конец игры


class Session(BaseClass):

    __tablename__ = "sessions"
    __unique_id__ = "session_id"

    def __init__(self, session_id: str = ""): 
        self.session_id = session_id
        self.cells: list[str] = []
        self.map_size: dict = {"rows": 7, "cols": 7}
        self.map_pattern: str = "random"
        self.cell_counts: dict = {}
        self.stage: str = SessionStages.WaitWebConnect.value

    def start(self):
        if not self.session_id:
            self.session_id = generate_code(32, use_letters=True, use_numbers=True, use_uppercase=True)
        self.stage = SessionStages.WaitWebConnect.value

        self.save_to_base()
        self.reupdate()

        return self

    def update_stage(self, new_stage: SessionStages):
        if not isinstance(new_stage, SessionStages):
            raise ValueError("new_stage must be an instance of SessionStages Enum")

        self.stage = new_stage.value
        self.save_to_base()
        self.reupdate()
        return self

    def can_user_connect(self):
        return self.stage == SessionStages.FreeUserConnect.value

    def can_add_company(self):
        return self.stage == SessionStages.FreeUserConnect.value

    @property
    def companies(self):
        from game.company import Company

        return [Company(_id=c_id
                        ).reupdate() for c_id in just_db.find(
            "companies", session_id=self.session_id)
                        ]

    @property
    def users(self):
        from game.user import User

        return [User(_id=u_id
                     ).reupdate() for u_id in just_db.find(
            "users", session_id=self.session_id)
                     ]

    def get_cell_with_label(self, label: str, 
                            rows: int = 0,
                            cols: int = 0,
                            x_operation: int = 0,
                            y_operation: int = 0
                            ) -> list[int]:
        """
        label 
            - center, получить центральную клетку
            - random, получить случайную клетку
            - right-top, получить клетку в правом верхнем углу
            - left-top, получить клетку в левом верхнем углу
            - right-bottom, получить клетку в правом нижнем углу
            - left-bottom, получить клетку в левом нижнем углу

        x_operation 
            - смещение по X от найденной клетки
        y_operation
            - смещение по Y от найденной клетки
        """

        if label == "center":
            result_row = rows // 2
            result_col = cols // 2
        elif label == "random":
            result_row = random.randint(0, rows - 1)
            result_col = random.randint(0, cols - 1)
        elif label == "right-top":
            result_row = 0
            result_col = cols - 1
        elif label == "left-top":
            result_row = 0
            result_col = 0
        elif label == "right-bottom":
            result_row = rows - 1
            result_col = cols - 1
        elif label == "left-bottom":
            result_row = rows - 1
            result_col = 0
        else:
            result_row = rows
            result_col = cols

        # Применяем смещения
        result_row += y_operation
        result_col += x_operation

        # Проверяем границы
        result_row = max(0, min(result_row, rows - 1))
        result_col = max(0, min(result_col, cols - 1))

        return [result_row, result_col]

    def generate_cells(self):
        if self.cells:
            raise ValueError("Cells have already been generated for this session.")

        # Ограничения на размер карты
        for r in range(self.map_size["rows"]):
            for c in range(self.map_size["cols"]):
                self.cells.append('null')

        # Установка объектов со стандартной позицией
        for cell_key, cell_info in cells.types.items():
            cell_info: CellType

            for location in cell_info.locations:
                x, y = self.get_cell_with_label(
                    label=location.start_point,
                    rows=self.map_size["rows"],
                    cols=self.map_size["cols"],
                    x_operation=location.x,
                    y_operation=location.y
                )
                index = x * self.map_size["cols"] + y
                self.cells[index] = cell_key
 

        # Заполнение остальных клеток
        if self.map_pattern == "random":
            # Заполнение остальных клеток равномерно случайными типами
            types = list(
                key for key, value in cells.types.items() if value.pickable
            )
            null_indices = [i for i, cell in enumerate(self.cells) if cell == 'null']

            if null_indices and types:
                # Создаем равномерное распределение типов для null клеток
                types_cycle = (types * ((len(null_indices) // len(types)) + 1))[:len(null_indices)]
                random.shuffle(types_cycle)

                for i, index in enumerate(null_indices):
                    self.cells[index] = types_cycle[i]

        # Подсчёт каждого типа клетки
        self.cell_counts = dict(Counter(self.cells))
        main_logger.info(f"Cell counts: {self.cell_counts}")

        self.save_to_base()
        return self.cells



class SessionsManager():
    def __init__(self):
        self.sessions = {}

    def create_session(self, session_id: str = ""):
        session = Session(session_id=session_id).start()
        self.sessions[session.session_id] = session
        return session

    def get_session(self, session_id):
        return self.sessions.get(session_id)

    def remove_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]

session_manager = SessionsManager()