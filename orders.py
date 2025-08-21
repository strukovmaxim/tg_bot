from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from data import carts, orders_data, all_orders, users_data, id_to_item
from cart import get_cart_text, cart_totals
from keyboards import main_menu
from config import ADMIN_ID
from aiogram import Bot

def register_order_handlers(dp):

    @dp.callback_query(lambda c: c.data == "checkout")
    async def checkout(callback: types.CallbackQuery):
        uid = callback.from_user.id
        if uid not in carts or not carts[uid]:
            await callback.answer("Корзина пуста.", show_alert=True)
            return
        if uid in users_data:
            kb = InlineKeyboardBuilder()
            kb.button(text="✅ Да", callback_data="use_saved_contacts")
            kb.button(text="✏️ Ввести заново", callback_data="enter_name")
            kb.adjust(1)
            await callback.message.edit_text("Использовать сохранённые контакты?", reply_markup=kb.as_markup())
        else:
            orders_data[uid] = {"step": "name"}
            await callback.message.edit_text("Введите ваше Имя и Фамилию, а так же ваш телеграм для связи")
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "use_saved_contacts")
    async def use_saved(callback: types.CallbackQuery):
        uid = callback.from_user.id
        orders_data[uid] = {"step": "rental_period"}
        await callback.message.edit_text("Введите период аренды (например: 1-3 сентября)")
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "enter_name")
    async def enter_name(callback: types.CallbackQuery):
        uid = callback.from_user.id
        orders_data[uid] = {"step": "name"}
        await callback.message.edit_text("Введите ваше Имя и Фамилию, а так же ваш телеграм для связи")
        await callback.answer()

    @dp.message(lambda m: m.text and m.from_user.id in orders_data)
    async def handle_order_steps(message: types.Message, bot: Bot):
        uid = message.from_user.id
        step = orders_data[uid].get("step")
        if step == "name":
            orders_data[uid]["name"] = message.text
            orders_data[uid]["step"] = "phone"
            await message.answer("Введите ваш контактный телефон")
        elif step == "phone":
            orders_data[uid]["phone"] = message.text
            orders_data[uid]["step"] = "rental_period"
            await message.answer("Введите период аренды (например: 1-3 сентября)")
        elif step == "rental_period":
            orders_data[uid]["period"] = message.text
            orders_data[uid]["step"] = "comment"
            await message.answer("Добавьте комментарий к заказу (или напишите «нет»)")
        elif step == "comment":
            orders_data[uid]["comment"] = message.text
            cart = carts.get(uid, {})
            nal, beznal = cart_totals(cart)
            summary = (
                f"Ваш заказ:\n\n{get_cart_text(uid)}\n\n"
                f"Имя/ник: {orders_data[uid]['name']}\n"
                f"Телефон: {orders_data[uid]['phone']}\n"
                f"Аренда: {orders_data[uid]['period']}\n"
                f"Комментарий: {orders_data[uid]['comment']}\n\n"
                f"💰 Наличные: {nal}₽\n💳 Безнал (+9%): {beznal}₽"
            )
            kb = InlineKeyboardBuilder()
            kb.button(text="✅ Подтвердить", callback_data="confirm_order")
            kb.button(text="❌ Отмена", callback_data="cancel_order")
            kb.adjust(1)
            await message.answer(summary, reply_markup=kb.as_markup())
            orders_data[uid]["step"] = "review"

    @dp.callback_query(lambda c: c.data == "confirm_order")
    async def confirm_order(callback: types.CallbackQuery, bot: Bot):
        uid = callback.from_user.id
        order = {
            "user_id": uid,
            "items": carts.get(uid, {}).copy(),
            "name": orders_data[uid].get("name"),
            "phone": orders_data[uid].get("phone"),
            "period": orders_data[uid].get("period"),
            "comment": orders_data[uid].get("comment"),
            "status": "pending"
        }
        all_orders.append(order)
        users_data[uid] = {"name": order["name"], "phone": order["phone"]}
        await bot.send_message(ADMIN_ID, f"📦 Новый заказ от {order['name']}\n\n{get_cart_text(uid)}")
        carts[uid] = {}
        await callback.message.edit_text("Спасибо! Заказ отправлен админу ✅", reply_markup=main_menu(uid))
        orders_data.pop(uid, None)
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "cancel_order")
    async def cancel_order(callback: types.CallbackQuery):
        uid = callback.from_user.id
        orders_data.pop(uid, None)
        await callback.message.edit_text("❌ Заказ отменён.", reply_markup=main_menu(uid))
        await callback.answer()
