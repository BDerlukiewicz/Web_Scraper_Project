import asyncio

import aiohttp

HEADERS = {
    "User-Agent": "Mozilla/5.0 WebScrapperProject/1.0"
}


async def fetch_html(session: aiohttp.ClientSession, url: str) -> tuple[str, str | None]:

    """
    Asynchronicznie pobiera kod HTML z podanego adresu URL.
    Zwraca krotke: (url, html albo None).
    """

    try:
        async with session.get(url, headers=HEADERS, timeout=10) as response:
            response.raise_for_status()

            html = await response.text(encoding="utf-8")

            return url, html


    except (aiohttp.ClientError, asyncio.TimeoutError) as error:
        print(f"Błąd pobierania strony: {url}")
        print(f"Szczegóły: {error}")
        return url, None
    
async def fetch_many(urls: list[str], concurrency_limit: int = 5) -> list[tuple[str, str | None]]:
    """
    Pobiera wiele stron równolegle z limitem jednoczesnych połączeń.
    """
    connector = aiohttp.TCPConnector(limit=concurrency_limit)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []

        for url in urls:
            task = fetch_html(session, url)
            tasks.append(task)

        results = await asyncio.gather(*tasks)

    return results
