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
                    'cell_select')
                    }
                )
        
        self.row_width = 7
        buttons = []
        scene_data = self.scene.get_data('scene')
        session_id = scene_data.get('session')
        free_cells = await get_sessions_free_cells(session_id=session_id)
        for b in buttons_o:
            x, y = cell_into_xy(b['text'])
            for c in free_cells:
                if b["text"] == "D4":
                    buttons.append({
                        'text': '🏦',
                        'callback_data': "bank"
                    })
                if b["text"] in ("B2", "F2", "B6", "F6"):
                    buttons.append({
                        'text': '🏢',
                        'callback_data': "city"
                    })
                if c[0] == x and c[1] == y:
                    buttons.append(b)
                else:
                    buttons.append({
                        'text': '❌',
                        'callback_data': "no"
                    })
        
        return buttons
    
    @Page.on_callback('cell_select')
    async def my_callback_handler(self, callback: CallbackQuery, args: list):
        cell = callback.data
        company_id = self.scene.get_data('company_id')
        x, y = cell_into_xy(cell)
        response = await set_company_position(company_id=company_id, x=x, y=y)
        print(response)
    
        
        
       
    
