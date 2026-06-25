import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from config import BOT_TOKEN, OWNER_ID
from database import connect_db

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


# پنل اصلی
def main_menu(is_owner=False):

    buttons = [
        [
            InlineKeyboardButton(
                text="➕ افزودن کلمه",
                callback_data="add_word"
            )
        ],
        [
            InlineKeyboardButton(
                text="📋 نمایش کلمات",
                callback_data="show_words"
            )
        ],
        [
            InlineKeyboardButton(
                text="🧠 ساخت جمله",
                callback_data="make_sentence"
            )
        ]
    ]

    if is_owner:
        buttons.append([
            InlineKeyboardButton(
                text="👤 افزودن سودو",
                callback_data="add_sudo"
            )
        ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


@dp.message(CommandStart())
async def start_cmd(message: Message):

    user_id = message.from_user.id

    if user_id != OWNER_ID:
        await message.answer(
            "⛔ شما دسترسی به ربات ندارید."
        )
        return

    text = (
        "🔥 پنل ساخت تاکا\n\n"
        "تعداد کلمات: 0\n"
        "تعداد سودوها: 0"
    )

    await message.answer(
        text,
        reply_markup=main_menu(True)
    )


async def main():

    print("Bot Started...")

    await connect_db()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())