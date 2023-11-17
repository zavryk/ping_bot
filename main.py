import logging
import os
import asyncio
import datetime

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

print(MONITORED_IP)


timeout = 5
start = datetime.datetime.now()
while (datetime.datetime.now() - start).total_seconds() < timeout:
    otvet = ping(MONITORED_IP, timeout=timeout, ttl=20)
    if otvet: # завершаем в случае успеха

            break
print(otvet)

# for _ in range(5):
#     otvet = ping('10.200.231.203', timeout=20, ttl=20)
#     if not (otvet == False): # завершаем если успех или таймаут


async def check_ip(ip):
    timeout = 10
    start = datetime.datetime.now()
    while (datetime.datetime.now() - start).total_seconds() < timeout:
        res = ping(ip, timeout=timeout, ttl=20)
        if res:
            return True
        # Wait for 5 seconds before the next check
        await asyncio.sleep(5)
    return False


async def monitor_ip():
    prev_status = await check_ip(MONITORED_IP)
    while True:
        current_status = await check_ip(MONITORED_IP)
        if current_status != prev_status:
            await notify_status_change(current_status)
            prev_status = current_status
        # Wait for 30 seconds before the next check
        await asyncio.sleep(30)

@dp.message_handler(commands=['start'])
async def notify_status_change(is_up):
    status_message = f"IP {MONITORED_IP} {'доступний' if is_up else 'недоступний'}"
    await bot.send_message(chat_id=YOUR_CHAT_ID, text=status_message, parse_mode=ParseMode.MARKDOWN)


# @dp.message_handler(commands=['check_status'])
# async def check_status(message: types.Message):
#     current_status = await check_ip(MONITORED_IP)
#     await notify_status_change(current_status)


#@dp.message_handler(commands=['start'])
#async def start(message: types.Message):
 #   keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
 #   button_check_status = KeyboardButton('Перевірити статус')
 #   keyboard.add(button_check_status)

   # await message.answer("Вітаю! Я готовий моніторити статус IP-адреси.", reply_markup=keyboard)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(monitor_ip())
    executor.start_polling(dp, loop=loop, skip_updates=True)
