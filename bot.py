import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- Конфиг ---
API_TOKEN = "7638897879:AAGhxCf1nBPNBmVWiXCKjvqdAJWBsj-Jc0k"
ADMIN_ID = 136480596                      # твой Telegram ID
ADMIN_CHAT_ID = 0                         # если нужен чат для уведомлений, поставь ID

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- Каталог ---
catalog = {
    "Камеры": {
        1: {"name": "Canon C70", "price": 6000, "desc": "Кинокамера 4K, Super35"},
        2: {"name": "Canon C80", "price": 8000, "desc": "Кинокамера с 6K сенсором"},
    },
    "Оптика": {
        3: {"name": "Laowa Ranger 17-50", "price": 4000, "desc": "Кино-зум для Super35"},
        4: {"name": "DZO Arles", "price": 15000, "desc": "Профессиональная кино-оптика"},
    },
    "Звук": {
        5: {"name": "Rode NTG-2", "price": 500, "desc": "Пушка-микрофон"},
        6: {"name": "Hollyland Mars M1", "price": 2000, "desc": "Монитор-передатчик"},
        7: {"name": "Hollyland Solidcom 4S", "price": 4000, "desc": "Беспроводная гарнитура"},
    },
    "Аксессуары": {
        8: {"name": "Tilta Nano Focus II", "price": 2300, "desc": "Follow Focus"},
        9: {"name": "Tilta Mirage", "price": 1000, "desc": "Матбокс с ND"},
        10: {"name": "Площадка V-mount", "price": 1000, "desc": "Крепление батарей"},
        11: {"name": "Cine saddle", "price": 500, "desc": "Мягкая опора"},
        12: {"name": "V-mount 99", "price": 500, "desc": "Аккумулятор 99Wh"},
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

# --- Данные ---
carts = {}
orders_data = {}
all_orders = []
users_data = {}

# --- Хелперы ---
def cart_totals(cart):
    total = sum(id_to_item[iid]["price"] * qty for iid, qty in cart.items())
    return total, int(total * 1.09)

def get_cart_text(user_id):
    cart = carts.get(user_id, {})
    if not cart:
        return "🛒 Корзина пуста."
    lines = ["🛒 Ваша корзина:\n"]
    for iid, qty in cart.items():
        item = id_to_item[iid]
        lines.append(f"- {item['name']} × {qty} — {item['price']*qty}₽")
    nal, beznal = cart_totals(cart)
    lines.append(f"\n💰 Наличные: {nal}₽")
    lines.append(f"💳 Безнал (+9%): {beznal}₽")
    return "\n".join(lines)

def main_menu(user_id):
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

# --- Start ---
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! 👋 Это бот для аренды техники.", reply_markup=main_menu(message.from_user.id))

# --- Категории ---
@dp.callback_query(lambda c: c.data == "menu_categories")
async def show_categories(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    for category in catalog.keys():
        kb.button(text=category, callback_data=f"cat_{category}")
    kb.button(text="⬅️ Главное меню", callback_data="back_to_main")
    kb.adjust(1)
    await callback.message.edit_text("Выберите категорию:", reply_markup=kb.as_markup())
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("cat_"))
async def show_category(callback: types.CallbackQuery):
    cat = callback.data[4:]
    kb = InlineKeyboardBuilder()
    for iid, item in catalog[cat].items():
        kb.button(text=f"{item['name']} ({item['price']}₽)", callback_data=f"item_{iid}")
    kb.button(text="⬅️ Назад", callback_data="menu_categories")
    kb.adjust(1)
    await callback.message.edit_text(f"Категория: {cat}", reply_markup=kb.as_markup())
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("item_"))
async def show_item(callback: types.CallbackQuery):
    iid = int(callback.data.split("_")[1])
    item = id_to_item[iid]
    text = f"📸 {item['name']}\n💰 {item['price']}₽\nℹ️ {item['desc']}"
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 В корзину", callback_data=f"add_{iid}")
    kb.button(text="⬅️ Категории", callback_data="menu_categories")
    kb.adjust(1)
    await callback.message.edit_text(text, reply_markup=kb.as_markup())
    await callback.answer()

# --- Корзина ---
@dp.callback_query(lambda c: c.data == "show_cart")
async def show_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    text = get_cart_text(user_id)
    kb = InlineKeyboardBuilder()
    cart = carts.get(user_id, {})
    if cart:
        for iid in cart.keys():
            kb.button(text=f"➕ {id_to_item[iid]['name']}", callback_data=f"inc_{iid}")
            kb.button(text=f"➖ {id_to_item[iid]['name']}", callback_data=f"dec_{iid}")
        kb.adjust(2)
        kb.button(text="✅ Оформить заказ", callback_data="checkout")
        kb.button(text="🗑 Очистить корзину", callback_data="clear_cart")
    kb.button(text="⬅️ Главное меню", callback_data="back_to_main")
    kb.adjust(1)
    await callback.message.edit_text(text, reply_markup=kb.as_markup())
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("inc_"))
async def inc_item(callback: types.CallbackQuery):
    uid = callback.from_user.id
    iid = int(callback.data.split("_")[1])
    if uid in carts and iid in carts[uid]:
        carts[uid][iid] += 1
    await show_cart(callback)

@dp.callback_query(lambda c: c.data.startswith("dec_"))
async def dec_item(callback: types.CallbackQuery):
    uid = callback.from_user.id
    iid = int(callback.data.split("_")[1])
    if uid in carts and iid in carts[uid]:
        carts[uid][iid] -= 1
        if carts[uid][iid] <= 0:
            del carts[uid][iid]
    await show_cart(callback)

# --- Оформление заказа ---
# (оставим как было — с автосохранением контактов и комментарием)
# ...

# --- Подтверждение заказа админом ---
@dp.callback_query(lambda c: c.data.startswith("admin_confirm_"))
async def admin_confirm(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет прав", show_alert=True)
        return
    user_id = int(callback.data.split("_")[2])
    for order in reversed(all_orders):
        if order["user_id"] == user_id and order["status"] == "pending":
            order["status"] = "confirmed"
            lines, total = ["✅ Ваш заказ подтверждён!\n"], 0
            for iid, qty in order["items"].items():
                item = id_to_item[iid]
                total += item["price"] * qty
                lines.append(f"- {item['name']} × {qty} — {item['price']*qty}₽")
            nal, beznal = total, int(total*1.09)
            lines.append(f"\n💰 Наличные: {nal}₽")
            lines.append(f"💳 Безнал (+9%): {beznal}₽")
            lines.append(f"📅 Период: {order['period']}")
            lines.append(f"📝 Комментарий: {order['comment']}")
            kb = InlineKeyboardBuilder()
            kb.button(text="⬅️ Главное меню", callback_data="back_to_main")
            await bot.send_message(user_id, "\n".join(lines), reply_markup=kb.as_markup())
            await callback.message.edit_text(callback.message.text + "\n\n✅ Подтверждено")
            await callback.answer()
            return
    await callback.answer("Не найден", show_alert=True)

# --- Запуск ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
