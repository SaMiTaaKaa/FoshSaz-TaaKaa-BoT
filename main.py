import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_TOKEN
from database import connect_db

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer("ربات روشنه سامی 🚀")


async def main():
    print("Bot Started...")

    await connect_db()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())