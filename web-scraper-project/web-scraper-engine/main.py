import argparse
import asyncio
from datetime import datetime, timezone
from multiprocessing import Pool, cpu_count
from uuid import uuid4

from db import clear_books, save_books, save_scrape_run
from fetcher import fetch_many
from worker import parse_page_worker


BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"


def parse_arguments():
    """
    Odczytuje parametry scrapera przekazane z konsoli.
    """
    parser = argparse.ArgumentParser(description="Web scraper dla books.toscrape.com")

    parser.add_argument(
        "--pages",
        type=int,
        default=5,
        help="Liczba stron katalogu do pobrania"
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=5,
        help="Limit równoległych połączeń HTTP"
    )

    parser.add_argument(
        "--processes",
        type=int,
        default=4,
        help="Liczba procesów parsujących"
    )

    return parser.parse_args()


def build_page_urls(pages_count: int) -> list[str]:
    """
    Tworzy listę adresów URL do kolejnych stron katalogu.
    """
    urls = []

    for page_number in range(1, pages_count + 1):
        url = BASE_URL.format(page_number)
        urls.append(url)

    return urls


def prepare_pages_for_workers(
    fetched_pages: list[tuple[str, str | None]],
    run_id: str
) -> list[tuple[str, str | None, str]]:
    """
    Dodaje run_id do każdej pobranej strony przed wysłaniem do procesów.
    """
    pages_for_workers = []

    for url, html in fetched_pages:
        pages_for_workers.append((url, html, run_id))

    return pages_for_workers


def parse_pages_with_processes(
    pages_for_workers: list[tuple[str, str | None, str]],
    processes_count: int
) -> list[dict]:
    """
    Parsuje pobrane strony w wielu procesach.
    """
    all_books = []

    with Pool(processes=processes_count) as pool:
        results = pool.map(parse_page_worker, pages_for_workers)

    for books_from_page in results:
        all_books.extend(books_from_page)

    return all_books


def print_book(book: dict, index: int) -> None:

    print(f"{index}. {book['basic_data']['title']}")
    print(f"   Cena: {book['price_data']['price_raw']}")
    print(f"   Kwota: {book['price_data']['amount']}")
    print(f"   Waluta: {book['price_data']['currency']}")
    print(f"   Dostępność: {book['availability_data']['status']}")
    print(f"   Ocena: {book['rating_data']['rating_value']}")
    print()


async def run_scraper(
    pages_count: int,
    concurrency_limit: int,
    requested_processes_count: int
) -> list[dict]:
    """
    Pobiera strony asynchronicznie, parsuje wieloprocesowo,
    zapisuje książki i zapisuje status uruchomienia.
    """
    run_id = str(uuid4())

    available_cpus = cpu_count()
    processes_count = min(available_cpus, requested_processes_count)

    urls = build_page_urls(pages_count)

    started_at = datetime.now(timezone.utc)

    print(f"Run ID: {run_id}")
    print(f"Start: {started_at.isoformat()}")
    print(f"Liczba stron do pobrania: {len(urls)}")
    print(f"Limit równoległych połączeń: {concurrency_limit}")
    print(f"Dostępne rdzenie CPU: {available_cpus}")
    print(f"Liczba procesów parsujących: {processes_count}")
    print()

    all_books = []
    inserted_count = 0
    status = "success"
    error_message = None

    try:
        deleted_count = clear_books()
        print(f"Wyczyszczono rekordów z poprzedniego testu: {deleted_count}")
        print()

        fetched_pages = await fetch_many(urls, concurrency_limit=concurrency_limit)

        successful_pages = 0
        failed_pages = 0

        for url, html in fetched_pages:
            if html is None:
                failed_pages += 1
            else:
                successful_pages += 1

        print("Pobieranie zakończone.")
        print(f"Strony pobrane poprawnie: {successful_pages}")
        print(f"Strony z błędem: {failed_pages}")
        print("Rozpoczynam parsowanie w wielu procesach...")
        print()

        pages_for_workers = prepare_pages_for_workers(fetched_pages, run_id)

        all_books = parse_pages_with_processes(
            pages_for_workers=pages_for_workers,
            processes_count=processes_count
        )

        inserted_count = save_books(all_books)

        print(f"Zapisano rekordów do MongoDB: {inserted_count}")

    except Exception as error:
        status = "failed"
        error_message = str(error)
        print("Wystąpił błąd podczas pracy scrapera.")
        print(error_message)

    finished_at = datetime.now(timezone.utc)

    run_data = {
        "run_id": run_id,
        "status": status,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "pages_requested": len(urls),
        "books_found": len(all_books),
        "books_inserted": inserted_count,
        "concurrency_limit": concurrency_limit,
        "processes_count": processes_count,
        "error_message": error_message
    }

    save_scrape_run(run_data)

    return all_books


def main():
    args = parse_arguments()

    all_books = asyncio.run(
        run_scraper(
            pages_count=args.pages,
            concurrency_limit=args.concurrency,
            requested_processes_count=args.processes
        )
    )

    print()
    print("=" * 50)
    print(f"Łącznie znaleziono książek: {len(all_books)}")
    print("=" * 50)
    print()

    for index, book in enumerate(all_books[:10], start=1):
        print_book(book, index)

    if len(all_books) > 10:
        print(f"... pominięto wyświetlanie kolejnych rekordów: {len(all_books) - 10}")


if __name__ == "__main__":
    main()