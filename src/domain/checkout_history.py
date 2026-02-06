from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class CheckoutRecord:
    book_id: str
    action: str  # 'check_out' or 'check_in'
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @classmethod
    def from_dict(cls, data: dict) -> "CheckoutRecord":
        return cls(**data)

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "book_id": self.book_id,
            "action": self.action,
            "timestamp": self.timestamp,
        }
