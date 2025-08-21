import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- Конфиг ---
API_TOKEN = "7638897879:AAGhxCf1nBPNBmVWiXCKjvqdAJWBsj-Jc0k"
ADMIN_ID = 136480596  # твой Telegram ID

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- Каталог ---
catalog = {
    "Камеры": {
        1: {"name": "Canon C70", "price": 6000},
        2: {"name": "Canon C80", "price": 8000},
    },
    "Объективы / Оптика": {
        3: {"name": "Laowa Ranger 17-50", "price": 4000},
        4: {"name": "DZO Arles", "price": 15000},
    },
    "Звук": {
        5: {"name": "Rode NTG-2", "price": 500},
        6: {"name": "Hollyland Mars M1", "price": 2000},
        7: {"name": "Hollyland Solidcom 4S", "price": 4000},
    },
    "Аксессуары / Монтаж": {
        8: {"name": "Tilta Nano Focus II", "price": 2300},
        9: {"name": "Tilta Mirage", "price": 1000},
        10: {"name": "Площадка V-mount", "price": 1000},
        11: {"name": "Cine saddle", "price": 500},
        12: {"name": "V-mount 99", "price": 500},
        13: {"name": "Телега OnStage", "price": 1000},
        14: {"name": "Грипня и железки", "price": 1000},
        15: {"name": "Штатив", "price": 3000},
        16: {"name": "Сумка операторская", "price": 700},
    },
    "Флешки / Аккумуляторы": {
        17: {"name": "Флешки 256гб", "price": 500},
        18: {"name": "BP-30a", "price": 500},
        19: {"name": "NP-F970", "price": 500},
    },
}

# Быстрый индекс item_id -> item
id_to_item = {}
for cat_items in catalog.values():
    for iid, item in cat_items.items():
        id_to_item[iid] = item

# --- Хранилища ---
carts: dict[int, dict[int, int]] = {}      # user_id → { item_id: count }
orders_data: dict[int, dict] = {}          # user_id → данные текущего оформления
all_orders: list[dict] = []                # все заказы

# --- Вспомогательные функции ---
def get_cart_summary(user_id: int) -> tuple[int, int]:
    cart = carts.get(user_id, {})
    total_items = sum(cart.values())
    total_price = sum(id_to_item[iid]["price"] * qty for iid, qty in cart.items())
    return total_items, total_price

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
    lines.append(f"\nИтого: {total}₽")
    return "\n".join(lines)

def main_menu(user_id: int):
    items, price = get_cart_summary(user_id)
    kb = InlineKeyboardBuilder()
    kb.button(text="📂 Категории", callback_data="menu_categories")
    kb.button(text=f"🛒 Корзина ({items} | {price}₽)", callback_data="show_cart")
    kb.button(text="👤 Связь с админом", callback_data="contact_admin")
    kb.adjust(1)
    return kb.as_markup()

# --- Команды ---
@dp.message(Command("start"))
async def start(message: types.Message):
    text = (
        "Привет! 👋\n\n"
        "Это бот для аренды техники.\n"
        "Выберите категорию, соберите корзину и оформите заказ."
    )
    await message.answer(text, reply_markup=main_menu(message.from_user.id))

# --- Обработчики меню ---
@dp.callback_query(lambda c: c.data == "contact_admin")
async def contact_admin(callback: types.CallbackQuery):
    await callback.message.answer("Напишите админу: @maximstrukov")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "menu_categories")
async def show_categories(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    for category in catalog.keys():
        kb.button(text=category, callback_data=f"cat_{category}")
    kb.button(text="⬅️ Главное меню", callback_data="back_to_main")
    kb.adjust(1)
    await callback.message.edit_text("Выберите категорию:", reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text("Главное меню:", reply_markup=main_menu(callback.from_user.id))

@dp.callback_query(lambda c: c.data.startswith("cat_"))
async def show_category(callback: types.CallbackQuery):
    category = callback.data.replace("cat_", "")
    kb = InlineKeyboardBuilder()
    for item_id, item in catalog[category].items():
        kb.button(text=f"{item['name']} ({item['price']}₽)", callback_data=f"add_{item_id}")
    kb.button(text="⬅️ Назад", callback_data="menu_categories")
    kb.adjust(1)
    await callback.message.edit_text(f"Категория: {category}", reply_markup=kb.as_markup())

# --- Корзина ---
@dp.callback_query(lambda c: c.data.startswith("add_"))
async def add_to_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    item_id = int(callback.data.split("_")[1])
    carts.setdefault(user_id, {})
    carts[user_id][item_id] = carts[user_id].get(item_id, 0) + 1
    await callback.answer("Добавлено в корзину!")
    await callback.message.answer("✅ Товар добавлен.", reply_markup=main_menu(user_id))

@dp.callback_query(lambda c: c.data == "show_cart")
async def show_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    text = get_cart_text(user_id)
    kb = InlineKeyboardBuilder()
    cart = carts.get(user_id, {})

    if cart:
        for iid in cart.keys():
            name = id_to_item[iid]["name"]
            kb.button(text=f"➕ {name}", callback_data=f"inc_{iid}")
            kb.button(text=f"➖ {name}", callback_data=f"dec_{iid}")
        kb.adjust(2)
        kb.button(text="✅ Оформить заказ", callback_data="checkout")
        kb.button(text="🗑 Очистить корзину", callback_data="clear_cart")
        kb.button(text="⬅️ Главное меню", callback_data="back_to_main")
        kb.adjust(2, 1)
    else:
        kb.button(text="📂 Категории", callback_data="menu_categories")
        kb.button(text="⬅️ Главное меню", callback_data="back_to_main")
        kb.adjust(1)

    await callback.message.edit_text(text, reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith("inc_"))
async def inc_item(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    item_id = int(callback.data.split("_")[1])
    carts.setdefault(user_id, {})
    carts[user_id][item_id] = carts[user_id].get(item_id, 0) + 1
    await show_cart(callback)

@dp.callback_query(lambda c: c.data.startswith("dec_"))
async def dec_item(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    item_id = int(callback.data.split("_")[1])
    if carts.get(user_id, {}).get(item_id, 0) > 1:
        carts[user_id][item_id] -= 1
    else:
        carts[user_id].pop(item_id, None)
    await show_cart(callback)

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
        await callback.answer()
        return
    orders_data[user_id] = {"step": "name"}
    await callback.message.answer("Введите ваше Имя и Фамилию, а так же ваш телеграм для связи @telegram")
    await callback.answer()

@dp.message()
async def handle_order_steps(message: types.Message):
    user_id = message.from_user.id
    if user_id not in orders_data:
        return
    step = orders_data[user_id].get("step")

    if step == "name":
        orders_data[user_id]["name"] = message.text.strip()
        orders_data[user_id]["step"] = "phone"
        await message.answer("Введите ваш контактный телефон:")

    elif step == "phone":
        orders_data[user_id]["phone"] = message.text.strip()
        orders_data[user_id]["step"] = "rental_period"
        await message.answer("Введите период аренды текстом (например: с 25.08 по 28.08):")

    elif step == "rental_period":
        orders_data[user_id]["rental_period"] = message.text.strip()
        cart_text = get_cart_text(user_id)
        order_summary = (
            f"📦 Проверьте заказ:\n\n{cart_text}\n\n"
            f"Имя/ник: {orders_data[user_id]['name']}\n"
            f"Телефон: {orders_data[user_id]['phone']}\n"
            f"Аренда: {orders_data[user_id]['rental_period']}"
        )
        orders_data[user_id]["step"] = "review"
        kb = InlineKeyboardBuilder()
        kb.button(text="✅ Подтвердить", callback_data="confirm_order")
        kb.button(text="❌ Отмена", callback_data="cancel_order")
        kb.adjust(2)
        await message.answer(order_summary, reply_markup=kb.as_markup())

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
        f"Аренда: {data['rental_period']}"
    )
    order = {
        "user_id": user_id,
        "name": data["name"],
        "phone": data["phone"],
        "period": data["rental_period"],
        "items": carts.get(user_id, {}).copy(),
        "status": "pending"
    }
    all_orders.append(order)
    await send_order_to_admin(order, final_text)
    await callback.message.edit_text("Спасибо! Заказ отправлен админу. Ожидайте подтверждения. ✅")
    carts[user_id] = {}
    orders_data.pop(user_id, None)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "cancel_order")
async def cancel_order(callback: types.CallbackQuery):
    orders_data.pop(callback.from_user.id, None)
    await callback.message.edit_text("Оформление отменено.", reply_markup=main_menu(callback.from_user.id))
    await callback.answer()

# --- Админ-функции ---
async def send_order_to_admin(order, text):
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data=f"admin_confirm_{order['user_id']}")
    kb.button(text="❌ Отклонить", callback_data=f"admin_decline_{order['user_id']}")
    kb.adjust(2)
    await bot.send_message(ADMIN_ID, text, reply_markup=kb.as_markup())

@dp.callback_query(lambda c: c.data.startswith("admin_confirm_"))
async def admin_confirm(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[2])
    for order in reversed(all_orders):
        if order["user_id"] == user_id and order["status"] == "pending":
            order["status"] = "confirmed"
            await bot.send_message(user_id, "✅ Ваш заказ подтверждён админом!")
            await callback.message.edit_text(callback.message.text + "\n\n✅ Подтверждено")
            await callback.answer("Заказ подтверждён.")
            return
    await callback.answer("Заказ не найден или уже обработан.", show_alert=True)

@dp.callback_query(lambda c: c.data.startswith("admin_decline_"))
async def admin_decline(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[2])
    for order in reversed(all_orders):
        if order["user_id"] == user_id and order["status"] == "pending":
            order["status"] = "declined"
            await bot.send_message(user_id, "❌ Ваш заказ отклонён админом.")
            await callback.message.edit_text(callback.message.text + "\n\n❌ Отклонено")
            await callback.answer("Заказ отклонён.")
            return
    await callback.answer("Заказ не найден или уже обработан.", show_alert=True)

@dp.message(Command("orders"))
async def list_orders(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    if not all_orders:
        await message.answer("Заказов пока нет.")
        return
    text = "📋 Последние заказы:\n\n"
    for order in all_orders[-5:]:
        text += (
            f"👤 {order['name']} | {order['phone']}\n"
            f"📅 {order['period']}\n"
            f"Статус: {order['status']}\n"
            "------\n"
        )
    await message.answer(text)

# --- Запуск ---
async def main():
    print("[LOG] Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
