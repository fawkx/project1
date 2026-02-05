from typing import Protocol, Optional
from src.domain.checkout_history import CheckoutRecord


class CheckoutHistoryRepositoryProtocol(Protocol):
    def get_all_records(self) -> list[CheckoutRecord]: ...

    def add_record(self, record: CheckoutRecord | list[CheckoutRecord]) -> str | list[str]: 
        ...

    def find_by_book_id(self, book_id: str) -> list[CheckoutRecord]: 
        ...

    def find_by_record_id(self, record_id: str) -> Optional[CheckoutRecord]: 
        ...

    def delete_record(self, record_id: str) -> bool: 
        ...

    def update_record(self, record_id: str, data: dict) -> bool: 
        ...