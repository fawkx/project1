from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import uuid

def _to_iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if dt else None

def _from_iso(s: Optional[str]) -> Optional[datetime]:
    return datetime.fromisoformat(s) if s else None

@dataclass
class CheckoutRecord:
    book_id: str
    user_id: Optional[str] = None
    checkout_at: datetime = field(default_factory=datetime.utcnow)
    returned_at: Optional[datetime] = None
    notes: Optional[str] = None
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def mark_returned(self, returned_at: Optional[datetime] = None) -> None:
        self.returned_at = returned_at or datetime.utcnow()

    def is_returned(self) -> bool:
        return self.returned_at is not None

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "book_id": self.book_id,
            "user_id": self.user_id,
            "checkout_at": _to_iso(self.checkout_at),
            "returned_at": _to_iso(self.returned_at),
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CheckoutRecord":
        return cls(
            book_id=data["book_id"],
            user_id=data.get("user_id"),
            checkout_at=_from_iso(data.get("checkout_at")) or datetime.utcnow(),
            returned_at=_from_iso(data.get("returned_at")),
            notes=data.get("notes"),
            record_id=data.get("record_id") or str(uuid.uuid4()),
        )