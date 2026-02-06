import json
from src.domain.book import Book
from src.repositories.book_repository_protocol import BookRepositoryProtocol


class BookRepository(BookRepositoryProtocol):
    """
    JSON-backed repository for Book persistence.

    Responsibilities:
    - Load books from a JSON file
    - Persist new or updated books to disk
    - Support basic CRUD operations

    This repository is intentionally simple and synchronous.
    Business logic and validation live in the service layer.
    """
    def __init__(self, filepath: str = "books.json"):
        self.filepath = filepath

    def get_all_books(self) -> list[Book]:
        """
        Load all books from disk.

        Returns:
            A list of Book domain objects.
        """
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Book.from_dict(item) for item in data]

    def add_book(self, book: Book | list[Book]) -> str | list[str]:
        """
        Add one or more books to storage.

        Supports both:
        - a single Book
        - a list of Book objects (bulk insert)

        Args:
            book: Book or list of Book instances.

        Returns:
            The book_id (str) for a single book,
            or a list of book_ids for bulk inserts.

        Raises:
            TypeError: if input is not Book or list[Book].
        """
        books = self.get_all_books()
        
        # Handle bulk insert
        if isinstance(book, list):
            for b in book:
                if not isinstance(b, Book):
                    raise TypeError("All items must be Book instances")
            books.extend(book)
            ids = [b.book_id for b in book]
        # Handle single insert
        else:
            if not isinstance(book, Book):
                raise TypeError("book must be a Book instance")
            books.append(book)
            ids = book.book_id

        # Persist updated list
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([b.to_dict() for b in books], f, indent=2)
        return ids

    def find_book_by_name(self, query) -> list[Book]:
        """
        Find books whose title contains the given query string
        (case-insensitive, partial match).

        Args:
            query: Title search string.

        Returns:
            List of matching Book objects.

        Raises:
            TypeError: if query is not a string.
        """
        if not isinstance(query, str):
            raise TypeError("query must be a string")
        q = query.strip().lower()
        books = self.get_all_books()
        return [b for b in books if q in (b.title or "").lower()]

    def delete_book(self, book_id: str) -> bool:
        """
        Delete a book by its unique book_id.

        Args:
            book_id: The ID of the book to delete.

        Returns:
            True if a book was deleted,
            False if no matching book was found.
        """
        books = self.get_all_books()
        filtered = [b for b in books if b.book_id != book_id]
        if len(filtered) == len(books):
            return False
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([b.to_dict() for b in filtered], f, indent=2)
        return True

    def update_book(self, book_id: str, data: dict) -> bool:
        """
        Update fields on an existing book.

        Only fields that already exist on the Book dataclass
        will be updated. The book_id itself cannot be changed.

        Args:
            book_id: ID of the book to update.
            data: Mapping of field -> new value.

        Returns:
            True if update succeeded,
            False if book was not found.

        Raises:
            TypeError: if data is not a dict.
        """
        if not isinstance(data, dict):
            raise TypeError("data must be a dict")

        books = self.get_all_books()
        updated = False
        for b in books:
            if b.book_id == book_id:
                for key, value in data.items():
                    if key == "book_id":
                        continue
                    if hasattr(b, key):
                        setattr(b, key, value)
                updated = True
                break
        if not updated:
            return False

        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([bb.to_dict() for bb in books], f, indent=2)
        return True
