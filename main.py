import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, WebAppInfo, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# ============================================
# КЛАВИАТУРЫ
# ============================================

def main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ ACTIVATE SOFTWARE",
            callback_data="activate_soft"
        )
    )
    return builder.as_markup()


def activated_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📊 OPEN TERMINAL",
            web_app=WebAppInfo(url="https://profitscannerbot.github.io/Profit_ScannerBotapp/")
        )
    )
    return builder.as_markup()


# ============================================
# СТАРТ — ПЕРВЫЙ ЭКРАН С ФОТО
# ============================================

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    try:
        photo = FSInputFile("welcome.jpg")
        await message.answer_photo(
            photo=photo,
            reply_markup=main_menu()
        )
    except Exception as e:
        await message.answer(
            "Welcome to Profit Scanner Bot!",
            reply_markup=main_menu()
        )


# ============================================
# АКТИВАЦИЯ — ВТОРОЙ ЭКРАН С ФОТО
# ============================================

@dp.callback_query(F.data == "activate_soft")
async def activate_soft(callback: CallbackQuery):
    try:
        photo = FSInputFile("activated.jpg")

        await callback.message.answer_photo(
            photo=photo,
            reply_markup=activated_menu()
        )

        try:
            await callback.message.delete()
        except:
            pass

    except Exception as e:
        await callback.message.edit_text(
            "Terminal activated!",
            reply_markup=activated_menu()
        )

    await callback.answer()


# ============================================
# ОБРАБОТКА ДАННЫХ ОТ MINI APP
# ============================================

@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    import json
    try:
        data = json.loads(message.web_app_data.data)
        asset = data.get('asset', 'Unknown')
        direction = data.get('direction', 'Unknown')

        await message.answer(
            f"✅ Signal received for {asset}!\n"
            f"Direction: {direction}\n\n"
            f"Good luck trading! 📊",
            parse_mode="HTML"
        )
    except:
        await message.answer("✅ Signal received! Check your terminal.")


# ============================================
# ЗАПУСК
# ============================================

async def main():
    print("🤖 Profit Scanner Bot is running!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
