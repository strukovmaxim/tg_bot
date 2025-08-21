from aiogram import types
from aiogram.filters import Command
from keyboards import main_menu
from data import orders_data

def register_start_handlers(dp):
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer(
            "👋 Добро пожаловать в Be gentle, it’s a rental!\n\n"
            "📽 Здесь можно арендовать камеры, оптику и аксессуары.\n"
            "Выберите действие из меню 👇",
            reply_markup=main_menu(message.from_user.id)
        )

    # fallback — только на "левый" текст и только если юзер НЕ в оформлении
    @dp.message(lambda m: m.text and not m.text.startswith("/") and m.from_user.id not in orders_data)
    async def fallback(message: types.Message):
        await message.answer(
            "Не понял сообщение 🤔\n\nВыберите действие из меню 👇",
            reply_markup=main_menu(message.from_user.id)
        )
