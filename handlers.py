from catalog import register_catalog_handlers
from orders import register_order_handlers
from admin import register_admin_handlers
from history import register_history_handlers
from start import register_start_handlers

def register_handlers(dp):
    # 1) каталог/корзина/контакты
    register_catalog_handlers(dp)
    # 2) оформление заказа
    register_order_handlers(dp)
    # 3) админ
    register_admin_handlers(dp)
    # 4) история заказов
    register_history_handlers(dp)
    # 5) /start + fallback (в самом конце)
    register_start_handlers(dp)
