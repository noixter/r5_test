from unittest.mock import create_autospec, AsyncMock

import pytest
from faker import Faker
import random

from apis.connector import RestConnector
from data.repository import Repository
from domain.models import Book

fake = Faker()


@pytest.fixture
def create_fake_book() -> Book:
    def _create():
        return Book(
            id=fake.uuid4(),
            title=fake.sentence(nb_words=3),
            subtitle=fake.sentence(nb_words=5) if random.choice([True, False]) else None,
            authors=[fake.name() for _ in range(random.randint(1, 3))],
            categories=[fake.word() for _ in range(random.randint(1, 3))],
            publication_date=fake.date(),
            editor=fake.company(),
            description=fake.text(),
            image=fake.image_url() if random.choice([True, False]) else None
        )
    yield _create


@pytest.fixture
def mock_repository():
    """Fixture for creating a mock repository."""
    return create_autospec(Repository)


@pytest.fixture
def mock_clients():
    """Fixture for creating mock clients."""
    client1 = create_autospec(RestConnector, instance=True)
    client2 = create_autospec(RestConnector, instance=True)

    # Manually setting async methods to AsyncMock
    client1.search = AsyncMock()
    client2.search = AsyncMock()

    return [client1, client2]

