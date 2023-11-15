import telebot
import os
import logging
from flask import Flask, request

app = Flask(__name__)

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

token = os.getenv("ACCESS_TOKEN")

bot = telebot.TeleBot(token)

logging.basicConfig(level=logging.INFO)


@app.route('/' + token, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=os.getenv("WEBHOOK_URL") + token)
    return "!", 200

@app.route("/remove_webhook/")
def remove_webhook():
    bot.remove_webhook()
    return "Webhook removed", 200

@bot.message_handler(commands=['start', 'help'])
def send_text(message):
    result = ping(nodes, 3)
    if result == "DOWN":
        bot.send_message(message.chat.id, 'Федір віддихає \U0001F937')
    else:
        bot.send_message(message.chat.id, 'Федір працює \U0001F477')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))