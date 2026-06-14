import csv
import os
from io import StringIO

import requests
from flask import Flask, Response, redirect, render_template, request, url_for
from pymongo import MongoClient


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
SCRAPER_ENGINE_URL = os.getenv("SCRAPER_ENGINE_URL", "http://localhost:8000")

DATABASE_NAME = "web_scraper_project"
BOOKS_COLLECTION = "books"
RUNS_COLLECTION = "scrape_runs"


app = Flask(__name__)


def get_database():
    client = MongoClient(MONGO_URI)
    return client[DATABASE_NAME]


def get_books_collection():
    database = get_database()
    return database[BOOKS_COLLECTION]


def get_runs_collection():
    database = get_database()
    return database[RUNS_COLLECTION]


@app.route("/")
def index():
    books_collection = get_books_collection()
    runs_collection = get_runs_collection()

    books_count = books_collection.count_documents({})

    last_run = runs_collection.find_one(
        {},
        sort=[("started_at", -1)]
    )

    return render_template(
        "index.html",
        books_count=books_count,
        last_run=last_run
    )


@app.route("/books")
def books():
    collection = get_books_collection()

    books_list = list(
        collection
        .find({})
        .sort("metadata.scraped_at", -1)
        .limit(100)
    )

    return render_template(
        "books.html",
        books=books_list
    )


@app.route("/export/books.csv")
def export_books_csv():
    """
    Eksportuje książki z MongoDB do pliku CSV.
    """
    collection = get_books_collection()

    books_list = list(
        collection
        .find({})
        .sort("metadata.scraped_at", -1)
    )

    output = StringIO()

    fieldnames = [
        "title",
        "detail_url",
        "price_raw",
        "amount",
        "currency",
        "availability",
        "rating_text",
        "rating_value",
        "source_url",
        "scraped_at",
        "run_id"
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for book in books_list:
        writer.writerow({
            "title": book.get("basic_data", {}).get("title"),
            "detail_url": book.get("basic_data", {}).get("detail_url"),
            "price_raw": book.get("price_data", {}).get("price_raw"),
            "amount": book.get("price_data", {}).get("amount"),
            "currency": book.get("price_data", {}).get("currency"),
            "availability": book.get("availability_data", {}).get("status"),
            "rating_text": book.get("rating_data", {}).get("rating_text"),
            "rating_value": book.get("rating_data", {}).get("rating_value"),
            "source_url": book.get("metadata", {}).get("source_url"),
            "scraped_at": book.get("metadata", {}).get("scraped_at"),
            "run_id": book.get("metadata", {}).get("run_id")
        })

    csv_data = output.getvalue()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=books_export.csv"
        }
    )


@app.route("/runs")
def runs():
    collection = get_runs_collection()

    runs_list = list(
        collection
        .find({})
        .sort("started_at", -1)
        .limit(50)
    )

    return render_template(
        "runs.html",
        runs=runs_list
    )


@app.route("/run-scraper", methods=["POST"])
def run_scraper():
    """
    Wysyła żądanie uruchomienia scrapera do kontenera scraper-engine.
    """
    pages = request.form.get("pages", "5")
    concurrency = request.form.get("concurrency", "5")
    processes = request.form.get("processes", "4")

    requests.post(
        f"{SCRAPER_ENGINE_URL}/run",
        json={
            "pages": pages,
            "concurrency": concurrency,
            "processes": processes
        },
        timeout=300
    )

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)