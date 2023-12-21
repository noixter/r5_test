import pytest

from domain.services import BookServices


@pytest.mark.asyncio
class TestServices:

    async def test_search_books_found_in_repository(
        self, mock_repository, mock_clients, create_fake_book
    ):
        book = create_fake_book()
        mock_repository.search.return_value = [book]

        book_service = BookServices(mock_repository, mock_clients)
        result = await book_service.search_books({"title": "Test Book"})

        assert result == [book]
        mock_repository.search.assert_called_once_with({"title": "Test Book"})
        for client in mock_clients:
            client.search.assert_not_called()

    async def test_search_books_found_in_client(
        self, mock_repository, mock_clients, create_fake_book
    ):
        book = create_fake_book()
        mock_repository.search.return_value = []
        mock_clients[0].search.return_value = book

        book_service = BookServices(mock_repository, mock_clients)
        result = await book_service.search_books({"title": "Test Book"})

        assert result == book
        mock_repository.search.assert_called_once_with({"title": "Test Book"})
        mock_clients[0].search.assert_called_once_with({"title": "Test Book"})
        mock_repository.save.assert_called_once_with(book)

    async def test_search_books_not_found_anywhere(
        self, mock_repository, mock_clients, create_fake_book
    ):
        mock_repository.search.return_value = []
        for client in mock_clients:
            client.search.return_value = None

        book_service = BookServices(mock_repository, mock_clients)
        result = await book_service.search_books({"title": "Unknown Book"})

        assert result == []
        mock_repository.search.assert_called_once_with({"title": "Unknown Book"})
        for client in mock_clients:
            client.search.assert_called_with({"title": "Unknown Book"})
