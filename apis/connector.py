from abc import ABC, abstractmethod
from typing import Dict, List
from data.repository import Repository  # Assuming Repository is imported from the correct module
from domain.models import Book  # Replace with your actual module name


class RestConnector(ABC):
    repository: Repository  # Type hint for the repository attribute
    origin: str

    @abstractmethod
    def search(self, search_params: Dict) -> List[Book]:
        """
        Abstract method to search through the repository using provided search parameters.

        :param search_params: A dictionary of search parameters.
        :return: A list of Book instances that match the search criteria.
        """
        ...
