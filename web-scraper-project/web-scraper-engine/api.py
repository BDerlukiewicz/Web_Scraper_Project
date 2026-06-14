import asyncio

from flask import Flask, jsonify, request

from main import run_scraper


app = Flask(__name__)


def get_int_param(data: dict, name: str, default: int, min_value: int, max_value: int) -> int:
    """
    Pobiera parametr liczbowy z JSON-a i ogranicza go do podanego zakresu.
    """
    try:
        value = int(data.get(name, default))
    except (TypeError, ValueError):
        value = default

    if value < min_value:
        value = min_value

    if value > max_value:
        value = max_value

    return value


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "scraper-engine"
    })


@app.route("/run", methods=["POST"])
def run():
    """
    Uruchamia scraper na żądanie z kontenera web.
    """
    data = request.get_json(silent=True) or {}

    pages = get_int_param(
        data=data,
        name="pages",
        default=5,
        min_value=1,
        max_value=50
    )

    concurrency = get_int_param(
        data=data,
        name="concurrency",
        default=5,
        min_value=1,
        max_value=20
    )

    processes = get_int_param(
        data=data,
        name="processes",
        default=4,
        min_value=1,
        max_value=16
    )

    books = asyncio.run(
        run_scraper(
            pages_count=pages,
            concurrency_limit=concurrency,
            requested_processes_count=processes
        )
    )

    return jsonify({
        "status": "success",
        "books_found": len(books),
        "pages": pages,
        "concurrency": concurrency,
        "processes": processes
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)