from datetime import datetime
from typing import Optional

from src.domain.book import Book
from src.domain.checkout_history import CheckoutRecord
from src.repositories.book_repository_protocol import BookRepositoryProtocol
from src.repositories.checkout_history_repository_protocol import \
    CheckoutHistoryRepositoryProtocol


class BookService:
    def __init__(
        self,
        repo: BookRepositoryProtocol,
        history_repo: Optional[CheckoutHistoryRepositoryProtocol] = None,
    ):
        self.repo = repo
        self.history_repo = history_repo

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

    def check_out(self, book_id: str) -> bool:
        if not isinstance(book_id, str):
            raise TypeError("Expected str book_id")
        books = self.repo.get_all_books()
        found = None
        for b in books:
            if b.book_id == book_id:
                found = b
                break
        if not found:
            raise Exception("Book not found")
        # perform domain-level check
        found.check_out()
        found.last_checkout = datetime.utcnow().isoformat()
        # persist change
        self.repo.update_book(
            book_id,
            {"available": found.available, "last_checkout": found.last_checkout},
        )
        # record history if repository provided
        if self.history_repo:
            rec = CheckoutRecord(
                book_id=book_id, action="check_out", timestamp=found.last_checkout
            )
            self.history_repo.add_record(rec)
        return True

    def check_in(self, book_id: str) -> bool:
        if not isinstance(book_id, str):
            raise TypeError("Expected str book_id")
        books = self.repo.get_all_books()
        found = None
        for b in books:
            if b.book_id == book_id:
                found = b
                break
        if not found:
            raise Exception("Book not found")
        found.check_in()
        # persist change (no timestamp update on check-in)
        self.repo.update_book(book_id, {"available": found.available})
        if self.history_repo:
            rec = CheckoutRecord(
                book_id=book_id,
                action="check_in",
                timestamp=datetime.utcnow().isoformat(),
            )
            self.history_repo.add_record(rec)
        return True
    
    def build_books_from_input(self, title_input: str, author_input: str) -> list[Book]:
        """
        Convert raw title/author strings into one or more Book objects.
        Supports comma-separated titles/authors.

        Returns: list[Book] (possibly empty if title_input is blank)
        """
        if not isinstance(title_input, str) or not isinstance(author_input, str):
            raise TypeError("title_input and author_input must be strings")

        titles = [t.strip() for t in title_input.split(",")] if "," in title_input else [title_input.strip()]
        authors = [a.strip() for a in author_input.split(",")] if "," in author_input else [author_input.strip()]

        # remove empty entries
        titles = [t for t in titles if t]
        authors = [a for a in authors if a]

        if not titles:
            return []

        # allow blank author -> empty string
        if not authors:
            authors = [""]

        max_len = max(len(titles), len(authors))
        result: list[Book] = []

        for i in range(max_len):
            t = titles[i] if i < len(titles) else titles[-1]
            a = authors[i] if i < len(authors) else authors[-1]
            result.append(Book(title=t, author=a))
        return result
