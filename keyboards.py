from aiogram.utils.keyboard import InlineKeyboardBuilder
from data import carts, id_to_item

def main_menu(user_id: int):
    cart = carts.get(user_id, {})
    items = sum(cart.values()) if cart else 0
    total = sum(id_to_item[iid]["price"] * qty for iid, qty in cart.items()) if cart else 0
    kb = InlineKeyboardBuilder()
    kb.button(text="📂 Категории", callback_data="menu_categories")
    kb.button(text=f"🛒 Корзина ({items}|{total}₽)", callback_data="show_cart")
    kb.button(text="📋 Мои заказы", callback_data="my_orders")
    kb.button(text="👤 Связь с админом", callback_data="contact_admin")
    kb.adjust(1)
    return kb.as_markup()
