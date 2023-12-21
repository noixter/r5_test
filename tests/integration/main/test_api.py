from unittest.mock import create_autospec, AsyncMock

from fastapi.testclient import TestClient

from apis.connector import RestConnector
from conftest import FakeRepository
from domain.services import BookServices
from main import app, get_book_services


client = TestClient(app)


def get_test_book_services() -> BookServices:
    test_repository = FakeRepository()
    client_1 = create_autospec(RestConnector)
    client_2 = create_autospec(RestConnector)
    test_clients = [client_1, client_2]
    return BookServices(test_repository, test_clients)


class TestBookEndpoints:

    @classmethod
    def setup_class(cls):
        services = get_test_book_services()
        cls.services = services
        app.dependency_overrides[get_book_services] = lambda: services

    def test_search_books_repository(self, create_fake_book):
        book = create_fake_book()
        self.services.repository._client.append(book)
        response = client.post(
            "/books/search",
            json={"title": book.title},
            headers={'api-key': 'super_secret'}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_search_books_client(self, create_fake_book):
        book = create_fake_book()
        for _client in self.services.clients:
            _client.search = AsyncMock(return_value=book)
        response = client.post(
            "/books/search",
            json={"title": book.title},
            headers={'api-key': 'super_secret'}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_search_books_not_found(self):
        for _client in self.services.clients:
            _client.search = AsyncMock(return_value=None)
        response = client.post(
            "/books/search",
            json={"title": "Test Book"},
            headers={'api-key': 'super_secret'}
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_list_books(self, create_fake_book):
        for _ in range(5):
            self.services.repository._client.append(create_fake_book())

        response = client.get(
            "/books",
            headers={'api-key': 'super_secret'}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_book(self, create_fake_book):
        book = create_fake_book()
        self.services.repository._client.append(book)
        response = client.get(
            f"/books/{book.id}",
            headers={'api-key': 'super_secret'}
        )
        assert response.status_code == 200
        assert response.json()['id'] == book.id

    def test_get_book_not_found(self):
        response = client.get(
            "/books/id_test",
            headers={'api-key': 'super_secret'}
        )
        assert response.status_code == 404

    def test_delete_book(self, create_fake_book):
        book = create_fake_book()
        self.services.repository._client.append(book)
        response = client.delete(
            f"/books/{book.id}",
            headers={'api-key': 'super_secret'}
        )
        assert response.status_code == 204

    def test_delete_book_not_found(self):
        response = client.delete(
            "/books/nonexistent_id",
            headers={'api-key': 'super_secret'}
        )
        assert response.status_code == 204

    def test_incorrect_search_params(self):
        response = client.post(
            "/books/search",
            json={"isbn": "12345"},
            headers={'api-key': 'super_secret'}
        )
        assert response.status_code == 400

    def test_non_authenticated_request(self):
        response = client.get("/books")
        assert response.status_code == 401

    def test_incorrect_api_key(self):
        response = client.get("/books", headers={'api-key': 'incorrect_key'})
        assert response.status_code == 403
