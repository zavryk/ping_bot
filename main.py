import logging
import os
import asyncio
import datetime
import httpx
import socket

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

def ping(host, port, timeout=10):
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except (socket.timeout, socket.error):
        return False

# Example
result = ping(MONITORED_IP,53131)
print(result)


# timeout = 5
# start = datetime.datetime.now()
# while (datetime.datetime.now() - start).total_seconds() < timeout:
#     otvet = ping(MONITORED_IP, timeout=timeout, ttl=20)
#     if otvet: # завершаем в случае успеха
#
#             break
# print(otvet)

async def check_ip(ip):
    timeout = 10
    start = datetime.datetime.now()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"http://{ip}", timeout=20)
            return response.status_code == 200

        #await asyncio.sleep(5)
    except Exception as e:
        logging.error(f"Error while checking IP {ip}: {e}")
    return False


async def monitor_ip():
    prev_status = await check_ip(MONITORED_IP)
    while True:
        current_status = await check_ip(MONITORED_IP)
        if current_status != prev_status:
            await notify_status_change(current_status)
            prev_status = current_status
        # Wait for 30 seconds before the next check
        await asyncio.sleep(60)


@dp.message_handler(commands=['start'])
async def notify_status_change(is_up: bool):
    status_message = f"IP {MONITORED_IP} {'доступний' if is_up else 'недоступний'}"
    await bot.send_message(chat_id=YOUR_CHAT_ID, text=status_message, parse_mode=ParseMode.MARKDOWN)

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(monitor_ip())
        executor.start_polling(dp, loop=loop, skip_updates=True)
    except Exception as e:
        logging.error(f"An error occurred: {e}")