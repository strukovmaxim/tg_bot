from aiogram import types
from data import all_orders
from config import ADMIN_ID
from cart import get_cart_text, cart_totals


def register_admin_handlers(dp):
    # подтверждение заказа админом
    @dp.callback_query(lambda c: c.data.startswith("admin_confirm_"))
    async def admin_confirm(callback: types.CallbackQuery):
        if callback.from_user.id != ADMIN_ID:
            await callback.answer("⛔ Только админ может выполнять это действие.", show_alert=True)
            return

        uid = int(callback.data.split("_")[-1])
        for order in all_orders:
            if order["user_id"] == uid:
                order["status"] = "✅ Подтверждён"

                # корзина
                cart_text = get_cart_text(uid, order["items"])
                nal, beznal = cart_totals(order["items"])

                # сообщение админу
                await callback.message.edit_text(callback.message.text + "\n\n✅ Заказ подтверждён")

                # сообщение пользователю
                user_text = (
                    f"✅ Ваш заказ подтверждён админом!\n\n"
                    f"📦 Ваш заказ:\n\n"
                    f"{cart_text}\n\n"
                    f"Имя: {order['name']}\n"
                    f"Телефон: {order['phone']}\n"
                    f"🕒 Период: {order['period']}\n"
                    f"📝 Комментарий: {order['comment']}\n\n"
                    f"Итого: 💰 {nal}₽ | 💳 {beznal}₽"
                )
                await callback.bot.send_message(uid, user_text)
                break

        await callback.answer()

    # отклонение заказа админом
    @dp.callback_query(lambda c: c.data.startswith("admin_decline_"))
    async def admin_decline(callback: types.CallbackQuery):
        if callback.from_user.id != ADMIN_ID:
            await callback.answer("⛔ Только админ может выполнять это действие.", show_alert=True)
            return

        uid = int(callback.data.split("_")[-1])
        for order in all_orders:
            if order["user_id"] == uid:
                order["status"] = "❌ Отклонён"

                # корзина
                cart_text = get_cart_text(uid, order["items"])
                nal, beznal = cart_totals(order["items"])

                # сообщение админу
                await callback.message.edit_text(callback.message.text + "\n\n❌ Заказ отклонён")

                # сообщение пользователю
                user_text = (
                    f"❌ К сожалению, ваш заказ был отклонён админом.\n\n"
                    f"📦 Заказ:\n\n"
                    f"{cart_text}\n\n"
                    f"Имя: {order['name']}\n"
                    f"Телефон: {order['phone']}\n"
                    f"🕒 Период: {order['period']}\n"
                    f"📝 Комментарий: {order['comment']}\n\n"
                    f"Итого: 💰 {nal}₽ | 💳 {beznal}₽"
                )
                await callback.bot.send_message(uid, user_text)
                break

        await callback.answer()
