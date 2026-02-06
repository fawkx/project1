from typing import List, Protocol

from src.domain.checkout_history import CheckoutRecord


class CheckoutHistoryRepositoryProtocol(Protocol):
	def get_all_records(self) -> List[CheckoutRecord]:
		...

	def add_record(self, record: CheckoutRecord) -> str:
		...

	def find_by_book_id(self, book_id: str) -> List[CheckoutRecord]:
		...

