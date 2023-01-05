import os
from click import group

from dotenv import load_dotenv

from pymongo import MongoClient

load_dotenv()
CONNECTION_STRING = os.environ["CONNECTION_STRING"]

client = MongoClient(CONNECTION_STRING)

db = client.get_default_database()
bot_users = db.Users
image = db.Images

def insert_new_user(id: int, chat_type: str) -> None:
    """
    Adds a participant to the leaderboard
    """
    try:
        bot_users.insert_one({"_id": str(id), "chat_type": f"{chat_type}"})
    except:
        return


def get_ids(**kwargs):
    """
    Get's the telegram Id's for all bot users
    """
    if not kwargs:
        all_users = bot_users.find({})
        return [user["_id"] for user in all_users]

    all_users = bot_users.find(kwargs)
    return [user["_id"] for user in all_users]


# def get_group_ids(group_names: list):
#     return [bot_users.find({"group_name": item})[0]["_id"] for item in group_names]


def change_media_id(id: int, type: str) -> None:
    """
    change image id
    """
    image.update_one({"_id": f"{type}"}, {"$set": {f"{type}_id": id}}, upsert=True)
    print("successfully updated")


def get_media_id(type: str) -> str:
    """
    Get Image ID from mongo
    """
    return image.find({"_id": f"{type}"})[0][f"{type}_id"]
