from aiogram import types
from data import all_orders
from cart import cart_totals, get_cart_text


def register_history_handlers(dp):
    @dp.message(lambda m: m.text and m.text.lower() in ["история", "мои заказы"])
    async def show_history(message: types.Message):
        uid = message.from_user.id
        user_orders = [o for o in all_orders if o["user_id"] == uid]

        if not user_orders:
            await message.answer("📭 У вас пока нет заказов.")
            return

        # показываем все заказы пользователя
        for i, order in enumerate(user_orders, 1):
            nal, beznal = cart_totals(order["items"])
            cart_text = get_cart_text(uid, order["items"])  # передаём товары этого заказа

            text = (
                f"📖 Заказ №{i} от {order['created_at']}\n\n"
                f"{cart_text}\n\n"
                f"Имя: {order['name']}\n"
                f"Телефон: {order['phone']}\n"
                f"🕒 Период: {order['period']}\n"
                f"📝 Комментарий: {order['comment']}\n"
                f"Статус: {order['status']}\n\n"
                f"Итого: 💰 {nal}₽ | 💳 {beznal}₽"
            )

            await message.answer(text)
