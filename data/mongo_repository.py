import re
from datetime import datetime
from typing import Callable, Optional

from dateutil import parser
from pymongo.errors import DuplicateKeyError

from data.repository import Repository
from domain.models import Book


class MongoDBRepository(Repository):

    def __init__(self, get_client: Callable, db_name: str, collection_name: str):
        self._client = get_client
        self.db_name = db_name
        self.collection_name = collection_name

    async def search(self, search_params: dict) -> list[Book]:
        breakpoint()
        query = {}
        if 'title' in search_params:
            query['title'] = {'$regex': search_params['title'], '$options': 'i'}

        if 'author' in search_params:
            query['authors'] = {'$all': [
                re.compile(author, re.IGNORECASE) for author in search_params['author']]
            }

        if 'publication_date' in search_params:
            date = parser.parse(search_params.get('publication_date'), default=datetime(1, 1, 1))
            query['publication_date'] = {"$gte": date, "$lt": date}
        async with self._client(self.collection_name, self.db_name) as client:
            results = client.find(query)
            results = await results.to_list(length=10)
            return [self.to_domain(doc) for doc in results]

    async def list(
        self, order_by: Optional[str] = None, limit: Optional[int] = None
    ) -> list[Book]:
        async with self._client(self.collection_name, self.db_name) as client:
            results = client.find()
            results = await results.to_list(length=limit)
            if order_by:
                results = results.sort(order_by)
            if limit:
                results = results.limit(limit)
            return [self.to_domain(doc) for doc in results]

    async def save(self, model: Book) -> None:
        async with self._client(self.collection_name, self.db_name) as client:
            try:
                client.insert_one(model.model_dump())
            except DuplicateKeyError:
                pass

    async def delete(self, id: str) -> None:
        async with self._client(self.collection_name, self.db_name) as client:
            client.delete_one({"id": id})

    def to_domain(self, model: dict) -> Book:
        return Book(**model)
