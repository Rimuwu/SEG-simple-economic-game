from oms import Page
from aiogram.types import Message, CallbackQuery
from modules.utils import update_page, cell_into_xy, xy_into_cell
from modules.ws_client import get_sessions_free_cells, set_company_position
from oms.utils import callback_generator


class SelectCell(Page):
    
    __page_name__ = 'select-cell-page'
    
    # Устанавливаем 7 кнопок в ряду
    row_width = 7
   
    async def buttons_worker(self):
        buttons = []
        
        for i in range(7):
            for y in range(7):
                cell_position = xy_into_cell(i, y)
                buttons.append(
                    {
                        'text': cell_position,
                        'callback_data': cell_position
                    }
                )
        
        self.row_width = 7
    
        scene_data = self.scene.get_data('scene')
        session_id = scene_data.get('session')
        free_cells = await get_sessions_free_cells(session_id=session_id)
        
        print(f"Free cells: {free_cells}")
        return buttons
        
        
       
    
