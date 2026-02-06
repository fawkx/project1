import json
from typing import List

from src.domain.checkout_history import CheckoutRecord
from src.repositories.checkout_history_repository_protocol import \
    CheckoutHistoryRepositoryProtocol


class CheckoutHistoryRepository(CheckoutHistoryRepositoryProtocol):
    def __init__(self, filepath: str = "checkout_history.json"):
        self.filepath = filepath

    def _read_all(self) -> List[CheckoutRecord]:
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [CheckoutRecord.from_dict(d) for d in data]
        except FileNotFoundError:
            return []

    def get_all_records(self) -> List[CheckoutRecord]:
        return self._read_all()

    def add_record(self, record: CheckoutRecord) -> str:
        if not isinstance(record, CheckoutRecord):
            raise TypeError("record must be a CheckoutRecord")
        records = self._read_all()
        records.append(record)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([r.to_dict() for r in records], f, indent=2)
        return record.record_id

    def find_by_book_id(self, book_id: str) -> List[CheckoutRecord]:
        return [r for r in self._read_all() if r.book_id == book_id]
