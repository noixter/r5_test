import asyncio
from typing import Optional, Union

from apis.connector import RestConnector
from apis.exceptions import ConnectorFails
from domain.exception import BookNotFound
from domain.models import Book


class BookServices:

    def __init__(self, repository, clients: list[RestConnector]):
        self.repository = repository
        self.clients = clients

    async def search_books(self, search_params: dict) -> Union[list[Book], Book, None]:
        books = await self.repository.search(search_params)
        if books:
            return books

        tasks = [client.search(search_params) for client in self.clients]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                continue
            if result:
                await self.repository.save(result)
                return result

        return []

    async def delete_book(self, id: str) -> None:
        await self.repository.delete(id)
