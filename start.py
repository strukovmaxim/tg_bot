from aiogram import types
from keyboards import main_menu
from data import orders_data

def register_start_handlers(dp):
    @dp.message(commands=["start"])
    async def cmd_start(message: types.Message):
        await message.answer(
            "👋 Добро пожаловать в Be gentle, it’s a rental!\n\n"
            "📽 Здесь можно арендовать камеры, оптику и аксессуары.\n"
            "Выберите действие из меню 👇",
            reply_markup=main_menu(message.from_user.id)
        )

    # fallback — только если пользователь НЕ оформляет заказ
    @dp.message(lambda m: m.text)
    async def fallback(message: types.Message):
        uid = message.from_user.id
        if uid in orders_data:  # если в процессе заказа — игнорируем
            return
        await message.answer(
            "Не понял сообщение 🤔\n\nВыберите действие из меню 👇",
            reply_markup=main_menu(uid)
        )
