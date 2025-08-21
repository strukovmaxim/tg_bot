import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

API_TOKEN = "7638897879:AAGhxCf1nBPNBmVWiXCKjvqdAJWBsj-Jc0k"
ADMIN_ID = 136480596  # твой Telegram ID

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Каталог
catalog = {
    "Камеры": {
        1: {"name": "Canon C70", "price": 6000},
        2: {"name": "Canon C80", "price": 8000},
    },
    "Объективы / Оптика": {
        3: {"name": "Laowa Ranger 17-50", "price": 4000},
        4: {"name": "DZO Arles", "price": 15000},
    },
    "Звук": {
        5: {"name": "Rode NTG-2", "price": 500},
        6: {"name": "Hollyland Mars M1", "price": 2000},
        7: {"name": "Hollyland Solidcom 4S", "price": 4000},
    },
    "Аксессуары / Монтаж": {
        8: {"name": "Tilta Nano Focus II", "price": 2300},
        9: {"name": "Tilta Mirage", "price": 1000},
        10: {"name": "Площадка V-mount", "price": 1000},
        11: {"name": "Cine saddle", "price": 500},
        12: {"name": "V-mount 99", "price": 500},
        13: {"name": "Телега OnStage", "price": 1000},
        14: {"name": "Грипня и железки", "price": 1000},
        15: {"name": "Штатив", "price": 3000},
        16: {"name": "Сумка операторская", "price": 700},
    },
    "Флешки / Аккумуляторы": {
        17: {"name": "Флешки 256гб", "price": 500},
        18: {"name": "BP-30a", "price": 500},
        19: {"name": "NP-F970", "price": 500},
    },
}

# Корзины: user_id → { item_id: count }
carts = {}
orders_data = {}

# Подсчёт содержимого корзины
def get_cart_summary(user_id):
    cart = carts.get(user_id, {})
    total_items = sum(cart.values())
    total_price = 0
    for category, items in catalog.items():
        for item_id, item in items.items():
            if item_id in cart:
                total_price += item["price"] * cart[item_id]
    return total_items, total_price

# Текст корзины
def get_cart_text(user_id):
    cart = carts.get(user_id, {})
    if not cart:
        return "🛒 Корзина пуста."
    text = "🛒 Ваша корзина:\n\n"
    total = 0
    for category, items in catalog.items():
        for item_id, item in items.items():
            if item_id in cart:
                qty = cart[item_id]
                price = item["price"] * qty
                text += f"- {item['name']} × {qty} — {price}₽\n"
                tota
