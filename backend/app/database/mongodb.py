import os

from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")


client = MongoClient(MONGODB_URL)

db = client[MONGODB_DATABASE]


def check_database_connection():
    try:
        client.admin.command("ping")
        return True
    except Exception:
        return False
