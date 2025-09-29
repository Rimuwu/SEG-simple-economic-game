from oms import Page
from aiogram.types import Message, CallbackQuery
from modules.utils import update_page, cell_into_xy, xy_into_cell
from modules.ws_client import get_sessions_free_cells, set_company_position
from oms.utils import callback_generator


class SelectCell(Page):
    
    __page_name__ = 'select-cell-page'
    
    row_width = 7
   
    async def buttons_worker(self):
        buttons_o = []
        
        for i in range(7):
            for y in range(7):
                cell_position = xy_into_cell(i, y)
                buttons_o.append(
                    {
                        'text': cell_position,
                        'callback_data': callback_generator(
                    self.scene.__scene_name__, 
                    'cell_select',
                    cell_position
                )
                    }
                )
        
        self.row_width = 7
        buttons = []
        scene_data = self.scene.get_data('scene')
        session_id = scene_data.get('session')
        free_cells = await get_sessions_free_cells(session_id=session_id)
        
        # Создаем множество свободных координат для быстрого поиска
        free_coords = set()
        if free_cells and "free_cells" in free_cells:
            for cell in free_cells["free_cells"]:
                free_coords.add((cell[0], cell[1]))
        
        for b in buttons_o:
            cell_text = b['text']
            x, y = cell_into_xy(cell_text)
            
            # Специальные ячейки (банк и города)
            if cell_text == "D4":
                buttons.append({
                    'text': '🏦',
                    'callback_data': "bank"
                })
            elif cell_text in ("B2", "F2", "B6", "F6"):
                buttons.append({
                    'text': '🏢',
                    'callback_data': "city"
                })
            # Проверяем, есть ли координаты в списке свободных
            elif (x, y) in free_coords:
                buttons.append({
                    'text': f"{cell_text}",
                    'callback_data': callback_generator(
                        self.scene.__scene_name__, 
                        'cell_select',
                        cell_text
                    )
                })
            else:
                # Занятая ячейка - крестик
                buttons.append({
                    'text': f"❌ {cell_text}",
                    'callback_data': "occupied"
                })
        
        return buttons
    
    @Page.on_callback('cell_select')
    async def my_callback_handler(self, callback: CallbackQuery, args: list):
        cell_name = args[0] if args else None
        x, y = cell_into_xy(cell_name)
        self.scene.update_page("wait-game-stage-page")
        await set_company_position(company_id=self.scene.get_data('company_id'), x=x, y=y)

