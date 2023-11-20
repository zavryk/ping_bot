import logging
import os
import asyncio
import socket
import random

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode
from aiogram.utils import executor

API_TOKEN = os.getenv('ACCESS_TOKEN')
MONITORED_IP = os.getenv('NODE')
NODE_PORT = int(os.getenv('NODE_PORT', '53131'))  # Default to 53131 if NODE_PORT is not set
YOUR_CHAT_ID = os.getenv('YOUR_CHAT_ID')

response_down = [
    "🔴 Наробився 🐧"
    # "🔴 Работа нє волк 🐺",
    # "🔴 Я шо, коняка? 🐎",
    # "🔴 На сьогодні хватить 🧘",
    # "🔴 Хай поки сохне там 💆",
    # "🔴 Сьогодні 40 квадратів не получилось 🤔",
    # "🔴 Свєт вимкнув, воду вимкнув, до завтра 🙋‍♂️",
    # "🔴 Пішов просить сестру, щоб помогла з маляркою 👫",
    # "🔴 Пішов, бо й метро закриється 🌒"
]

response_up = [
    # "🟩 Добрий день! 🖖",
    # "🟩 Прийшов рано, щоб до 1 вересня кончить 🥹",
    # "🟩 Зайшов взнать, чи вже придумали, що на фартух вішать? 🐼",
    # "🟩 А де всі? 🤔",
    # "🟩 Сьогодні 40 квадратів здєлаю, а може й усі 50 🥸",
    "🟩 На місці! 👌"
    #"🟩 Сьогодні буду работать до ночі 💪"
]

logging.basicConfig(level=logging.DEBUG)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Set to keep track of sent messages
sent_messages = {}


async def check_ip(port, timeout=10):
    try:
        socket.create_connection((MONITORED_IP, port), timeout=timeout)
        return True
    except (socket.timeout, socket.error):
        return False

result = check_ip(MONITORED_IP, NODE_PORT)
print(result)


async def on_startup(_):
    # Removed check_current_status from on_startup
    pass


async def check_ip(host, port, timeout=10):
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except (socket.timeout, socket.error):
        return False


async def check_current_status(message: types.Message = None, force: bool = False):
    chat_id = message.chat.id if message and message.chat else YOUR_CHAT_ID

    # Always send the message, regardless of the value of force
    status_message = await check_ip_status(chat_id)
    sent_messages[chat_id] = status_message  # Update previous status

async def check_ip_status(chat_id):
    current_status = await check_ip(MONITORED_IP, NODE_PORT)
    is_up = bool(current_status)
    status_message = random.choice(response_up) if is_up else random.choice(response_down)

    # Log the result of the status check
    status_result = "UP" if is_up else "DOWN"
    logging.info(f"IP {MONITORED_IP}:{NODE_PORT} status: {status_result}")

    # Логуємо повідомлення
    logging.info(f"Sent message to chat {chat_id}: {status_message}")
    await bot.send_message(chat_id=chat_id, text=status_message, parse_mode=ParseMode.MARKDOWN)
    return status_message


async def schedule_ip_status_check():
    previous_status = None

    while True:
        current_status = await check_ip(MONITORED_IP, NODE_PORT)
        is_up = bool(current_status)

        if previous_status is None or is_up != previous_status:
            # If the status changes, or it's the first check, send the status message
            await check_current_status(force=True)
            previous_status = is_up

        await asyncio.sleep(30)  # Check every 30 seconds


@dp.message_handler(commands=['status'])
async def check_current_status_command(message: types.Message = None):
    await check_current_status(message)


@dp.message_handler(lambda message: message.text == 'А щас?')
async def call_status_command(message: types.Message):
    await check_current_status(message)


@dp.inline_handler(lambda query: True)
async def inline_status_query(inline_query: types.InlineQuery):
    current_status = await check_ip(MONITORED_IP, NODE_PORT)
    is_up = bool(current_status)
    status_message = random.choice(response_up) if is_up else random.choice(response_down)

    inline_result_id = f"{random.randint(1, 999)}_{is_up}"
    inline_result = types.InlineQueryResultArticle(
        id=inline_result_id,
        title="Статус",
        input_message_content=types.InputTextMessageContent(status_message)
    )
    try:
        await bot.answer_inline_query(inline_query.id, results=[inline_result], cache_time=0)
    except Exception as inner_exception:
        logging.error(f"An error occurred while answering inline query: {inner_exception}")

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(schedule_ip_status_check())
        executor.start_polling(dp, loop=loop, on_startup=on_startup, skip_updates=True)
    except Exception as e:
        logging.error(f"An error occurred: {e}")