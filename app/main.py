import os
import time

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
    "gen": ["CHAP", "AEIES", "CUMCH", "CUCHM", "CUMD", "CUSC"],
    "100": ["FRESH"],
    "200": ["CU2425"],
    "300": ["CU300"],
    "400": ["DAN", "EIE400"]
}


bot = telebot.TeleBot(TOKEN)
start_message_text = """Hi there \!\!\! 👋\n\nI'm CUSC bot 🤖, the official bot of the CU Student Council\.
I'm here to give you first hand information and news concerning student life on campus 🏫\.
You can also connect with the student council through the [official Instagram page](https://www.instagram.com/studentcouncil_cu/):\n\nStay tuned\!\!\! 💥
"""

admin_start_message = """
categories \= \{
    "500": ["DAN", "EIE500", "EEE22", "CU2022"],
    "gen": ["CHAP", "AEIES", "CUMCH", "CUCHM", "CUMD", "CUSC"],
    "100": ["FRESH"],
    "200": ["CU2425"],
    "300": ["CU300"],
    "400": ["DAN", "EIE400"]
    "all": \- Groups and DMs
    "private": \- Dms Only
\}

Example
```
/sendphoto
100,200,300
I am the CUSC Bot
```
    This would send the a photo with the caption "I am the CUSC Bot" to "FRESH", "CU2425" and "CU300"

**NOTE:**
    The "all" and "private" categories cannot be used with any other category
"""


def send_messages(ids: str, func, **kwargs):
    count = 0
    for id in ids:
        try:
            func(id, **kwargs)
            count += 1
        except:
            continue
        if count % 20 == 0:
            time.sleep(.7)


@bot.message_handler(commands=['start'])
def start_message_handler(message):
    chat = message.chat
    mongo.insert_new_user(chat.id, chat.type)

    if chat.type != "private":
        return
    if chat.id not in ADMIN:
        bot.reply_to(message=message, text=start_message_text,
                     parse_mode="MarkdownV2")
        return
    bot.reply_to(message=message,
                 text=f"Hello {chat.first_name.split(' ')[0].title()},\n"+admin_start_message, parse_mode="MarkdownV2")


@bot.message_handler(func=lambda message: message.text.startswith("/sendphoto"))
def broadcast_photo(message):
    receivers = message.text.split('\n')[1]
    chat = message.chat

    if chat.id not in ADMIN:
        return
    image_id = mongo.get_image_id()

    # Get message text
    message_text = '\n'.join(message.text.split('\n')[2:])

    # Broadcast to all users
    if receivers.strip().lower() == "all":
        ids = mongo.get_ids()
        send_messages(ids, bot.send_photo,
                      caption=message_text, photo=image_id)
        return

    # Broadcast to dms only
    if receivers.strip().lower() == "private":
        ids = mongo.get_ids(chat_type="private")
        send_messages(ids, bot.send_photo,
                      caption=message_text, photo=image_id)
        return

    # Broadcast to groups only
    if receivers.strip().lower() == "groups":
        ids = mongo.get_ids(chat_type="supergroup")
        send_messages(ids, bot.send_photo,
                      caption=message_text, photo=image_id)
        return

    # Get a list of receivers categories
    receivers_list = [reciever.strip() for reciever in receivers.split(",")]
    group_names = [
        group_name for item in receivers_list for group_name in categories[item]]

    # Broadcast Photo to all categories
    group_ids = mongo.get_group_ids(group_names)

    send_messages(group_ids, bot.send_photo,
                  caption=message_text, photo=image_id)


@bot.message_handler(func=lambda message: message.chat.id in ADMIN)
def broadcast_message(message):
    receivers_list = [reciever.strip() for reciever in receivers.split(",")]

    # Get message text
    message_text = '\n'.join(message.text.split('\n')[1:])

    # Get a list of receivers categories
    receivers = message.text.split('\n')[0]

    # Broadcast to all users
    if receivers.strip().lower() == "all":
        ids = mongo.get_ids()
        send_messages(ids, bot.send_message,
                      text=message_text)
        return

    # Broadcast to dms only
    if receivers.strip().lower() == "private":
        ids = mongo.get_ids(chat_type="private")
        send_messages(ids, bot.send_message,
                      text=message_text)
        return

    # Broadcast to groups only
    if receivers.strip().lower() == "groups":
        ids = mongo.get_ids(chat_type="supergroup")
        send_messages(ids, bot.send_message,
                      text=message_text)
        return

    # Broadcast to custom set of groups
    group_names = [
        group_name for item in receivers_list for group_name in categories[item]]

    group_ids = mongo.get_group_ids(group_names)
    send_messages(group_ids, bot.send_message,
                  text=message_text)


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
