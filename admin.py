from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from data import all_orders
from config import ADMIN_ID
from cart import get_cart_text, cart_totals

def register_admin_handlers(dp):

    # подтверждение админом
    @dp.callback_query(lambda c: c.data.startswith("admin_confirm_"))
    async def admin_confirm(callback: types.CallbackQuery):
        if callback.from_user.id != ADMIN_ID:
            await callback.answer("⛔ Только админ.", show_alert=True); return

        uid = int(callback.data.split("_")[-1])
        for order in reversed(all_orders):
            if order["user_id"] == uid and order["status"] == "⏳ В обработке":
                order["status"] = "✅ Подтверждён"
                nal, beznal = cart_totals(order["items"])
                cart_text = get_cart_text(uid, order["items"])
                summary = (
                    f"✅ Ваш заказ подтверждён!\n\n{cart_text}\n\n"
                    f"Имя: {order['name']}\nТелефон: {order['phone']}\n"
                    f"🕒 Период: {order['period']}\n📝 Комментарий: {order['comment']}\n\n"
                    f"Итого: 💰 {nal}₽ | 💳 {beznал}₽"
                )
                kb = InlineKeyboardBuilder()
                kb.button(text="🏠 Главное меню", callback_data="back_to_main")
                await callback.bot.send_message(uid, summary, reply_markup=kb.as_markup())
                await callback.message.edit_text("Заказ подтверждён ✅")
                await callback.answer()
                return
        await callback.answer("Заказ не найден или уже обработан.", show_alert=True)

    # отклонение админом
    @dp.callback_query(lambda c: c.data.startswith("admin_decline_"))
    async def admin_decline(callback: types.CallbackQuery):
        if callback.from_user.id != ADMIN_ID:
            await callback.answer("⛔ Только админ.", show_alert=True); return

        uid = int(callback.data.split("_")[-1])
        for order in reversed(all_orders):
            if order["user_id"] == uid and order["status"] == "⏳ В обработке":
                order["status"] = "❌ Отклонён"
                await callback.bot.send_message(uid, "Ваш заказ ❌ был отклонён администратором.")
                await callback.message.edit_text("Заказ отклонён ❌")
                await callback.answer()
                return
        await callback.answer("Заказ не найден или уже обработан.", show_alert=True)
