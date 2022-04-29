import os

import mongo

import telebot

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ["TOKEN2"]
PRO = int(os.environ["PRO"])
CHAIRMAN = int(os.environ["CHAIRMAN"])
AGS = int(os.environ["AGS"])
ADMIN = [CHAIRMAN, PRO, AGS]

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
    chat = message.chat

    if chat.id not in ADMIN:
        return
    image_id = mongo.get_image_id()

    # Get message text
    message_text = '\n'.join(message.text.split('\n')[2:])

    # Broadcast to all users
    if receivers.strip().lower() == "all":
        ids = mongo.get_ids()
        for id in ids:
            bot.send_photo(chat_id=id, caption=message_text, photo=image_id)
        return

    # Broadcast to dms only
    if receivers.strip().lower() == "private":
        ids = mongo.get_ids(chat_type="private")
        for id in ids:
            bot.send_photo(chat_id=id, caption=message_text, photo=image_id)
        return

    # Broadcast to groups only
    if receivers.strip().lower() == "groups":
        ids = mongo.get_ids(chat_type="supergroup")
        for id in ids:
            bot.send_photo(chat_id=id, caption=message_text, photo=image_id)
        return

    # Get a list of receivers categories
    receivers = message.text.split('\n')[1]
    receivers_list = [reciever.strip() for reciever in receivers.split(",")]
    group_names = [
        group_name for item in receivers_list for group_name in categories[item]]

    # Broadcast Photo to all categories
    group_ids = mongo.get_group_ids(group_names)
    for id in group_ids:
        bot.send_photo(chat_id=id, caption=message_text, photo=image_id)


@bot.message_handler(func=lambda message: message.chat.id in ADMIN)
def broadcast_message(message):

    # Get message text
    message_text = '\n'.join(message.text.split('\n')[1:])

    # Get a list of receivers categories
    receivers = message.text.split('\n')[0]

    # Broadcast to all users
    if receivers.strip().lower() == "all":
        ids = mongo.get_ids()
        for id in ids:
            bot.send_message(chat_id=id, text=message_text)
        return

    # Broadcast to dms only
    if receivers.strip().lower() == "private":
        ids = mongo.get_ids(chat_type="private")
        for id in ids:
            bot.send_message(chat_id=id, text=message_text)
        return

    # Broadcast to groups only
    if receivers.strip().lower() == "groups":
        ids = mongo.get_ids(chat_type="supergroup")
        for id in ids:
            bot.send_message(chat_id=id, text=message_text)
        return

    # Broadcast to custom set of groups
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


bot.infinity_polling()
