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
get_words_count,
get_all_words,
generate_sentence,
delete_word,
word_exists,
add_sudo,
remove_sudo,
is_sudo,
get_sudo_count
)

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

waiting_for_words = set()
waiting_for_delete = set()
waiting_for_sudo_add = set()
waiting_for_sudo_remove = set()

def main_menu(is_owner=False):

```
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
    ],
    [
        InlineKeyboardButton(
            text="🗑 حذف کلمه",
            callback_data="delete_word"
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

    buttons.append([
        InlineKeyboardButton(
            text="❌ حذف سودو",
            callback_data="remove_sudo"
        )
    ])

return InlineKeyboardMarkup(
    inline_keyboard=buttons
)
```

async def send_panel(message: Message):

```
words_count = await get_words_count()
sudo_count = await get_sudo_count()

is_owner_user = (
    message.from_user.id == OWNER_ID
)

text = (
    f"🔥 پنل ساخت تاکا\n\n"
    f"تعداد کلمات: {words_count}\n"
    f"تعداد سودوها: {sudo_count}"
)

await message.answer(
    text,
    reply_markup=main_menu(is_owner_user)
)
```

@dp.message(CommandStart())
async def start_cmd(message: Message):

```
user_id = message.from_user.id

allowed = (
    user_id == OWNER_ID
    or await is_sudo(user_id)
)

if not allowed:
    await message.answer(
        "⛔ شما دسترسی به ربات ندارید."
    )
    return

await send_panel(message)
```

@dp.callback_query(F.data == "add_word")
async def add_word_button(callback: CallbackQuery):

```
waiting_for_words.add(
    callback.from_user.id
)

await callback.message.answer(
    "📝 کلمات را ارسال کنید\n\nحداکثر 50 کلمه"
)

await callback.answer()
```

@dp.callback_query(F.data == "show_words")
async def show_words(callback: CallbackQuery):

```
words = await get_all_words()

if not words:

    await callback.message.answer(
        "❌ هنوز کلمه‌ای ثبت نشده."
    )

    await callback.answer()
    return

text = "\n".join(words)

if len(text) > 4000:
    text = text[:4000]

await callback.message.answer(text)

await callback.answer()
```

@dp.callback_query(F.data == "make_sentence")
async def make_sentence(callback: CallbackQuery):

```
sentence = await generate_sentence()

if not sentence:

    await callback.message.answer(
        "❌ هیچ کلمه‌ای در دیتابیس وجود ندارد."
    )

    await callback.answer()
    return

await callback.message.answer(sentence)

await callback.answer()
```

@dp.callback_query(F.data == "delete_word")
async def delete_word_button(callback: CallbackQuery):

```
waiting_for_delete.add(
    callback.from_user.id
)

await callback.message.answer(
    "🗑 کلمه مورد نظر برای حذف را ارسال کنید"
)

await callback.answer()
```

@dp.callback_query(F.data == "add_sudo")
async def add_sudo_button(callback: CallbackQuery):

```
if callback.from_user.id != OWNER_ID:
    await callback.answer(
        "فقط مالک",
        show_alert=True
    )
    return

waiting_for_sudo_add.add(
    callback.from_user.id
)

await callback.message.answer(
    "👤 آیدی عددی سودو را ارسال کنید"
)

await callback.answer()
```

@dp.callback_query(F.data == "remove_sudo")
async def remove_sudo_button(callback: CallbackQuery):

```
if callback.from_user.id != OWNER_ID:
    await callback.answer(
        "فقط مالک",
        show_alert=True
    )
    return

waiting_for_sudo_remove.add(
    callback.from_user.id
)

await callback.message.answer(
    "❌ آیدی عددی سودو را ارسال کنید"
)

await callback.answer()
```

@dp.message()
async def receive_messages(message: Message):

```
user_id = message.from_user.id

if user_id in waiting_for_sudo_add:

    try:
        sudo_id = int(
            message.text.strip()
        )

        await add_sudo(sudo_id)

        waiting_for_sudo_add.remove(
            user_id
        )

        await message.answer(
            "✅ سودو اضافه شد."
        )

        await send_panel(message)

    except:

        await message.answer(
            "❌ آیدی نامعتبر است."
        )

    return

if user_id in waiting_for_sudo_remove:

    try:
        sudo_id = int(
            message.text.strip()
        )

        await remove_sudo(sudo_id)

        waiting_for_sudo_remove.remove(
            user_id
        )

        await message.answer(
            "✅ سودو حذف شد."
        )

        await send_panel(message)

    except:

        await message.answer(
            "❌ آیدی نامعتبر است."
        )

    return

if user_id in waiting_for_delete:

    word = message.text.strip()

    exists = await word_exists(word)

    if not exists:

        waiting_for_delete.remove(
            user_id
        )

        await message.answer(
            "❌ این کلمه وجود ندارد."
        )

        return

    await delete_word(word)

    waiting_for_delete.remove(
        user_id
    )

    await message.answer(
        f"✅ کلمه {word} حذف شد."
    )

    await send_panel(message)

    return

if user_id in waiting_for_words:

    words = message.text.split()

    if len(words) > 50:

        await message.answer(
            "❌ حداکثر 50 کلمه مجاز است."
        )

        return

    await add_words(words)

    waiting_for_words.remove(
        user_id
    )

    await message.answer(
        f"✅ {len(words)} کلمه ذخیره شد."
    )

    await send_panel(message)

    return
```

async def main():

```
print("Bot Started...")

await connect_db()

await dp.start_polling(bot)
```

if **name** == "**main**":
asyncio.run(main())
