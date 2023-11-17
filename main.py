import logging
import os
import asyncio

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from ping3 import ping

API_TOKEN = os.getenv('ACCESS_TOKEN')
MONITORED_IP = os.getenv('NODE')
YOUR_CHAT_ID = os.getenv('YOUR_CHAT_ID')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


async def check_ip(ip):
    for _ in range(3):
        try:
            if ping(ip, timeout=1) is not None:
                return True
        except Exception as e:
            logging.error(f"Помилка при перевірці IP {ip}: {e}")

        # Зачекайте 5 секунд перед наступною спробою
        await asyncio.sleep(5)

    return False


async def monitor_ip():
    is_up = await check_ip(MONITORED_IP)
    while True:
        current_status = await check_ip(MONITORED_IP)

        if current_status != is_up:
            is_up = current_status
            await notify_status_change(is_up)

        # Зачекайте 60 секунд перед наступною перевіркою
        await asyncio.sleep(60)


async def notify_status_change(is_up):
    status_message = f"IP {MONITORED_IP} {'доступний' if is_up else 'недоступний'}"
    await bot.send_message(chat_id=YOUR_CHAT_ID, text=status_message, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=['check_status'])
async def check_status(message: types.Message):
    current_status = await check_ip(MONITORED_IP)
    await notify_status_change(current_status)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_check_status = KeyboardButton('Перевірити статус')
    keyboard.add(button_check_status)

    await message.answer("Вітаю! Я готовий моніторити статус IP-адреси.", reply_markup=keyboard)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(monitor_ip())
    executor.start_polling(dp, loop=loop, skip_updates=True)
