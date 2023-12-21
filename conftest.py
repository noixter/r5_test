from typing import Dict, List, TypeVar
from data.repository import Repository
from domain.models import Book

_M = TypeVar('_M', bound=Dict)


class FakeRepository(Repository):
    def __init__(self):
        self._client: List[_M] = []

    async def search(self, search_params: Dict) -> List[Book]:
        results = [
            item
            for item in self._client
            if all(getattr(item, k) == v for k, v in search_params.items())
        ]
        return [self.to_domain(result) for result in results]

    async def list(self, order_by: str = None, limit: int = None) -> List[Book]:
        results = self._client
        if order_by:
            results = sorted(self._client, key=lambda x: getattr(x, order_by, None))
        if limit:
            results = results[:limit]
        return [self.to_domain(item) for item in results]

    async def save(self, model: _M) -> None:
        self._client.append(model)

    async def delete(self, id: str) -> None:
        self._client = [item for item in self._client if getattr(item, 'id') != id]

    def to_domain(self, model: _M) -> Book:
        return model
