import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

BOT_TOKEN = "8664993494:AAHreU6aACxjWZyZiMMryTV304QSFrw7ib0"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer("ربات روشنه سامی 🚀")


async def main():
    print("Bot Started...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())