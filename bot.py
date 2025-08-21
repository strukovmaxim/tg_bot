import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import API_TOKEN
import handlers

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

handlers.register_handlers(dp)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
