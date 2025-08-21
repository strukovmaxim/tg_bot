from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import ADMIN_ID
from data import all_orders
from cart import get_cart_text, cart_totals
from keyboards import main_menu
from aiogram import Bot

def register_admin_handlers(dp):

    @dp.callback_query(lambda c: c.data.startswith("admin_confirm_"))
    async def admin_confirm(callback: types.CallbackQuery, bot: Bot):
        if callback.from_user.id != ADMIN_ID:
            await callback.answer("Недостаточно прав.", show_alert=True)
            return
        uid = int(callback.data.split("_")[2])
        for order in reversed(all_orders):
            if order["user_id"] == uid and order["status"] == "pending":
                order["status"] = "confirmed"
                cart_text = get_cart_text(uid)
                nal, beznal = cart_totals(order["items"])
                summary = (
                    f"✅ Ваш заказ подтверждён!\n\n{cart_text}\n\n"
                    f"Имя/ник: {order['name']}\n"
                    f"Телефон: {order['phone']}\n"
                    f"Аренда: {order['period']}\n"
                    f"Комментарий: {order['comment']}\n\n"
                    f"💰 Наличные: {nal}₽\n💳 Безнал (+9%): {beznal}₽"
                )
                kb = InlineKeyboardBuilder()
                kb.button(text="⬅️ Главное меню", callback_data="back_to_main")
                await bot.send_message(uid, summary, reply_markup=kb.as_markup())
                await callback.message.edit_text("Заказ подтверждён ✅")
                await callback.answer()
                return
        await callback.answer("Заказ не найден.", show_alert=True)

    @dp.callback_query(lambda c: c.data.startswith("admin_decline_"))
    async def admin_decline(callback: types.CallbackQuery, bot: Bot):
        if callback.from_user.id != ADMIN_ID:
            await callback.answer("Недостаточно прав.", show_alert=True)
            return
        uid = int(callback.data.split("_")[2])
        for order in reversed(all_orders):
            if order["user_id"] == uid and order["status"] == "pending":
                order["status"] = "declined"
                await bot.send_message(uid, "❌ Ваш заказ отклонён администратором.")
                await callback.message.edit_text("Заказ отклонён ❌")
                await callback.answer()
                return
        await callback.answer("Заказ не найден.", show_alert=True)
