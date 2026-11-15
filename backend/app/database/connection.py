
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Load the backend .env file
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

DATABASE_NAME = os.getenv("DATABASE_NAME", "learntrack_db")

client = None
db = None


def connect_database():
    global client, db

    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        raise ValueError("MONGO_URI is missing from the .env file")

    try:
        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=15000
        )

        # Test the connection
        client.admin.command("ping")

        db = client[DATABASE_NAME]

        print("MongoDB connected successfully!")
        print(f"Database: {DATABASE_NAME}")

        return db

    except PyMongoError as error:
        print(f"MongoDB connection failed: {error}")
        raise


def get_database():
    if db is None:
        raise RuntimeError("Database is not connected")

    return db
