import json
from typing import List

from src.domain.checkout_history import CheckoutRecord
from src.repositories.checkout_history_repository_protocol import \
    CheckoutHistoryRepositoryProtocol


class CheckoutHistoryRepository(CheckoutHistoryRepositoryProtocol):
    """
    JSON-backed repository for checkout/check-in history records.

    Responsibilities:
    - Persist checkout/check-in events to disk
    - Load records from a JSON file
    - Provide simple query access by book_id

    This repository is append-only:
    records are never updated or deleted, only added.
    """
    def __init__(self, filepath: str = "checkout_history.json"):
        self.filepath = filepath

    def _read_all(self) -> List[CheckoutRecord]:
        """
        Internal helper to load all checkout records from disk.

        Returns:
            List of CheckoutRecord objects.
            Returns an empty list if the file does not exist.
        """
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [CheckoutRecord.from_dict(d) for d in data]
        except FileNotFoundError:
            return []

    def get_all_records(self) -> List[CheckoutRecord]:
        """
        Retrieve the complete checkout history.

        Returns:
            List of CheckoutRecord objects, ordered by insertion time.
        """
        return self._read_all()

    def add_record(self, record: CheckoutRecord) -> str:
        """
        Append a new checkout/check-in record to history.

        Args:
            record: CheckoutRecord instance representing a single event.

        Returns:
            The unique record_id of the newly added record.

        Raises:
            TypeError: if record is not a CheckoutRecord instance.
        """
        if not isinstance(record, CheckoutRecord):
            raise TypeError("record must be a CheckoutRecord")
        records = self._read_all()
        records.append(record)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([r.to_dict() for r in records], f, indent=2)
        return record.record_id

    def find_by_book_id(self, book_id: str) -> List[CheckoutRecord]:
        """
        Retrieve all checkout/check-in records for a specific book.

        Args:
            book_id: The unique ID of the book.

        Returns:
            List of CheckoutRecord objects associated with the given book.
        """
        return [r for r in self._read_all() if r.book_id == book_id]
