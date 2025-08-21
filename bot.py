import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

API_TOKEN = "7638897879:AAGhxCf1nBPNBmVWiXCKjvqdAJWBsj-Jc0k"
ADMIN_ID = 136480596  # твой Telegram ID

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Каталог с подкатегориями и актуальными ценами
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
carts = {}          # корзины пользователей
orders_data = {}    # временные данные заказа

# Формирование текста корзины
def get_cart_text(user_id):
    cart = carts.get(user_id, [])
    if not cart:
        return "Корзина пуста."
    text = "🛒 Ваша корзина:\n\n"
    total = 0
    for category, items in catalog.items():
        for item_id, item in items.items():
            if item_id in cart:
                text += f"- {item['name']} — {item['price']}₽\n"
                total += item['price']
    text += f"\nИтого: {total}₽"
    return text

# Главное меню
def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="Категории", callback_data="menu_categories")
    kb.button(text="Корзина", callback_data="show_cart")
    kb.button(text="Связь с админом", callback_data="contact_admin")
    kb.adjust(1)
    return kb.as_markup()

# /start — приветствие
@dp.message(Command("start"))
async def start(message: types.Message):
    text = (
        "Привет! 👋\n\n"
        "Это бот для аренды техники. Вы можете выбрать категорию товаров, "
        "добавить их в корзину и оформить аренду.\n\n"
        "Главное меню:"
    )
    await message.answer(text, reply_markup=main_menu())

# Меню «Связь с админом»
@dp.callback_query(lambda c: c.data == "contact_admin")
async def contact_admin(callback: types.CallbackQuery):
    await callback.message.answer("Вы можете написать админу напрямую в Telegram: @maximstrukov")
    await callback.answer()

# Меню «Категории»
@dp.callback_query(lambda c: c.data == "menu_categories")
async def show_categories(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    for category in catalog.keys():
        kb.button(text=category, callback_data=f"cat_{category}")
    kb.button(text="⬅️ Главное меню", callback_data="back_to_main")
    kb.adjust(1)
    await callback.message.edit_text("Выберите категорию:", reply_markup=kb.as_markup())

# Кнопка «Назад» к главному меню
@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text("Главное меню:", reply_markup=main_menu())

# Выбор категории — показ товаров
@dp.callback_query(lambda c: c.data.startswith("cat_"))
async def show_category(callback: types.CallbackQuery):
    category = callback.data.replace("cat_", "")
    kb = InlineKeyboardBuilder()
    for item_id, item in catalog[category].items():
        kb.button(text=f"{item['name']} ({item['price']}₽)", callback_data=f"add_{item_id}")
    kb.button(text="⬅️ Назад", callback_data="menu_categories")
    kb.adjust(1)
    await callback.message.edit_text(f"Категория: {category}\nВыберите товар:", reply_markup=kb.as_markup())

# Добавление товара в корзину
@dp.callback_query(lambda c: c.data.startswith("add_"))
async def add_to_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    item_id = int(callback.data.split("_")[1])
    carts.setdefault(user_id, []).append(item_id)
    await callback.answer("Добавлено в корзину!")
    await callback.message.answer("Товар добавлен в корзину. Выберите следующую категорию или перейдите в корзину.", reply_markup=main_menu())

# Показ корзины
@dp.callback_query(lambda c: c.data == "show_cart")
async def show_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    text = get_cart_text(user_id)
    kb = InlineKeyboardBuilder()
    kb.button(text="Оформить заказ", callback_data="checkout")
    kb.button(text="Очистить корзину", callback_data="clear_cart")
    kb.button(text="⬅️ Главное меню", callback_data="back_to_main")
    kb.adjust(1)
    await callback.message.edit_text(text, reply_markup=kb.as_markup())

# Очистка корзины
@dp.callback_query(lambda c: c.data == "clear_cart")
async def clear_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    carts[user_id] = []
    await callback.answer("Корзина очищена!")
    await show_cart(callback)

# Начало оформления заказа
@dp.callback_query(lambda c: c.data == "checkout")
async def checkout(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not carts.get(user_id):
        await callback.message.answer("Ваша корзина пуста! Добавьте товары перед оформлением заказа.")
        return
    orders_data[user_id] = {"step": "name"}
    await callback.message.answer("Введите ваше Имя и @ник:")
    await callback.answer()

# Обработка шагов заказа
@dp.message()
async def handle_order_steps(message: types.Message):
    user_id = message.from_user.id
    if user_id not in orders_data:
        return
    step = orders_data[user_id].get("step")

    if step == "name":
        orders_data[user_id]["name"] = message.text
        orders_data[user_id]["step"] = "phone"
        await message.answer("Введите ваш контактный телефон:")

    elif step == "phone":
        orders_data[user_id]["phone"] = message.text
        orders_data[user_id]["step"] = "rental_period"
        await message.answer("Введите период аренды текстом (например: с 25.08 по 28.08):")

    elif step == "rental_period":
        orders_data[user_id]["rental_period"] = message.text
        # Формируем заказ
        cart_text = get_cart_text(user_id)
        order_summary = (
            f"📦 Новый заказ:\n\n{cart_text}\n\n"
            f"Имя/ник: {orders_data[user_id]['name']}\n"
            f"Телефон: {orders_data[user_id]['phone']}\n"
            f"Аренда: {orders_data[user_id]['rental_period']}"
        )
        await message.answer("Ваш заказ оформлен! ✅")
        await bot.send_message(ADMIN_ID, f"Новый заказ:\n\n{order_summary}")
        # Очистка корзины и данных
        carts[user_id] = []
        orders_data.pop(user_id)

# Запуск бота
async def main():
    print("[LOG] Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
