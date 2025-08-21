import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- Конфиг ---
API_TOKEN = "7638897879:AAGhxCf1nBPNBmVWiXCKjvqdAJWBsj-Jc0k"
ADMIN_ID = 136480596

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- Каталог ---
catalog = {
    "Камеры": {
        1: {"name": "Canon C70", "price": 6000, "desc": "Кинокамера 4K, Super35, Dual Gain Output"},
        2: {"name": "Canon C80", "price": 8000, "desc": "Кинокамера с 6K сенсором и улучшенным автофокусом"},
    },
    "Объективы / Оптика": {
        3: {"name": "Laowa Ranger 17-50", "price": 4000, "desc": "Кино-зум для Super35"},
        4: {"name": "DZO Arles", "price": 15000, "desc": "Профессиональная кино-оптика"},
    },
    "Звук": {
        5: {"name": "Rode NTG-2", "price": 500, "desc": "Пушка-микрофон"},
        6: {"name": "Hollyland Mars M1", "price": 2000, "desc": "Монитор-передатчик видео"},
        7: {"name": "Hollyland Solidcom 4S", "price": 4000, "desc": "Беспроводная гарнитура для команды"},
    },
    "Аксессуары / Монтаж": {
        8: {"name": "Tilta Nano Focus II", "price": 2300, "desc": "Follow Focus система"},
        9: {"name": "Tilta Mirage", "price": 1000, "desc": "Матбокс с вари-ND фильтром"},
        10: {"name": "Площадка V-mount", "price": 1000, "desc": "Крепление батарей"},
        11: {"name": "Cine saddle", "price": 500, "desc": "Мягкая опора для камеры"},
        12: {"name": "V-mount 99", "price": 500, "desc": "Аккумулятор 99Wh"},
        13: {"name": "Телега OnStage", "price": 1000, "desc": "Тележка для оборудования"},
        14: {"name": "Грипня и железки", "price": 1000, "desc": "Разное оборудование для монтажа"},
        15: {"name": "Штатив", "price": 3000, "desc": "Профессиональный штатив"},
        16: {"name": "Сумка операторская", "price": 700, "desc": "Сумка для техники"},
    },
    "Флешки / Аккумуляторы": {
        17: {"name": "Флешки 256гб", "price": 500, "desc": "Карты памяти 256GB"},
        18: {"name": "BP-30a", "price": 500, "desc": "Аккумулятор BP-30a"},
        19: {"name": "NP-F970", "price": 500, "desc": "Аккумулятор NP-F970"},
    },
}

# --- Быстрый доступ ---
id_to_item = {iid: item for cat in catalog.values() for iid, item in cat.items()}

# --- Хранилища ---
carts: dict[int, dict[int, int]] = {}
orders_data: dict[int, dict] = {}
all_orders: list[dict] = []
users_data: dict[int, dict] = {}  # автозаполнение контактов

# --- Вспомогательные ---
def get_cart_text(user_id: int) -> str:
    cart = carts.get(user_id, {})
    if not cart:
        return "🛒 Корзина пуста."
    lines, total = ["🛒 Ваша корзина:\n"], 0
    for iid, qty in cart.items():
        item = id_to_item[iid]
        price = item["price"] * qty
        lines.append(f"- {item['name']} × {qty} — {price}₽")
        total += price
    total_nal = total
    total_beznal = int(total * 1.09)
    lines.append(f"\n💰 Итого (наличные): {total_nal}₽")
    lines.append(f"💳 Итого (безнал +9%): {total_beznal}₽")
    return "\n".join(lines)

def main_menu(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="📂 Категории", callback_data="menu_categories")
    kb.button(text="🛒 Корзина", callback_data="show_cart")
    kb.button(text="📋 Мои заказы", callback_data="my_orders")
    kb.button(text="👤 Связь с админом", callback_data="contact_admin")
    kb.adjust(1)
    return kb.as_markup()

# --- Команды ---
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! 👋 Это бот для аренды техники.", reply_markup=main_menu(message.from_user.id))

# --- Меню категорий ---
@dp.callback_query(lambda c: c.data == "menu_categories")
async def show_categories(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    for category in catalog.keys():
        kb.button(text=category, callback_data=f"cat_{category}")
    kb.button(text="⬅️ Главное меню", callback_data="back_to_main")
    kb.adjust(1)
    await callback.message.edit_text("Выберите категорию:", reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith("cat_"))
async def show_category(callback: types.CallbackQuery):
    category = callback.data.replace("cat_", "")
    kb = InlineKeyboardBuilder()
    for item_id, item in catalog[category].items():
        kb.button(text=f"{item['name']} ({item['price']}₽)", callback_data=f"item_{item_id}")
    kb.button(text="⬅️ Назад", callback_data="menu_categories")
    kb.adjust(1)
    await callback.message.edit_text(f"Категория: {category}", reply_markup=kb.as_markup())

# --- Карточка товара ---
@dp.callback_query(lambda c: c.data.startswith("item_"))
async def show_item(callback: types.CallbackQuery):
    item_id = int(callback.data.split("_")[1])
    item = id_to_item[item_id]
    text = f"📸 {item['name']}\n💰 Цена: {item['price']}₽\nℹ️ {item['desc']}"
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Добавить в корзину", callback_data=f"add_{item_id}")
    kb.button(text="⬅️ Назад", callback_data="menu_categories")
    kb.adjust(1)
    await callback.message.edit_text(text, reply_markup=kb.as_markup())

# --- Добавление в корзину ---
@dp.callback_query(lambda c: c.data.startswith("add_"))
async def add_to_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    item_id = int(callback.data.split("_")[1])
    carts.setdefault(user_id, {})
    carts[user_id][item_id] = carts[user_id].get(item_id, 0) + 1
    await callback.answer("Добавлено в корзину!")
    await callback.message.answer("✅ Товар добавлен.", reply_markup=main_menu(user_id))

# --- Корзина ---
@dp.callback_query(lambda c: c.data == "show_cart")
async def show_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    text = get_cart_text(user_id)
    kb = InlineKeyboardBuilder()
    if carts.get(user_id):
        kb.button(text="✅ Оформить заказ", callback_data="checkout")
        kb.button(text="🗑 Очистить корзину", callback_data="clear_cart")
        kb.button(text="📂 Вернуться в категории", callback_data="menu_categories")
    kb.button(text="⬅️ Главное меню", callback_data="back_to_main")
    kb.adjust(1)
    await callback.message.edit_text(text, reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data == "clear_cart")
async def clear_cart(callback: types.CallbackQuery):
    carts[callback.from_user.id] = {}
    await callback.answer("Корзина очищена!")
    await show_cart(callback)

# --- Оформление заказа ---
@dp.callback_query(lambda c: c.data == "checkout")
async def checkout(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not carts.get(user_id):
        await callback.message.answer("Ваша корзина пуста!")
        return
    if user_id in users_data:
        kb = InlineKeyboardBuilder()
        kb.button(text="✅ Да", callback_data="use_saved_contacts")
        kb.button(text="✏️ Ввести заново", callback_data="new_contacts")
        kb.adjust(2)
        await callback.message.answer(
            f"Использовать сохранённые контакты?\n\n👤 {users_data[user_id]['name']}\n📞 {users_data[user_id]['phone']}",
            reply_markup=kb.as_markup()
        )
    else:
        orders_data[user_id] = {"step": "name"}
        await callback.message.answer("Введите ваше Имя и Фамилию, а так же ваш телеграм для связи")

@dp.callback_query(lambda c: c.data == "use_saved_contacts")
async def use_saved_contacts(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    orders_data[user_id] = users_data[user_id].copy()
    orders_data[user_id]["step"] = "rental_period"
    await callback.message.answer("Введите период аренды (например: с 25.08 по 28.08):")

@dp.callback_query(lambda c: c.data == "new_contacts")
async def new_contacts(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    orders_data[user_id] = {"step": "name"}
    await callback.message.answer("Введите ваше Имя и Фамилию, а так же ваш телеграм для связи")

@dp.message()
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
        users_data[user_id] = {
            "name": orders_data[user_id]["name"],
            "phone": orders_data[user_id]["phone"]
        }
        orders_data[user_id]["step"] = "rental_period"
        await message.answer("Введите период аренды:")

    elif step == "rental_period":
        orders_data[user_id]["rental_period"] = message.text.strip()
        orders_data[user_id]["step"] = "comment"
        await message.answer("Добавьте комментарий к заказу (или напишите «-»):")

    elif step == "comment":
        orders_data[user_id]["comment"] = message.text.strip()
        cart_text = get_cart_text(user_id)
        order_summary = (
            f"📦 Проверьте заказ:\n\n{cart_text}\n\n"
            f"Имя/ник: {orders_data[user_id]['name']}\n"
            f"Телефон: {orders_data[user_id]['phone']}\n"
            f"Аренда: {orders_data[user_id]['rental_period']}\n"
            f"Комментарий: {orders_data[user_id]['comment']}"
        )
        orders_data[user_id]["step"] = "review"
        kb = InlineKeyboardBuilder()
        kb.button(text="✅ Подтвердить", callback_data="confirm_order")
        kb.button(text="❌ Отмена", callback_data="cancel_order")
        kb.adjust(2)
        await message.answer(order_summary, reply_markup=kb.as_markup())

# --- Подтверждение заказа ---
@dp.callback_query(lambda c: c.data == "confirm_order")
async def confirm_order(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    data = orders_data[user_id]
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
        "items": carts[user_id].copy(),
        "status": "pending"
    }
    all_orders.append(order)
    await send_order_to_admin(order, final_text)
    await callback.message.edit_text("Спасибо! Заказ отправлен админу. ✅")
    carts[user_id] = {}
    orders_data.pop(user_id, None)
    await callback.answer()

async def send_order_to_admin(order, text):
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data=f"admin_confirm_{order['user_id']}")
    kb.button(text="❌ Отклонить", callback_data=f"admin_decline_{order['user_id']}")
    kb.adjust(2)
    await bot.send_message(ADMIN_ID, text, reply_markup=kb.as_markup())
    try:
        await bot.send_message(ADMIN_CHAT_ID, text)
    except Exception:
        pass

# --- Запуск ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
