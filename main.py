import telebot
import os
from re import findall
from subprocess import Popen, PIPE


def ping(host, ping_count) -> str:
    for ip in host:
        data = ""

        output = Popen(f"ping {ip} -n {ping_count}", stdout=PIPE, encoding="utf-8")

        for line in output.stdout:
            data = data + line
            ping_test = findall("TTL", data)
        if ping_test:
            return "UP"
        else:
            return "DOWN"


nodes = os.getenv("NODE")

# nodes = ["127.0.0.1"]
#result = ping(nodes, 3)
#print(result)

token = os.getenv("ACCESS_TOKEN")
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start', 'help'])
def send_text(message):
    result = ping(nodes, 3)  # Викликайте функцію ping тут
    if result == "DOWN":
        bot.send_message(message.chat.id, 'Федір віддихає \U0001F937')
    else:
        bot.send_message(message.chat.id, 'Федір работає \U0001F477')


if __name__ == '__main__':
    bot.infinity_polling()
