from datetime import datetime, timezone


RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


def parse_price(price_raw: str | None) -> dict:
    """
    Zamienia cenę tekstową na walutę i liczbę.
    """
    if not price_raw:
        return {
            "price_raw": None,
            "currency": None,
            "amount": None
        }

    cleaned_price = price_raw.strip()
    cleaned_price = cleaned_price.replace("Â", "")

    currency = None

    if "£" in cleaned_price:
        currency = "GBP"
    elif "$" in cleaned_price:
        currency = "USD"
    elif "€" in cleaned_price:
        currency = "EUR"

    amount_text = (
        cleaned_price
        .replace("£", "")
        .replace("$", "")
        .replace("€", "")
        .replace(",", ".")
        .strip()
    )

    try:
        amount = float(amount_text)
    except ValueError:
        amount = None

    return {
        "price_raw": cleaned_price,
        "currency": currency,
        "amount": amount
    }


def parse_rating(rating_text: str | None) -> dict:
    """
    Zamienia ocenę tekstową na wartość liczbową.
    """
    return {
        "rating_text": rating_text,
        "rating_value": RATING_MAP.get(rating_text)
    }


def build_book_record(
    title: str | None,
    detail_url: str | None,
    price_raw: str | None,
    availability: str | None,
    rating_text: str | None,
    source_url: str,
    run_id: str | None = None
) -> dict:
    """
    Buduje uporządkowany rekord książki zgodny z profilem danych
    """
    return {
        "basic_data": {
            "title": title,
            "detail_url": detail_url
        },
        "price_data": parse_price(price_raw),
        "availability_data": {
            "status": availability
        },
        "rating_data": parse_rating(rating_text),
        "metadata": {
            "source_url": source_url,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "run_id": run_id
        }
    }