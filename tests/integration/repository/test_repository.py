import pytest
from data.mongo_connector import mongo_client
from data.mongo_repository import MongoDBRepository
from faker import Faker

from data.repository import Repository

faker = Faker()


@pytest.fixture
def mongo_repository() -> Repository:
    repository = MongoDBRepository(
        mongo_client,
        db_name="test",
        collection_name="books"
    )

    return repository


class TestMongoDBRepository:

    @pytest.mark.asyncio
    async def test_save_and_search(
        self, create_fake_book, mongo_repository
    ):
        book = create_fake_book()
        await mongo_repository.save(book)

        found_books = await mongo_repository.search({"title": book.title})
        assert len(found_books) == 1
        assert found_books[0].title == book.title

    @pytest.mark.asyncio
    async def test_save_twice_an_element(
        self, create_fake_book, mongo_repository
    ):
        book = create_fake_book()

        await mongo_repository.save(book)
        await mongo_repository.save(book)

        found_books = await mongo_repository.search({"title": book.title})
        assert len(found_books) == 1
        assert found_books[0].title == book.title

    @pytest.mark.asyncio
    async def test_list(
        self, create_fake_book, mongo_repository
    ):
        for i in range(5):
            book = create_fake_book()
            await mongo_repository.save(book)

        books = await mongo_repository.list(order_by="id", limit=3)
        assert len(books) == 3

    @pytest.mark.asyncio
    async def test_delete(
        self, create_fake_book, mongo_repository
    ):
        book = create_fake_book()
        await mongo_repository.save(book)
        await mongo_repository.delete(book.id)

        found_books = await mongo_repository.search({"id": book.id})
        assert len(found_books) == 0
