import os

from pymongo import MongoClient
from pymongo.collection import Collection


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = "web_scraper_project"
BOOKS_COLLECTION = "books"
RUNS_COLLECTION = "scrape_runs"


def get_database():
    client = MongoClient(MONGO_URI)
    return client[DATABASE_NAME]


def get_books_collection() -> Collection:
    database = get_database()
    return database[BOOKS_COLLECTION]


def get_runs_collection() -> Collection:
    database = get_database()
    return database[RUNS_COLLECTION]


def save_books(books: list[dict]) -> int:
    """
    Zapisuje listę książek do MongoDB.
    """
    if not books:
        return 0

    collection = get_books_collection()
    result = collection.insert_many(books)

    return len(result.inserted_ids)


def clear_books() -> int:
    """
    Czyści kolekcję książek.
    """
    collection = get_books_collection()
    result = collection.delete_many({})

    return result.deleted_count


def save_scrape_run(run_data: dict) -> str:
    """
    Zapisuje informacje o jednym uruchomieniu scrapera.
    """
    collection = get_runs_collection()
    result = collection.insert_one(run_data)

    return str(result.inserted_id)