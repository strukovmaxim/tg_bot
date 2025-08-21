# catalog.py
from aiogram import types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards import main_menu
from data import catalog, id_to_item, carts
from cart import get_cart_text
from config import ADMIN_ID

def find_category_by_item(iid: int) -> str | None:
    for cat, items in catalog.items():
        if iid in items:
            return cat
    return None

def register_catalog_handlers(dp):

    # Связь с админом
    @dp.callback_query(F.data == "contact_admin")
    async def contact_admin(callback: types.CallbackQuery):
        await callback.message.edit_text("Напишите админу: @maximstrukov", reply_markup=main_menu(callback.from_user.id))
        await callback.answer()

    # Кнопка "Главное меню"
    @dp.callback_query(F.data == "back_to_main")
    async def back_to_main(callback: types.CallbackQuery):
        await callback.message.edit_text("Главное меню:", reply_markup=main_menu(callback.from_user.id))
        await callback.answer()

    # Категории
    @dp.callback_query(F.data == "menu_categories")
    async def show_categories(callback: types.CallbackQuery):
        kb = InlineKeyboardBuilder()
        for category in catalog.keys():
            kb.button(text=category, callback_data=f"cat_{category}")
        kb.button(text="⬅️ Главное меню", callback_data="back_to_main")
        kb.adjust(1)
        await callback.message.edit_text("Выберите категорию:", reply_markup=kb.as_markup())
        await callback.answer()

    # Конкретная категория
    @dp.callback_query(F.data.startswith("cat_"))
    async def show_category(callback: types.CallbackQuery):
        cat = callback.data[4:]
        kb = InlineKeyboardBuilder()
        for iid, item in catalog[cat].items():
            kb.button(text=f"{item['name']} ({item['price']}₽)", callback_data=f"item_{iid}")
        kb.button(text="⬅️ Назад", callback_data="menu_categories")
        kb.button(text="⬅️ Главное меню", callback_data="back_to_main")
        kb.adjust(1)
        await callback.message.edit_text(f"Категория: {cat}", reply_markup=kb.as_markup())
        await callback.answer()

    # Карточка товара
    @dp.callback_query(F.data.startswith("item_"))
    async def show_item(callback: types.CallbackQuery):
        iid = int(callback.data.split("_")[1])
        item = id_to_item[iid]
        text = f"📸 {item['name']}\n💰 {item['price']}₽\nℹ️ {item['desc']}"
        kb = InlineKeyboardBuilder()
        kb.button(text="🛒 В корзину", callback_data=f"add_{iid}")
        kb.button(text="⬅️ Категории", callback_data="menu_categories")
        kb.button(text="⬅️ Главное меню", callback_data="back_to_main")
        kb.adjust(1)
        await callback.message.edit_text(text, reply_markup=kb.as_markup())
        await callback.answer()

    # Добавление в корзину (возвращаемся к списку товаров категории)
    @dp.callback_query(F.data.startswith("add_"))
    async def add_to_cart(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        iid = int(callback.data.split("_")[1])

        carts.setdefault(user_id, {})
        carts[user_id][iid] = carts[user_id].get(iid, 0) + 1

        cat = find_category_by_item(iid)
        kb = InlineKeyboardBuilder()
        for item_id, item in catalog[cat].items():
            kb.button(text=f"{item['name']} ({item['price']}₽)", callback_data=f"item_{item_id}")
        kb.button(text="⬅️ Назад", callback_data="menu_categories")
        kb.button(text="⬅️ Главное меню", callback_data="back_to_main")
        kb.adjust(1)

        await callback.message.edit_text(
            f"Категория: {cat}\n✅ {id_to_item[iid]['name']} добавлен в корзину",
            reply_markup=kb.as_markup()
        )
        await callback.answer()

    # Просмотр корзины
    @dp.callback_query(F.data == "show_cart")
    async def show_cart(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        text = get_cart_text(user_id)
        kb = InlineKeyboardBuilder()
        cart = carts.get(user_id, {})
        if cart:
            for iid in list(cart.keys()):
                kb.button(text=f"➕ {id_to_item[iid]['name']}", callback_data=f"inc_{iid}")
                kb.button(text=f"➖ {id_to_item[iid]['name']}", callback_data=f"dec_{iid}")
            kb.adjust(2)
            kb.button(text="✅ Оформить заказ", callback_data="checkout")
            kb.button(text="🗑 Очистить корзину", callback_data="clear_cart")
            kb.button(text="📂 Вернуться в категории", callback_data="menu_categories")
        kb.button(text="⬅️ Главное меню", callback_data="back_to_main")
        kb.adjust(2, 2)
        await callback.message.edit_text(text, reply_markup=kb.as_markup())
        await callback.answer()

    # Плюс/минус в корзине
    @dp.callback_query(F.data.startswith("inc_"))
    async def inc_item(callback: types.CallbackQuery):
        uid = callback.from_user.id
        iid = int(callback.data.split("_")[1])
        if uid in carts and iid in carts[uid]:
            carts[uid][iid] += 1
        await show_cart(callback)

    @dp.callback_query(F.data.startswith("dec_"))
    async def dec_item(callback: types.CallbackQuery):
        uid = callback.from_user.id
        iid = int(callback.data.split("_")[1])
        if uid in carts and iid in carts[uid]:
            carts[uid][iid] -= 1
            if carts[uid][iid] <= 0:
                del carts[uid][iid]
        await show_cart(callback)

    # Очистка корзины
    @dp.callback_query(F.data == "clear_cart")
    async def clear_cart(callback: types.CallbackQuery):
        carts[callback.from_user.id] = {}
        await callback.answer("Корзина очищена!")
        await show_cart(callback)
