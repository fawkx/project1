import pytest
import src.services.book_service as book_service
from tests.mocks.mock_book__repository import MockBookRepo


def test_get_all_books_positive():
    # AAA - Arrange, Act, Assert
    repo = MockBookRepo()
    svc = book_service.BookService(repo)
    books = svc.get_all_books()
    assert len(books) == 1


def test_find_book_by_name_negative():
    name = 3
    repo = MockBookRepo()
    svc = book_service.BookService(repo)

    with pytest.raises(TypeError) as e:
        book = svc.find_book_by_name(name)
    assert str(e.value) == "Expected str, got something else"


def test_delete_book_positive():
    repo = MockBookRepo()
    svc = book_service.BookService(repo)
    result = svc.delete_book("any-id")
    assert result is True


def test_delete_book_negative():
    repo = MockBookRepo()
    svc = book_service.BookService(repo)
    with pytest.raises(TypeError):
        svc.delete_book(123)


def test_update_book_positive():
    repo = MockBookRepo()
    svc = book_service.BookService(repo)
    result = svc.update_book("any-id", {"title": "new title"})
    assert result is True


def test_update_book_negative_types():
    repo = MockBookRepo()
    svc = book_service.BookService(repo)
    with pytest.raises(TypeError):
        svc.update_book(123, {"title": "new"})
    with pytest.raises(TypeError):
        svc.update_book("id", "not-a-dict")


def test_add_multiple_books_with_mock():
    from src.domain.book import Book

    repo = MockBookRepo()
    svc = book_service.BookService(repo)

    b1 = Book(title="A", author="Auth A")
    b2 = Book(title="B", author="Auth B")

    ids = svc.add_book([b1, b2])
    assert isinstance(ids, list)
    assert len(ids) == 2
    assert all(isinstance(i, str) for i in ids)


def test_add_multiple_books_integration(tmp_path):
    import json
    from src.domain.book import Book
    from src.repositories.book_repository import BookRepository
    from src.services.book_service import BookService

    file = tmp_path / "books.json"
    file.write_text("[]", encoding="utf-8")

    repo = BookRepository(str(file))
    svc = BookService(repo)

    b1 = Book(title="A", author="Auth A")
    b2 = Book(title="B", author="Auth B")

    ids = svc.add_book([b1, b2])
    assert isinstance(ids, list) and len(ids) == 2

    data = json.loads(file.read_text(encoding="utf-8"))
    assert any(item["title"] == "A" for item in data)
    assert any(item["title"] == "B" for item in data)
