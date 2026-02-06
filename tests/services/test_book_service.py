import json
import pytest

from src.domain.book import Book
from src.repositories.book_repository import BookRepository
from src.services.book_service import BookService
from tests.mocks.mock_book__repository import MockBookRepo

import json

from src.domain.book import Book
from src.repositories.book_repository import BookRepository
from src.services.book_service import BookService


# -------------------------
# Test for CRUD
# -------------------------
# - Create persists to JSON
# - Read/search works via repository
# - Update persists to JSON
# - Delete persists to JSON


def test_create_book_integration(tmp_path):
    """C: Create a book and verify it is persisted to the JSON file."""
    file = tmp_path / "books.json"
    file.write_text("[]", encoding="utf-8")

    repo = BookRepository(str(file))
    svc = BookService(repo)

    book = Book(title="Solo", author="One Author")
    book_id = svc.add_book(book)

    assert isinstance(book_id, str)

    data = json.loads(file.read_text(encoding="utf-8"))
    assert any(item["book_id"] == book_id for item in data)


def test_read_find_book_by_name_integration(tmp_path):
    """R: Search by title and confirm the correct book is returned."""
    file = tmp_path / "books.json"
    file.write_text("[]", encoding="utf-8")

    repo = BookRepository(str(file))
    svc = BookService(repo)

    svc.add_book(Book(title="Dune", author="Frank Herbert"))
    svc.add_book(Book(title="Neuromancer", author="William Gibson"))

    found = svc.find_book_by_name("Dune")
    assert isinstance(found, list)
    assert any(b.title == "Dune" for b in found)


def test_update_book_integration(tmp_path):
    """U: Update a book and verify the change is persisted to the JSON file."""
    file = tmp_path / "books.json"
    file.write_text("[]", encoding="utf-8")

    repo = BookRepository(str(file))
    svc = BookService(repo)

    book = Book(title="Old", author="Author")
    book_id = svc.add_book(book)

    ok = svc.update_book(book_id, {"title": "New"})
    assert ok is True

    data = json.loads(file.read_text(encoding="utf-8"))
    updated = next(item for item in data if item["book_id"] == book_id)
    assert updated["title"] == "New"


def test_delete_book_integration(tmp_path):
    """D: Delete a book and verify it is removed from the JSON file."""
    file = tmp_path / "books.json"
    file.write_text("[]", encoding="utf-8")

    repo = BookRepository(str(file))
    svc = BookService(repo)

    book = Book(title="To Delete", author="Author")
    book_id = svc.add_book(book)

    ok = svc.delete_book(book_id)
    assert ok is True

    data = json.loads(file.read_text(encoding="utf-8"))
    assert all(item["book_id"] != book_id for item in data)
