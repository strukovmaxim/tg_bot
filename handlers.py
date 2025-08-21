from start import register_start_handlers
from orders import register_order_handlers
from admin import register_admin_handlers
from history import register_history_handlers

def register_handlers(dp):
    register_start_handlers(dp)     # ← важно, первым!
    register_order_handlers(dp)
    register_admin_handlers(dp)
    register_history_handlers(dp)
