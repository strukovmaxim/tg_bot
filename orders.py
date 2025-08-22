from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Bot
from datetime import datetime

from data import carts, id_to_item, orders_data, all_orders
from cart import get_cart_text, cart_totals
from config import ADMIN_ID


def register_order_handlers(dp):

    # checkout из корзины
    @dp.callback_query(lambda c: c.data == "checkout")
    async def checkout(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        if not carts.get(user_id):
            await callback.answer("Корзина пуста!", show_alert=True)
            return

        if user_id in orders_data and "name" in orders_data[user_id] and "phone" in orders_data[user_id]:
            # спрашиваем использовать старые данные или ввести новые
            kb = InlineKeyboardBuilder()
            kb.button(text="✅ Использовать старые", callback_data="use_saved_contacts")
            kb.button(text="✏️ Ввести новые", callback_data="enter_new_contacts")
            kb.adjust(1)
            await callback.message.answer(
                f"📇 Мы нашли ваши данные:\n\n"
                f"Имя: {orders_data[user_id]['name']}\n"
                f"Телефон: {orders_data[user_id]['phone']}\n\n"
                "Хотите использовать их снова или изменить?",
                reply_markup=kb.as_markup()
            )
        else:
            # если данных нет — спрашиваем имя
            await callback.message.answer("Введите ваше Имя и Фамилию, а так же ваш телеграм для связи:")
            orders_data[user_id] = {"step": "name"}
        await callback.answer()

    # использовать сохранённые данные
    @dp.callback_query(lambda c: c.data == "use_saved_contacts")
    async def use_saved_contacts(callback: types.CallbackQuery):
        uid = callback.from_user.id
        orders_data[uid]["step"] = "rental_period"
        await callback.message.answer("Введите период аренды с временем (например: 01.09 10:00 — 03.09 19:00):")
        await callback.answer()

    # ввести новые данные
    @dp.callback_query(lambda c: c.data == "enter_new_contacts")
    async def enter_new_contacts(callback: types.CallbackQuery):
        uid = callback.from_user.id
        orders_data[uid] = {"step": "name"}  # сбрасываем старые контакты
        await callback.message.answer("Введите ваше Имя и Фамилию, а так же ваш телеграм для связи:")
        await callback.answer()

    # ввод имени
    @dp.message(lambda m: orders_data.get(m.from_user.id, {}).get("step") == "name")
    async def process_name(message: types.Message):
        user_id = message.from_user.id
        orders_data[user_id]["name"] = message.text.strip()
        orders_data[user_id]["step"] = "phone"
        await message.answer("Введите ваш номер телефона:")

    # ввод телефона
    @dp.message(lambda m: orders_data.get(m.from_user.id, {}).get("step") == "phone")
    async def process_phone(message: types.Message):
        user_id = message.from_user.id
        orders_data[user_id]["phone"] = message.text.strip()
        orders_data[user_id]["step"] = "rental_period"
        await message.answer("Введите период аренды с временем (например: 01.09 10:00 — 03.09 19:00):")

    # ввод периода
    @dp.message(lambda m: orders_data.get(m.from_user.id, {}).get("step") == "rental_period")
    async def process_period(message: types.Message):
        user_id = message.from_user.id
        orders_data[user_id]["rental_period"] = message.text.strip()
        orders_data[user_id]["step"] = "comment"
        await message.answer(
            "Добавьте комментарий к заказу (например: нужна доставка, механик, точка встречи). "
            "Если ничего не нужно — напишите «-»."
        )

    # ввод комментария и финальный чек
    @dp.message(lambda m: orders_data.get(m.from_user.id, {}).get("step") == "comment")
    async def process_comment(message: types.Message):
        user_id = message.from_user.id
        comment = message.text.strip()
        if comment == "-":
            comment = "нет"
        orders_data[user_id]["comment"] = comment
        orders_data[user_id]["step"] = "review"

        nal, beznal = cart_totals(carts[user_id])
        cart_text = get_cart_text(user_id)

        text = (
            f"📦 Ваш заказ:\n\n"
            f"{cart_text}\n\n"
            f"Имя: {orders_data[user_id]['name']}\n"
            f"Телефон: {orders_data[user_id]['phone']}\n"
            f"🕒 Период: {orders_data[user_id]['rental_period']}\n"
            f"📝 Комментарий: {orders_data[user_id]['comment']}\n\n"
            f"Итого: 💰 {nal}₽ | 💳 {beznal}₽"
        )

        kb = InlineKeyboardBuilder()
        kb.button(text="✅ Подтвердить заказ", callback_data="confirm_order")
        kb.button(text="❌ Отменить", callback_data="cancel_order")
        kb.adjust(1)
        await message.answer(text, reply_markup=kb.as_markup())

    # подтверждение заказа
    @dp.callback_query(lambda c: c.data == "confirm_order")
    async def confirm_order(callback: types.CallbackQuery, bot: Bot):
        uid = callback.from_user.id
        data = orders_data.get(uid)
        if not data or data.get("step") != "review":
            await callback.answer("Действие недоступно.", show_alert=True)
            return

        # собираем заказ
        order = {
            "user_id": uid,
            "items": carts.get(uid, {}).copy(),
            "name": data.get("name"),
            "phone": data.get("phone"),
            "period": data.get("rental_period"),
            "comment": data.get("comment"),
            "status": "⏳ В обработке",
            "created_at": datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        all_orders.append(order)

        # текст корзины
        nal, beznal = cart_totals(order["items"])
        cart_text = get_cart_text(uid, order["items"])

        # текст для админа
        admin_text = (
            f"📦 Новый заказ от {order['name']} (id {uid})\n"
            f"📞 {order['phone']}\n"
            f"🕒 Период: {order['period']}\n"
            f"📝 Комментарий: {order['comment']}\n\n"
            f"{cart_text}\n\n"
            f"Итого: 💰 {nal}₽ | 💳 {beznal}₽"
        )

        # кнопки админу
        kb = InlineKeyboardBuilder()
        kb.button(text="✅ Подтвердить", callback_data=f"admin_confirm_{uid}")
        kb.button(text="❌ Отклонить", callback_data=f"admin_decline_{uid}")
        kb.adjust(2)
        await bot.send_message(ADMIN_ID, admin_text, reply_markup=kb.as_markup())

        # сообщение пользователю
        user_text = (
            f"Спасибо! Заказ отправлен админу ✅\n\n"
            f"📦 Ваш заказ:\n\n"
            f"{cart_text}\n\n"
            f"Имя: {order['name']}\n"
            f"Телефон: {order['phone']}\n"
            f"🕒 Период: {order['period']}\n"
            f"📝 Комментарий: {order['comment']}\n\n"
            f"Итого: 💰 {nal}₽ | 💳 {beznal}₽"
        )
        await callback.message.edit_text(user_text)

        # очистка корзины, но контакты остаются
        carts[uid] = {}
        if uid in orders_data:
            orders_data[uid].pop("step", None)
            orders_data[uid].pop("rental_period", None)
            orders_data[uid].pop("comment", None)

        await callback.answer()

    # отмена заказа
    @dp.callback_query(lambda c: c.data == "cancel_order")
    async def cancel_order(callback: types.CallbackQuery):
        uid = callback.from_user.id
        if uid in orders_data:
            orders_data[uid].pop("step", None)
            orders_data[uid].pop("rental_period", None)
            orders_data[uid].pop("comment", None)
        await callback.message.edit_text("Заказ отменён ❌")
        await callback.answer()
