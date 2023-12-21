from typing import List, Optional, Annotated
from pydantic import BaseModel, Field, BeforeValidator
from datetime import datetime
from dateutil import parser


def validate_date(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        date = parser.parse(value, default=datetime(1, 1, 1))
        return date
    raise TypeError('Invalid type for date')


DateValidator = Annotated[datetime, BeforeValidator(validate_date)]


class Book(BaseModel):
    id: str
    title: str = Field(...)
    subtitle: Optional[str] = Field(None)
    authors: List[str] = Field(...)
    categories: List[str] = Field(...)
    publication_date: DateValidator = Field(...)
    editor: str = Field(...)
    description: str = Field(...)
    image: Optional[str] = Field(None)
    origin: str = Field(default='repository')

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "title": "Example Book Title",
                "subtitle": "An Example Subtitle",
                "authors": ["John Doe", "Jane Doe"],
                "categories": ["Fiction", "Adventure"],
                "publication_date": "2023-01-01",
                "editor": "Example Editor",
                "description": "This is an example description of the book.",
                "image": "https://example.com/image.jpg",
                "origin": "repository"
            }
        }


def validate_lower_string(value):
    if isinstance(value, str):
        return value.lower()
    raise TypeError('Invalid type for string')


LowerString = Annotated[str, BeforeValidator(validate_lower_string)]


class SearchParams(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publication_date: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Example Title",
                "author": "Author Name",
                "publication_date": "2023-01-01"
            }
        }
