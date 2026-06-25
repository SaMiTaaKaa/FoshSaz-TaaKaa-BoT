import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from config import BOT_TOKEN, OWNER_ID
from database import (
    connect_db,
    add_words,
    get_words_count
)

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

waiting_for_words = set()


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


async def send_panel(message: Message):

    words_count = await get_words_count()

    text = (
        f"🔥 پنل ساخت تاکا\n\n"
        f"تعداد کلمات: {words_count}\n"
        f"تعداد سودوها: 0"
    )

    await message.answer(
        text,
        reply_markup=main_menu(True)
    )


@dp.message(CommandStart())
async def start_cmd(message: Message):

    if message.from_user.id != OWNER_ID:
        await message.answer(
            "⛔ شما دسترسی به ربات ندارید."
        )
        return

    await send_panel(message)


@dp.callback_query(F.data == "add_word")
async def add_word_button(callback: CallbackQuery):

    waiting_for_words.add(
        callback.from_user.id
    )

    await callback.message.answer(
        "📝 کلمات را ارسال کنید\n\nحداکثر 50 کلمه"
    )

    await callback.answer()


@dp.message()
async def receive_words(message: Message):

    user_id = message.from_user.id

    if user_id not in waiting_for_words:
        return

    words = message.text.split()

    if len(words) > 50:

        await message.answer(
            "❌ حداکثر 50 کلمه مجاز است."
        )

        return

    await add_words(words)

    waiting_for_words.remove(user_id)

    await message.answer(
        f"✅ {len(words)} کلمه ذخیره شد."
    )

    await send_panel(message)


async def main():

    print("Bot Started...")

    await connect_db()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())