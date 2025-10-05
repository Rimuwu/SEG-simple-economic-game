from typing import Optional, Type, Union

from .models.radio_page import RadioTypeScene
from .models.page import Page
from .models.text_page import TextTypeScene
from .models.int_page import IntTypeScene
from .models.option_page import OptionTypeScene

page_type: dict[str, Union[Page, Type[Page]]] = {
    'text': TextTypeScene,
    'int': IntTypeScene,
    'radio': RadioTypeScene,
    'option': OptionTypeScene
}

def fast_page(page_type_str: Optional[str], 
              page_name: str) -> type[Page]:
    """ Быстрый доступ к типам страниц по строковому идентификатору """
    base_cls = page_type.get(page_type_str, Page)

    class Modified(base_cls): 
        __page_name__ = page_name

    return Modified