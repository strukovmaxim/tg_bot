from aiogram import types
from keyboards import main_menu

def register_start_handlers(dp):
    @dp.message(commands=["start"])
    async def cmd_start(message: types.Message):
        await message.answer(
            "👋 Добро пожаловать в Be gentle, it’s a rental!\n\n"
            "📽 Здесь можно арендовать камеры, оптику и аксессуары.\n"
            "Выберите действие из меню 👇",
            reply_markup=main_menu(message.from_user.id)
        )
