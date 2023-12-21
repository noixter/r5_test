import aiohttp
from typing import Optional

from retry import retry

from apis.connector import RestConnector
from apis.exceptions import ConnectorFails
from domain.models import Book


class OpenLibraryConnector(RestConnector):
    def __init__(self):
        self.url = "https://openlibrary.org"
        self.origin = "Open Library API"

    @retry(ConnectorFails, tries=3, delay=2)
    async def _make_request(self, url: str, params: dict, headers: dict) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status != 200:
                    raise ConnectorFails("Failed to retrieve data from the API")
                return await response.json()

    async def search(self, search_params: dict) -> Optional[Book]:
        search_url = f"{self.url}/search.json"
        data = await self._make_request(search_url, params=search_params, headers={})
        result = data.get('docs', [])
        if not result:
            return
        book = self._to_book(result[0])
        return book

    def _to_book(self, item: dict) -> Book:
        return Book(
            id=item.get('key').split('/')[-1],
            title=item.get('title'),
            subtitle=item.get('subtitle'),
            authors=item.get('author_name', []),
            categories=item.get('subject', []),
            publication_date=item.get('publish_date', '')[0],
            editor=item.get('publisher', '')[0],
            description=item.get('notes', ''),
            image=f"http://covers.openlibrary.org/b/id/{item.get('cover_i', '')}-L.jpg" if item.get('cover_i') else None,
            origin=self.origin
        )
