from src.domain.book import Book


class MockBookRepo:
    def get_all_books(self):
        return [Book(title="test", author="author")]

    def add_book(self, book):
        if isinstance(book, list):
            if not all(isinstance(b, Book) for b in book):
                raise TypeError("All items must be Book instances")
            return ["mock_id" for _ in book]
        if not isinstance(book, Book):
            raise TypeError("book must be a Book instance")
        return "mock_id"

    def find_book_by_name(self, query):
        return [Book(title="test", author="author")]

    def delete_book(self, book_id: str) -> bool:
        if not isinstance(book_id, str):
            raise TypeError("Expected str book_id")
        return True

    def update_book(self, book_id: str, data: dict) -> bool:
        if not isinstance(book_id, str):
            raise TypeError("Expected str book_id")
        if not isinstance(data, dict):
            raise TypeError("Expected dict data")
        return True
