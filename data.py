# --- Каталог ---
catalog = {
    "Камеры": {
        1: {"name": "Canon C70", "price": 6000, "desc": "Кинокамера 4K, Super35"},
        2: {"name": "Canon C80", "price": 8000, "desc": "Кинокамера с 6K сенсором"},
    },
    "Оптика": {
        3: {"name": "Laowa Ranger 17-50", "price": 4000, "desc": "Кино-зум"},
        4: {"name": "DZO Arles", "price": 15000, "desc": "Профессиональная оптика"},
    },
    "Звук": {
        5: {"name": "Rode NTG-2", "price": 500, "desc": "Микрофон"},
        6: {"name": "Hollyland Mars M1", "price": 2000, "desc": "Монитор-передатчик"},
        7: {"name": "Hollyland Solidcom 4S", "price": 4000, "desc": "Гарнитура"},
    },
    "Аксессуары": {
        8: {"name": "Tilta Nano Focus II", "price": 2300, "desc": "Follow Focus"},
        9: {"name": "Tilta Mirage", "price": 1000, "desc": "Матбокс"},
        10: {"name": "Площадка V-mount", "price": 1000, "desc": "Крепление батарей"},
        11: {"name": "Cine saddle", "price": 500, "desc": "Мягкая опора"},
        12: {"name": "V-mount 99", "price": 500, "desc": "Аккумулятор"},
        13: {"name": "Телега OnStage", "price": 1000, "desc": "Тележка"},
        14: {"name": "Грипня и железки", "price": 1000, "desc": "Железо"},
        15: {"name": "Штатив", "price": 3000, "desc": "Штатив"},
        16: {"name": "Сумка операторская", "price": 700, "desc": "Сумка"},
    },
    "Флешки / Аккумы": {
        17: {"name": "Флешки 256гб", "price": 500, "desc": "Карты памяти"},
        18: {"name": "BP-30a", "price": 500, "desc": "Аккумулятор"},
        19: {"name": "NP-F970", "price": 500, "desc": "Аккумулятор"},
    },
}

id_to_item = {iid: item for cat in catalog.values() for iid, item in cat.items()}

# --- Данные пользователей и заказы (память в рантайме) ---
carts: dict[int, dict[int, int]] = {}      # user_id -> {item_id: qty}
orders_data: dict[int, dict] = {}          # user_id -> {name, phone, step, rental_period, comment}
all_orders: list[dict] = []                # список всех заказов
