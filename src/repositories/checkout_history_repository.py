import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from src.domain.checkout_history import CheckoutRecord


class CheckoutHistoryRepository:
    def __init__(self, filepath: str = "checkout_history.json"):
        self.filepath = Path(filepath)

    def _load(self) -> List[dict]:
        if not self.filepath.exists():
            return []
        with self.filepath.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, records: List[dict]) -> None:
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with self.filepath.open("w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

    def get_all_records(self) -> List[CheckoutRecord]:
        data = self._load()
        return [CheckoutRecord.from_dict(d) for d in data]

    def add_record(self, record: CheckoutRecord | List[CheckoutRecord]) -> str | List[str]:
        records = self.get_all_records()
        if isinstance(record, list):
            if not all(isinstance(r, CheckoutRecord) for r in record):
                raise TypeError("All items must be CheckoutRecord instances")
            records.extend(record)
            ids = [r.record_id for r in record]
        else:
            if not isinstance(record, CheckoutRecord):
                raise TypeError("record must be a CheckoutRecord instance")
            records.append(record)
            ids = record.record_id

        self._save([r.to_dict() for r in records])
        return ids

    def find_by_book_id(self, book_id: str) -> List[CheckoutRecord]:
        if not isinstance(book_id, str):
            raise TypeError("book_id must be a string")
        return [r for r in self.get_all_records() if r.book_id == book_id]

    def find_by_record_id(self, record_id: str) -> Optional[CheckoutRecord]:
        for r in self.get_all_records():
            if r.record_id == record_id:
                return r
        return None

    def delete_record(self, record_id: str) -> bool:
        records = self.get_all_records()
        filtered = [r for r in records if r.record_id != record_id]
        if len(filtered) == len(records):
            return False
        self._save([r.to_dict() for r in filtered])
        return True

    def update_record(self, record_id: str, data: dict) -> bool:
        if not isinstance(data, dict):
            raise TypeError("data must be a dict")

        raw = self._load()  # list of dicts from disk
        updated = False
        for d in raw:
            if d.get("record_id") == record_id:
                for k, v in data.items():
                    if k == "record_id":
                        continue
                    # convert datetime to iso string for JSON storage
                    if isinstance(v, datetime):
                        d[k] = v.isoformat()
                    else:
                        d[k] = v
                updated = True
                break

        if not updated:
            return False

        self._save(raw)
        return True