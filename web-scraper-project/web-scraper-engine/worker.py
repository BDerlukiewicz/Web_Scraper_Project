from parser import parse_books



def parse_page_worker(page_data: tuple[str, str | None, str]) -> list[dict]:
    """
    Funkcja uruchamiana w osobnym procesie
    Otrzymuje krotkę: (url, html, run_id)
    Zwraca listę książek z jednej strony
    """
    url, html, run_id = page_data

    if html is None:
        return []
    
    books = parse_books(html, source_url=url, run_id=run_id)

    return books