import os

from app import mongo

import telebot
from flask import Flask, request

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ["TOKEN"]
CHAIRMAN = int(os.environ["CHAIRMAN"])
PRO = int(os.environ["PRO"])
ADMIN = [CHAIRMAN, PRO]
server = Flask(__name__)

categories = {
    "500": ["DAN", "EIE500", "EEE22", "CU2022"],
    "groups": ["CHAP", "AEIES", "CUCHM", "CUMCH", "CUMD", "CUSC", "DAN", "EIE500", "EEE22",
               "CU2022", "EIE400", "CU300", "CU2425", "FRESH"],
    "gen": ["CHAP", "AEIES", "CUMCH", "CUCHM", "CUMD", "CUSC"],
    "100": ["FRESH"],
    "200": ["CU2425"],
    "300": ["CU300"],
    "400": ["DAN", "EIE400"]
}


bot = telebot.TeleBot(TOKEN)
start_message_text = """Hi there !!! 👋\n\nI'm CUSC bot 🤖, the official bot of the CU Student Council.
I'm here to give you first hand information and news concerning student life on campus 🏫.
You can also connect with the student council through the official Instagram page:
https://www.instagram.com/studentcouncil_cu/\n\nStay tuned!!! 💥
"""


@bot.message_handler(commands=['start'])
def start_message_handler(message):
    chat = message.chat

    if chat.id not in ADMIN:
        bot.reply_to(message=message, text=start_message_text)
        mongo.insert_new_user(chat.id, chat.type)
        return
    bot.reply_to(message=message,
                 text=f"Hello {chat.first_name.split(' ')[0].title()},\nWhat message would you like to broadcast today?")


@bot.message_handler(func=lambda message: message.text.startswith("/sendphoto"))
def broadcast_photo(message):
    chat = message.chat

    if chat.id not in ADMIN:
        return

    # Get message text
    message_text = '\n'.join(message.text.split('\n')[2:])

    # Get a list of receivers categories
    receivers = message.text.split('\n')[1]
    receivers_list = [reciever.strip() for reciever in receivers.split(",")]
    group_names = [
        group_name for item in receivers_list for group_name in categories[item]]

    # Broadcast Photo to all categories
    group_ids = mongo.get_group_ids(group_names)
    image_id = mongo.get_image_id()
    for id in group_ids:
        bot.send_photo(chat_id=id, caption=message_text, photo=image_id)


@bot.message_handler(func=lambda message: message.chat.id in ADMIN)
def broadcast_message(message):

    # Get message text
    message_text = '\n'.join(message.text.split('\n')[1:])

    # Get a list of receivers categories
    receivers = message.text.split('\n')[0]

    # Broadcast to all users
    if receivers == "all":
        ids = mongo.get_ids()
        for id in ids:
            bot.send_message(chat_id=id, text=message_text)
        return

    # broadcast to groups
    receivers_list = [reciever.strip() for reciever in receivers.split(",")]
    group_names = [
        group_name for item in receivers_list for group_name in categories[item]]

    group_ids = mongo.get_group_ids(group_names)
    for id in group_ids:
        bot.send_message(chat_id=id, text=message_text)


@bot.message_handler(content_types=["photo"])
def save_new_image(message):
    chat = message.chat

    if chat.id not in ADMIN:
        return

    image_id = message.photo[0].file_id
    mongo.change_image_id(image_id)


@server.route("/" + TOKEN, methods=["POST"])
def getMessage():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://cusc-bot.herokuapp.com/" + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
