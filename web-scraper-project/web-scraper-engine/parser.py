from urllib.parse import urljoin

from bs4 import BeautifulSoup

from models import build_book_record


def parse_books(html: str, source_url: str, run_id: str | None = None) -> list[dict]:
    """
    Parsuje stronę books.toscrape.com i zwraca listę książek
    w uporządkowanym profilu danych.
    """
    soup = BeautifulSoup(html, "html.parser")

    books = []
    book_items = soup.select("article.product_pod")

    for item in book_items:
        title_tag = item.select_one("h3 a")
        price_tag = item.select_one(".price_color")
        availability_tag = item.select_one(".availability")
        rating_tag = item.select_one("p.star-rating")

        title = title_tag["title"] if title_tag else None

        detail_url = None
        if title_tag and title_tag.get("href"):
            detail_url = urljoin(source_url, title_tag["href"])

        price_raw = price_tag.get_text(strip=True) if price_tag else None
        availability = availability_tag.get_text(strip=True) if availability_tag else None

        rating_text = None
        if rating_tag:
            rating_classes = rating_tag.get("class", [])
            for class_name in rating_classes:
                if class_name != "star-rating":
                    rating_text = class_name

        book = build_book_record(
            title=title,
            detail_url=detail_url,
            price_raw=price_raw,
            availability=availability,
            rating_text=rating_text,
            source_url=source_url,
            run_id=run_id
        )

        books.append(book)

    return books