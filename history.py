from aiogram import types, F
from data import all_orders
from cart import cart_totals, get_cart_text

def register_history_handlers(dp):

    # Кнопка "Мои заказы" из меню
    @dp.callback_query(F.data == "my_orders")
    async def my_orders_cb(callback: types.CallbackQuery):
        uid = callback.from_user.id
        user_orders = [o for o in all_orders if o["user_id"] == uid]

        if not user_orders:
            await callback.message.edit_text("📭 У вас пока нет заказов.")
            await callback.answer(); return

        for i, order in enumerate(user_orders, 1):
            nal, beznal = cart_totals(order["items"])
            cart_text = get_cart_text(uid, order["items"])
            text = (
                f"📖 Заказ №{i} от {order['created_at']}\n"
                f"Статус: {order['status']}\n\n"
                f"{cart_text}\n\n"
                f"Имя: {order['name']}\nТелефон: {order['phone']}\n"
                f"🕒 Период: {order['period']}\n📝 Комментарий: {order['comment']}\n\n"
                f"Итого: 💰 {nal}₽ | 💳 {beznал}₽"
            )
            await callback.message.answer(text)
        await callback.answer()

    # Альтернативно по тексту "история"/"мои заказы"
    @dp.message(lambda m: m.text and m.text.lower() in ["история", "мои заказы"])
    async def my_orders_msg(message: types.Message):
        uid = message.from_user.id
        user_orders = [o for o in all_orders if o["user_id"] == uid]
        if not user_orders:
            await message.answer("📭 У вас пока нет заказов."); return
        for i, order in enumerate(user_orders, 1):
            nal, beznal = cart_totals(order["items"])
            cart_text = get_cart_text(uid, order["items"])
            text = (
                f"📖 Заказ №{i} от {order['created_at']}\n"
                f"Статус: {order['status']}\n\n"
                f"{cart_text}\n\n"
                f"Имя: {order['name']}\nТелефон: {order['phone']}\n"
                f"🕒 Период: {order['period']}\n📝 Комментарий: {order['comment']}\n\n"
                f"Итого: 💰 {nal}₽ | 💳 {beznал}₽"
            )
            await message.answer(text)
