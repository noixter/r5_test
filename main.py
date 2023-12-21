import os

from fastapi import FastAPI, Depends, HTTPException, Header
from starlette import status

from apis.google_connector import GoogleBooksConnector
from apis.open_library import OpenLibraryConnector
from data.mongo_connector import mongo_client, MONGO_DB
from data.mongo_repository import MongoDBRepository
from domain.services import BookServices
from domain.models import Book, SearchParams
from typing import Union

app = FastAPI()


def get_book_services() -> BookServices:
    collection_name = "books"
    repository = MongoDBRepository(mongo_client, MONGO_DB, collection_name)
    clients = [GoogleBooksConnector(), OpenLibraryConnector()]
    return BookServices(repository, clients)


API_KEY = os.environ.get('API_KEY', "super_secret")


def get_api_key(api_key: str = Header(None)):
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing Authentication method")
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key


@app.post("/books/search", response_model=Union[list[Book], Book, None])
async def search_books(
    search_params: SearchParams,
    services: BookServices = Depends(get_book_services),
    api_key: str = Depends(get_api_key)
):
    if not (search_params.title or search_params.author or search_params.publication_date):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Incorrect search params",
                "message": f"use one of this: {', '.join(search_params.model_fields)}"
            }
        )
    return await services.search_books(search_params.model_dump(exclude_none=True))


@app.get("/books", response_model=list[Book])
async def list_books(
    services: BookServices = Depends(get_book_services),
    api_key: str = Depends(get_api_key)
):
    return await services.repository.list()


@app.get("/books/{book_id}", response_model=Book)
async def get_book(
    book_id: str,
    services: BookServices = Depends(get_book_services),
    api_key: str = Depends(get_api_key)
):
    book = await services.search_books({"id": book_id})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book[0]


@app.delete(
    "/books/{book_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_book(
    book_id: str,
    services: BookServices = Depends(get_book_services),
    api_key: str = Depends(get_api_key)
):
    await services.delete_book(book_id)
    return None
