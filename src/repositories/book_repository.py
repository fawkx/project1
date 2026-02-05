import json
from src.domain.book import Book
from .book_repository_protocol import BookRepositoryProtocol


class BookRepository(BookRepositoryProtocol):
    def __init__(self, filepath: str = "books.json"):
        self.filepath = filepath

    def get_all_books(self) -> list[Book]:
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Book.from_dict(item) for item in data]

    def add_book(self, book: Book | list[Book]) -> str | list[str]:
        books = self.get_all_books()
        # support adding a single Book or a list of Book
        if isinstance(book, list):
            for b in book:
                if not isinstance(b, Book):
                    raise TypeError("All items must be Book instances")
            books.extend(book)
            ids = [b.book_id for b in book]
        else:
            if not isinstance(book, Book):
                raise TypeError("book must be a Book instance")
            books.append(book)
            ids = book.book_id

        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([b.to_dict() for b in books], f, indent=2)
        return ids

    def find_book_by_name(self, query) -> list[Book]:
        if not isinstance(query, str):
            raise TypeError("query must be a string")
        q = query.strip().lower()
        books = self.get_all_books()
        return [b for b in books if q in (b.title or "").lower()]

    def delete_book(self, book_id: str) -> bool:
        """Delete a book by its book_id. Returns True if a book was deleted, False otherwise."""
        books = self.get_all_books()
        filtered = [b for b in books if b.book_id != book_id]
        if len(filtered) == len(books):
            return False
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([b.to_dict() for b in filtered], f, indent=2)
        return True

    def update_book(self, book_id: str, data: dict) -> bool:
        """Update fields of a book identified by book_id using keys in `data`.
        Returns True if updated, False if book not found.
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
