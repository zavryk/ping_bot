import asyncpg
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode
from aiogram.utils import executor
import os
import asyncio
import socket
import random
import logging

API_TOKEN = os.getenv('ACCESS_TOKEN')
MONITORED_IP = os.getenv('NODE')
NODE_PORT = int(os.getenv('NODE_PORT', '53131'))  # Default to 53131 if NODE_PORT is not set
YOUR_CHAT_ID = os.getenv('YOUR_CHAT_ID')
DATABASE_URL = os.getenv('DATABASE_URL')

response_down = [
    "🔴 Наробився 🐧"
]

response_up = [
    "🟩 На місці! 👌"
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


async def check_ip_status_and_save_to_db(chat_id):
    current_status = await check_ip(MONITORED_IP, NODE_PORT)
    is_up = bool(current_status)
    status_message = random.choice(response_up) if is_up else random.choice(response_down)

    # Log the result of the status check
    status_result = "UP" if is_up else "DOWN"
    logging.info(f"IP {MONITORED_IP}:{NODE_PORT} status: {status_result}")

    # Save the event to the database
    await save_event_to_db(chat_id, is_up)

    # Логуємо повідомлення
    logging.info(f"Sent message to chat {chat_id}: {status_message}")
    await bot.send_message(chat_id=chat_id, text=status_message, parse_mode=ParseMode.MARKDOWN)
    return status_message


async def save_event_to_db(chat_id, is_up):
    # Connect to the database
    connection = await asyncpg.connect(DATABASE_URL)

    try:
        # Insert a new record into the events table
        await connection.execute(
            "INSERT INTO events (chat_id, event_time, status) VALUES ($1, CURRENT_TIMESTAMP, $2)",
            chat_id, "UP" if is_up else "DOWN"
        )
    finally:
        # Close the database connection
        await connection.close()


async def schedule_ip_status_check():
    previous_status = None

    while True:
        current_status = await check_ip(MONITORED_IP, NODE_PORT)
        is_up = bool(current_status)

        if previous_status is None or is_up != previous_status:
            # If the status changes, or it's the first check, send the status message and save to the database
            await check_ip_status_and_save_to_db(YOUR_CHAT_ID)
            previous_status = is_up

        await asyncio.sleep(30)  # Check every 30 seconds


# Інші функції залишаються незмінними

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(schedule_ip_status_check())
        executor.start_polling(dp, loop=loop, skip_updates=True)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
