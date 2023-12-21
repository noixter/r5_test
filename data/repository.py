from abc import ABC, abstractmethod
from typing import Any, Dict, TypeVar, Optional

# Define a generic type variable _M
_M = TypeVar('_M')


class Repository(ABC):
    __client: Any

    @abstractmethod
    def search(self, search_params: Dict) -> Any:
        """
        Search in the database based on search_params
        """
        ...

    @abstractmethod
    def list(
        self,
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Any:
        """
        List items from the database based on order_by and slots
        """
        ...

    @abstractmethod
    def save(self, model: _M) -> None:
        """
        Save a model of type _M to the database
        """
        ...

    @abstractmethod
    def delete(self, id: str) -> None:
        """
        Delete an item from the database based on its ID
        """
        ...

    @abstractmethod
    def to_domain(self, model: _M) -> Any:
        """
        Convert the database model type _M to a domain model
        """
        ...
