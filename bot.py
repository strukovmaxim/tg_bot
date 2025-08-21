import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- Конфиг ---
API_TOKEN = "7638897879:AAGhxCf1nBPNBmVWiXCKjvqdAJWBsj-Jc0k"
ADMIN_ID = 136480596
ADMIN_CHAT_ID = 0  # если нужен чат для уведомлений, вставь ID группы

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
carts: dict[int, dict[int, int]] = {}
orders_data: dict[int, dict] = {}
all_orders: list[dict] = []
users_data: dict[int, dict] = {}

# --- Хелперы ---
def cart_totals(cart: dict[int, int]) -> tuple[int, int]:
    total = sum(id_to_item[iid]["price"] * qty for iid, qty in cart.items())
    return total, int(total * 1.09)

def get_cart_text(user_id: int) -> str:
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

def find_category_by_item(iid: int) -> str | None:
    for cat, items in catalog.items():
        if iid in items:
            return cat
    return None

# --- Команды ---
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привет! 👋 Это бот для аренды техники.\nВыберите категорию, соберите корзину и оформите заказ.",
        reply_markup=main_menu(message.from_user.id)
    )

# --- Общие кнопки ---
@dp.callback_query(lambda c: c.data == "contact_admin")
async def contact_admin(callback: types.CallbackQuery):
    await callback.message.edit_text("Напишите админу: @maximstrukov", reply_markup=main_menu(callback.from_user.id))
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text("Главное меню:", reply_markup=main_menu(callback.from_user.id))
    await callback.answer()

# --- Категории / Товары ---
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
    kb.button(text="⬅️ Главное меню", callback_data="back_to_main")
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
    kb.button(text="⬅️ Главное меню", callback_data="back_to_main")
    kb.adjust(1)
    await callback.message.edit_text(text, reply_markup=kb.as_markup())
    await callback.answer()

# --- Добавление в корзину ---
@dp.callback_query(lambda c: c.data.startswith("add_"))
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

    await callback.message.edit_text(f"Категория: {cat}\n✅ {id_to_item[iid]['name']} добавлен в корзину", reply_markup=kb.as_markup())
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
        kb.button(text="📂 Вернуться в категории", callback_data="menu_categories")
    kb.button(text="⬅️ Главное меню", callback_data="back_to_main")
    kb.adjust(2, 2)
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

@dp.callback_query(lambda c: c.data == "clear_cart")
async def clear_cart(callback: types.CallbackQuery):
    carts[callback.from_user.id] = {}
    await callback.answer("Корзина очищена!")
    await show_cart(callback)

# --- Оформление заказа (исправленный блок) ---
@dp.callback_query(lambda c: c.data == "checkout")
async def checkout(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not carts.get(user_id):
        await callback.message.answer("Ваша корзина пуста!")
        await callback.answer()
        return
    if user_id in users_data:
        saved = users_data[user_id]
        kb = InlineKeyboardBuilder()
        kb.button(text="✅ Да", callback_data="use_saved_contacts")
        kb.button(text="✏️ Ввести заново", callback_data="new_contacts")
        kb.adjust(2)
        await callback.message.answer(
            f"Использовать сохранённые контакты?\n\n👤 {saved['name']}\n📞 {saved['phone']}",
            reply_markup=kb.as_markup()
        )
    else:
        orders_data[user_id] = {"step": "name"}
        await callback.message.answer("Введите ваше Имя и Фамилию, а так же ваш телеграм для связи")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "use_saved_contacts")
async def use_saved_contacts(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    saved = users_data[user_id]
    orders_data[user_id] = {"name": saved["name"], "phone": saved["phone"], "step": "rental_period"}
    await callback.message.answer("Введите период аренды (например: с 25.08 по 28.08):")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "new_contacts")
async def new_contacts(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    orders_data[user_id] = {"step": "name"}
    await callback.message.answer("Введите ваше Имя и Фамилию, а так же ваш телеграм для связи")
    await callback.answer()

@dp.message(lambda m: m.text)
async def handle_order_steps(message: types.Message):
    user_id = message.from_user.id
    if user_id not in orders_data:
        return
    step = orders_data[user_id]["step"]

    if step == "name":
        orders_data[user_id]["name"] = message.text.strip()
        orders_data[user_id]["step"] = "phone"
        await message.answer("Введите ваш контактный телефон:")

    elif step == "phone":
        orders_data[user_id]["phone"] = message.text.strip()
        users_data[user_id] = {"name": orders_data[user_id]["name"], "phone": orders_data[user_id]["phone"]}
        orders_data[user_id]["step"] = "rental_period"
        await message.answer("Введите период аренды (например: с 25.08 по 28.08):")

    elif step == "rental_period":
        orders_data[user_id]["rental_period"] = message.text.strip()
        orders_data[user_id]["step"] = "comment"
        await message.answer("Добавьте комментарий к заказу (или напишите «-»):")

    elif step == "comment":
        orders_data[user_id]["comment"] = message.text.strip()
        orders_data[user_id]["step"] = "review"
        cart_text = get_cart_text(user_id)
        summary = (
            f"📦 Проверьте заказ:\n\n{cart_text}\n\n"
            f"Имя/ник: {orders_data[user_id]['name']}\n"
            f"Телефон: {orders_data[user_id]['phone']}\n"
            f"Аренда: {orders_data[user_id]['rental_period']}\n"
            f"Комментарий: {orders_data[user_id]['comment']}"
        )
        kb = InlineKeyboardBuilder()
        kb.button(text="✅ Подтвердить", callback_data="confirm_order")
        kb.button(text="❌ Отмена", callback_data="cancel_order")
        kb.adjust(2)
        await message.answer(summary, reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data == "confirm_order")
async def confirm_order(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    data = orders_data.get(user_id)
    if not data or data.get("step") != "review":
        await callback.answer("Действие недоступно.", show_alert=True)
        return
    cart_text = get_cart_text(user_id)
    final_text = (
        f"📦 Новый заказ:\n\n{cart_text}\n\n"
        f"Имя/ник: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Аренда: {data['rental_period']}\n"
        f"Комментарий: {data['comment']}"
    )
    order = {
        "user_id": user_id,
        "name": data["name"],
        "phone": data["phone"],
        "period": data["rental_period"],
        "comment": data["comment"],
        "items": carts.get(user_id, {}).copy(),
        "status": "pending"
    }
    all_orders.append(order)
    await send_order_to_admin(order, final_text)
    await callback.message.edit_text("Спасибо! Заказ отправлен админу. ✅")
    carts[user_id] = {}
    orders_data.pop(user_id, None)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "cancel_order")
async def cancel_order(callback: types.CallbackQuery):
    orders_data.pop(callback.from_user.id, None)
    await callback.message.edit_text("Оформление отменено.", reply_markup=main_menu(callback.from_user.id))
    await callback.answer()

# --- Админ функции ---
async def send_order_to_admin(order: dict, text: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data=f"admin_confirm_{order['user_id']}")
    kb.button(text="❌ Отклонить", callback_data=f"admin_decline_{order['user_id']}")
    kb.adjust(2)
    await bot.send_message(ADMIN_ID, text, reply_markup=kb.as_markup())
    if ADMIN_CHAT_ID:
        try:
            await bot.send_message(ADMIN_CHAT_ID, text)
        except Exception:
            pass

# --- Запуск ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
