from datetime import datetime
from typing import Optional

from src.domain.book import Book
from src.domain.checkout_history import CheckoutRecord
from src.repositories.book_repository_protocol import BookRepositoryProtocol
from src.repositories.checkout_history_repository_protocol import CheckoutHistoryRepositoryProtocol


class BookService:
    """
    Service layer responsible for business logic around books.

    Responsibilities:
    - Validate inputs before delegating to repositories
    - Coordinate domain behavior (check-in / check-out)
    - Optionally record checkout history
    - Act as a boundary between the REPL and repositories
    """
    def __init__(
        self,
        repo: BookRepositoryProtocol,
        history_repo: Optional[CheckoutHistoryRepositoryProtocol] = None,
    ):
        self.repo = repo
        self.history_repo = history_repo

    def get_all_books(self) -> list[Book]:
        """
        Retrieve all books from the repository.

        No business logic is applied here; this is a direct pass-through.
        """
        return self.repo.get_all_books()

    def add_book(self, book: Book | list[Book]) -> str | list[str]:
        """
        Add one or more Book objects to the repository.

        Performs type validation before delegating persistence.
        Returns generated book_id(s).
        """
        if isinstance(book, list):
            if not all(isinstance(b, Book) for b in book):
                raise TypeError("All items must be Book instances")
        else:
            if not isinstance(book, Book):
                raise TypeError("book must be a Book instance")
        return self.repo.add_book(book)

    def find_book_by_name(self, query) -> list[Book]:
        """
        Search for books by title.

        Type validation is enforced here to keep repository logic simple.
        """
        if not isinstance(query, str):
            raise TypeError("Expected str, got something else")
        return self.repo.find_book_by_name(query)

    def delete_book(self, book_id: str) -> bool:
        """
        Remove a book from the repository by its unique ID.
        """
        if not isinstance(book_id, str):
            raise TypeError("Expected str book_id")
        return self.repo.delete_book(book_id)

    def update_book(self, book_id: str, data: dict) -> bool:
        """
        Update one or more fields of a book.

        The data dictionary contains field -> new value mappings.
        """
        if not isinstance(book_id, str):
            raise TypeError("Expected str book_id")
        if not isinstance(data, dict):
            raise TypeError("Expected dict for data")
        return self.repo.update_book(book_id, data)

    def check_out(self, book_id: str) -> bool:
        """
        Check out a book.

        Steps:
        - Locate the book
        - Apply domain rule (cannot check out twice)
        - Update availability and timestamp
        - Persist changes
        - Record checkout history if enabled
        """
        if not isinstance(book_id, str):
            raise TypeError("Expected str book_id")
        
        books = self.repo.get_all_books()
        found = None

        # Locate book in current collection
        for b in books:
            if b.book_id == book_id:
                found = b
                break
        if not found:
            raise Exception("Book not found")
        
       # Domain-level validation
        found.check_out()
        found.last_checkout = datetime.utcnow().isoformat()

        # Persist state change
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
        """
        Check in a book and mark it as available.

        Unlike checkout, no timestamp update is required.
        """
        if not isinstance(book_id, str):
            raise TypeError("Expected str book_id")
        
        books = self.repo.get_all_books()
        found = None

        # Locate book in current collection
        for b in books:
            if b.book_id == book_id:
                found = b
                break

        if not found:
            raise Exception("Book not found")
        
        # Domain-level validation
        found.check_in()

        # Persist availability change
        self.repo.update_book(book_id, {"available": found.available})

        # record history if repository provided
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

        # Remove empty entries
        titles = [t for t in titles if t]
        authors = [a for a in authors if a]

        # No valid titles means nothing to add
        if not titles:
            return []

        # Allow empty author values
        if not authors:
            authors = [""]

        max_len = max(len(titles), len(authors))
        result: list[Book] = []

        # Pair titles/authors, repeating last value if lengths differ
        for i in range(max_len):
            t = titles[i] if i < len(titles) else titles[-1]
            a = authors[i] if i < len(authors) else authors[-1]
            result.append(Book(title=t, author=a))
        return result
