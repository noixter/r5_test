import logging
import os
from typing import Optional

import aiohttp
from retry import retry
from domain.models import Book
from apis.connector import RestConnector
from apis.exceptions import ConnectorFails


logger = logging.getLogger(__name__)
logger.level = logging.INFO

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', None)
GOOGLE_API_URL = os.environ.get('GOOGLE_API_URL', 'https://www.googleapis.com/books/v1/volumes')

SEARCH_ATTRIBUTES = {
    'title': 'intitle',
    'author': 'inauthor',
    'publisher': 'inpublisher',
    'subject': 'subject',
    'isbn': 'isbn',
}


class GoogleBooksConnector(RestConnector):

    def __init__(self, api_key: str = GOOGLE_API_KEY):
        self.api_key = api_key
        self.url = GOOGLE_API_URL
        self.origin = 'Google Books API'

    def _authenticate_request(self) -> dict:
        """
        Add authentication details to request parameters.
        """
        assert self.api_key, "API key is required"
        headers = {'key': self.api_key}
        return headers

    @retry(ConnectorFails, tries=3, delay=2)
    async def _make_request(self, url: str, params: dict, headers: dict) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status != 200:
                    raise ConnectorFails("Failed to retrieve data from the API")
                return await response.json()

    async def search(self, search_params: dict) -> Optional[Book]:
        headers = self._authenticate_request()
        search_params = self._format_search_params(search_params)
        response = await self._make_request(self.url, params=search_params, headers=headers)

        # TODO handle multiple books
        data = response.get('items', [])
        if not data:
            return None
        book_data = data[0].get('volumeInfo', {})
        logger.info(f"Found book: {book_data}")
        book = Book(
            id=data[0].get('id'),
            title=book_data.get('title'),
            subtitle=book_data.get('subtitle', ''),
            authors=book_data.get('authors', []),
            categories=book_data.get('categories', []),
            publication_date=book_data.get('publishedDate', ''),
            editor=book_data.get('publisher', ''),
            description=book_data.get('description', ''),
            image=book_data.get('imageLinks', {}).get('thumbnail'),
            origin=self.origin
        )
        return book

    def _format_search_params(self, search_params: dict) -> dict:
        """
        Format search parameters for the API.
        """
        params = []
        for key, value in search_params.items():
            if key not in SEARCH_ATTRIBUTES.keys():
                continue
            params.append(f"{SEARCH_ATTRIBUTES[key]}:{value}")
        if not params:
            raise ValueError("Invalid search parameters")
        return {'q': '+'.join(params)}
