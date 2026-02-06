from __future__ import annotations

from typing import Any
from src.domain.book import Book


class MockBookRepo:
    """
    Mock repository for unit tests.

    This mock behaves like a real repository:
    - Stores books in memory
    - Supports CRUD operations
    - Allows assertions on state changes
    """

    def __init__(self, initial: list[Book] | None = None):
        self._books: list[Book] = list(initial) if initial else []

    def get_all_books(self) -> list[Book]:
        return list(self._books)

    def add_book(self, book: Book | list[Book]) -> str | list[str]:
        if isinstance(book, list):
            if not all(isinstance(b, Book) for b in book):
                raise TypeError("All items must be Book instances")
            self._books.extend(book)
            return [b.book_id for b in book]

        if not isinstance(book, Book):
            raise TypeError("book must be a Book instance")

        self._books.append(book)
        return book.book_id

    def find_book_by_name(self, query: str) -> list[Book]:
        q = query.lower()
        return [b for b in self._books if q in b.title.lower()]

    def delete_book(self, book_id: str) -> bool:
        for i, b in enumerate(self._books):
            if b.book_id == book_id:
                del self._books[i]
                return True
        return False

    def update_book(self, book_id: str, data: dict[str, Any]) -> bool:
        for b in self._books:
            if b.book_id == book_id:
                for k, v in data.items():
                    if hasattr(b, k):
                        setattr(b, k, v)
                return True
        return False
