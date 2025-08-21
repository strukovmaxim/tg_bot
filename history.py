from aiogram import types
from data import all_orders
from cart import cart_totals
from keyboards import main_menu

def register_history_handlers(dp):

    @dp.callback_query(lambda c: c.data == "my_orders")
    async def my_orders(callback: types.CallbackQuery):
        uid = callback.from_user.id
        user_orders = [o for o in all_orders if o["user_id"] == uid]
        if not user_orders:
            await callback.message.edit_text("У вас пока нет заказов.", reply_markup=main_menu(uid))
        else:
            lines = ["📋 Ваши заказы:\n"]
            for i, order in enumerate(user_orders, 1):
                nal, beznal = cart_totals(order["items"])
                lines.append(
                    f"{i}. {order['period']} — {order['status']}\n"
                    f"💰 {nal}₽ | 💳 {beznal}₽\n"
                )
            await callback.message.edit_text("\n".join(lines), reply_markup=main_menu(uid))
        await callback.answer()
