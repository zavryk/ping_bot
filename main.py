import logging
import os
import asyncio
import socket
import random

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor

API_TOKEN = os.getenv('ACCESS_TOKEN')
MONITORED_IP = os.getenv('NODE')
YOUR_CHAT_ID = os.getenv('YOUR_CHAT_ID')

response_down = [
    "🔴 Наробився 🐧",
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

logging.basicConfig(level=logging.DEBUG)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Set to keep track of sent messages
sent_messages = set()


async def check_ip(port, timeout=10):
    try:
        socket.create_connection((MONITORED_IP, port), timeout=timeout)
        return True
    except (socket.timeout, socket.error):
        return False


result = check_ip(MONITORED_IP, 53131)
print(result)


async def on_startup(_):
    await check_current_status(force=True)
    # Schedule the IP status check every 120 seconds
    asyncio.create_task(schedule_ip_status_check())


async def check_ip(host, port, timeout=10):
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except (socket.timeout, socket.error):
        return False


async def check_current_status(message: types.Message = None, force: bool = False):
    chat_id = message.chat.id if message and message.chat else YOUR_CHAT_ID

    # If force is False and the message has already been sent, return
    if not force and chat_id in sent_messages:
        return

    await bot.send_message(chat_id=chat_id, text="Bot is starting...", parse_mode=ParseMode.MARKDOWN)
    await asyncio.sleep(5)  # Затримка для визначення статусу IP
    await check_ip_status(chat_id)
    sent_messages.add(chat_id)  # Add the chat_id to the set of sent messages


async def check_ip_status(chat_id):
    current_status = await check_ip(MONITORED_IP, 53131)
    is_up = bool(current_status)
    status_message = random.sample(response_up, 1)[0] if is_up else random.sample(response_down, 1)[0]

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text='А щас?'))

    # Логуємо повідомлення
    logging.info(f"Sent message to chat {chat_id}: {status_message}")
    await bot.send_message(chat_id=chat_id, text=status_message, parse_mode=ParseMode.MARKDOWN,
                           reply_markup=keyboard)


async def schedule_ip_status_check():
    while True:
        await asyncio.sleep(120)  # Wait for 120 seconds
        await check_ip_status(YOUR_CHAT_ID)


@dp.message_handler(commands=['status'])
async def check_current_status_command(message: types.Message = None):
    await check_current_status(message)


@dp.message_handler(lambda message: message.text == 'А щас?')
async def call_status_command(message: types.Message):
    await check_current_status(message)


@dp.inline_handler(lambda query: True)
async def inline_status_query(inline_query: types.InlineQuery):
    current_status = await check_ip(MONITORED_IP, 53131)
    is_up = bool(current_status)
    status_message = random.sample(response_up, 1)[0] if is_up else random.sample(response_down, 1)[0]

    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text='А щас?', switch_inline_query_current_chat='status'
        )
    )
    inline_result_id = f"{random.randint(1, 999)}_{is_up}"
    inline_result = types.InlineQueryResultArticle(
        id=inline_result_id,
        title="Статус",
        input_message_content=types.InputTextMessageContent(status_message),
        reply_markup=keyboard
    )
    try:
        await bot.answer_inline_query(inline_query.id, results=[inline_result], cache_time=0)
    except Exception as inner_exception:
        logging.error(f"An error occurred while answering inline query: {inner_exception}")


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(on_startup(None))
        executor.start_polling(dp, loop=loop, on_startup=on_startup, skip_updates=True)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
