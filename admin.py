from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from data import all_orders
from config import ADMIN_ID


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
                await callback.message.edit_text(callback.message.text + "\n\n✅ Заказ подтверждён")
                await callback.bot.send_message(uid, "Ваш заказ ✅ подтверждён админом!")
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
                await callback.message.edit_text(callback.message.text + "\n\n❌ Заказ отклонён")
                await callback.bot.send_message(uid, "Ваш заказ ❌ был отклонён админом.")
                break

        await callback.answer()
