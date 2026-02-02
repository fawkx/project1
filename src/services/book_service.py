from src.repositories.book_repository_protocol import BookRepositoryProtocol
from src.domain.book import Book


class BookService:
    def __init__(self, repo: BookRepositoryProtocol):
        self.repo = repo

    def get_all_books(self) -> list[Book]:
        return self.repo.get_all_books()

    def add_book(self, book: Book | list[Book]) -> str | list[str]:
        if isinstance(book, list):
            if not all(isinstance(b, Book) for b in book):
                raise TypeError("All items must be Book instances")
        else:
            if not isinstance(book, Book):
                raise TypeError("book must be a Book instance")
        return self.repo.add_book(book)

    def find_book_by_name(self, query) -> list[Book]:
        if not isinstance(query, str):
            raise TypeError("Expected str, got something else")
        return self.repo.find_book_by_name(query)

    def delete_book(self, book_id: str) -> bool:
        if not isinstance(book_id, str):
            raise TypeError("Expected str book_id")
        return self.repo.delete_book(book_id)

    def update_book(self, book_id: str, data: dict) -> bool:
        if not isinstance(book_id, str):
            raise TypeError("Expected str book_id")
        if not isinstance(data, dict):
            raise TypeError("Expected dict for data")
        return self.repo.update_book(book_id, data)
