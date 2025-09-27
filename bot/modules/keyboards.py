from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


cancel_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_ac")
        ]
    ]
)


# Клавиатура создания компании
create_company_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
           InlineKeyboardButton(text="🏢 Создать компанию", callback_data="create_company") 
        ],
        [
            InlineKeyboardButton(text="🤝 Присоединиться по коду", callback_data="join_company")
        ]
    ]
)

# Первый слой
# Главная клавиатура управления компанией
control_company_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🏦 Банк", callback_data="bank"),
            InlineKeyboardButton(text="📈 Биржа", callback_data="exchange"),
            InlineKeyboardButton(text="📋 Контракты", callback_data="contracts")
        ],
        [
            InlineKeyboardButton(text="", callback_data="factories")
        ],
        [
            InlineKeyboardButton(text="Улучшение клетки", callback_data="upgrader_cell")
        ],
        [
            InlineKeyboardButton(text="Профиль", callback_data="profile"),
            InlineKeyboardButton(text="🚚 Логистика", callback_data="logistics"),
            InlineKeyboardButton(text="🏙️ Города", callback_data="cities")
        ]
    ]
)

# Второй слой
# Клавиатура банка
bank_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Кредиты", callback_data="credits"),
        ],
        [
            InlineKeyboardButton(text="Вклады", callback_data="deposits")
        ],
        [
            InlineKeyboardButton(text="Налоги", callback_data="taxes")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_main")
        ]
    ]
)

# Клавиатура биржи
exchange_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Купить продукты на бирже", callback_data="market_buy")
        ],
        [
            InlineKeyboardButton(text="Выставить товар на биржу", callback_data="market_sell")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_main")
        ]
    ]
)

# Клавиатура контрактов
contracts_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Создать контракт", callback_data="create_contract")
        ],
        [
            InlineKeyboardButton(text="Предложения контрактов", callback_data="see_all_contracts")
        ],
        [
            InlineKeyboardButton(text="Выполнить мои контракты", callback_data="my_contracts")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_main")
        ]
    ]
)

# Клавиуатура управления заводами
factories_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Комплектация", callback_data="factory_equipment")
        ],
        [
            InlineKeyboardButton(text="Автоматическое производство", callback_data="factory_production")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_main")
        ]
    ]
)

# Клавиатура улучшения клетки
upgrade_cell_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Просмотр улучшений", callback_data="see_upgrades_cell")
        ],
        [
            InlineKeyboardButton(text="Улучшить", callback_data="upgrade_cell")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_main")
        ]
    ]
)

# Клавиатура профиля
profile_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Инвентарь", callback_data="my_inventory")
        ],
        [
            InlineKeyboardButton(text="О компании", callback_data="about_company"),
            InlineKeyboardButton(text="О этапе", callback_data="about_stage"),
            InlineKeyboardButton(text="О клетке", callback_data="about_cell")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_main")
        ]
    ]
)

# Клавиатура логистики
logistics_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад", callback_data="back_main")
        ]
    ]
)

# Клавиатура городов
cities_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Город А", callback_data="city_a"),
            InlineKeyboardButton(text="Город Б", callback_data="city_b")
        ],
        [
            InlineKeyboardButton(text="Город В", callback_data="city_c"),
            InlineKeyboardButton(text="Город Г", callback_data="city_d")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_main")
        ]
]
)

# Третий слой
# Клавиатура отмены действия
cancel_action_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Отменить", callback_data="cancel_action")
        ]
    ]
)