from orders import register_order_handlers
from admin import register_admin_handlers
from history import register_history_handlers
from start import register_start_handlers

def register_handlers(dp):
    # сначала бизнес-логика
    register_order_handlers(dp)
    register_admin_handlers(dp)
    register_history_handlers(dp)

    # и только потом fallback (/start и универсальный ответ)
    register_start_handlers(dp)
