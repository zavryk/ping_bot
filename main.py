import logging
import os
import asyncio
import socket
import random

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode
from aiogram.utils import executor

API_TOKEN = os.getenv('ACCESS_TOKEN')
MONITORED_IP = os.getenv('NODE')
YOUR_CHAT_ID = os.getenv('YOUR_CHAT_ID')


response_down = [
    "🔴 Наробився 💽",
    "🔴 Свєт пропав, або бажання робить пропало ♂",
    "🔴 Работа нє волк, подожде до завтра 🌌",
    "🔴 Я шо, коняка? 🐎",
    "🔴 На сьогодні хватить 🧘",
    "🔴 Хай пока сохне там 💆",
    "🔴 Свєт виключив, воду виключив, до завтра 🙋‍♂️",
    "🔴 Пішов просить сестру, щоб помогла з маляркою 👫",
    "🔴 Пішов, бо й метро закриється 🌒"
]

response_up = [
    "🟩 Добрий день! 🖖",
    "🟩 Прийшов оце рано, шоб до 1 вересня кончить ❄",
    "🟩 Зайшов спитать, чи же придумали, шо на фартух вішать? 🐼",
    "🟩 А де всі? 🤔",
    "🟩 На мєстє! 👌",
    "🟩 Сьогодні буду работать до ночі 💪"
]


logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def ping(host, port, timeout=10):
    try:
        socket.create_connection((MONITORED_IP, port), timeout=timeout)
        return True
    except (socket.timeout, socket.error):
        return False


result = ping(MONITORED_IP, 53131)
print(result)
async def check_ip(host, port, timeout=10):
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except (socket.timeout, socket.error):
        return False


async def monitor_ip():
    prev_status = await check_ip(MONITORED_IP, 53131)
    while True:
        current_status = await check_ip(MONITORED_IP, 53131)
        if current_status != prev_status:
            await notify_status_change(int(current_status))
            prev_status = current_status
        # Wait for 60 seconds before the next check
        await asyncio.sleep(120)


@dp.message_handler(commands=['start'])
async def notify_status_change(status: int):
    is_up = bool(status)  # Convert to boolean
    status_message = random.sample(response_up, 1)[0] if is_up else random.sample(response_down, 1)[0]
    await bot.send_message(chat_id=YOUR_CHAT_ID, text=str(status_message), parse_mode=ParseMode.MARKDOWN)


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(monitor_ip())
        executor.start_polling(dp, loop=loop, skip_updates=True)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
