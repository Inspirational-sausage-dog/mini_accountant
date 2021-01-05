"""Сервер Telegram бота"""

import logging
import os

from aiogram import Bot, Dispatcher, executor, types

from categories import Categories

API_TOKEN = '433463558:AAFn6JW6dbT9xPG37KlDCGOSzrcSvpAPxD4'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start','help'])
async def send_welcome(message: types.Message):
    """/start or /help"""
    await message.reply("Спасибо Баке!\nБип-боп!")

@dp.message_handler(commands=['categories'])
async def show_categories(message: types.Message):
    categories = Categories.get_all_categories()
    answer_message = "Категории: \n\n* " +\
            ("\n* ".join([c.name for c in categories]))
    await message.answer(answer_message)
    
@dp.message_handler(commands=['add_category'])
async def add_category(message: types.Message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
