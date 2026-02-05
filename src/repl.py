from datetime import datetime
from src.services.book_generator_service_V2 import generate_books_json
from src.services.book_generator_bad_data_service import generate_books as get_bad_books
from src.domain.book import Book
from src.domain.checkout_history import CheckoutRecord
from src.services.book_service import BookService
from src.services.book_analytics_services import BookAnalyticsService
from src.repositories.book_repository import BookRepository
from src.repositories.checkout_history_repository import CheckoutHistoryRepository


class BookREPL:
    def __init__(self, book_service, book_analytics_service):
        self.running = True
        self.book_service = book_service
        self.book_analytics_service = book_analytics_service

    def start(self):
        print("Welcome to the book app!")
        while self.running:
            self.print_main_menu()
            cmd = input(">>>").strip()
            self.handle_command(cmd)

    def handle_command(self, cmd):
        if cmd == "1":
            self.get_all_records()
        elif cmd == "2":
            self.check_in_out()
        elif cmd == "3":
            self.add_book()
        elif cmd == "4":
            self.delete_book()
        elif cmd == "5":
            self.update_book()
        elif cmd == "6":
            self.find_book_by_name()
        elif cmd == "7":
            self.analytics()
        elif cmd == "8":
            self.running = False
            print("Goodbye!")
        else:
            print("Please use a valid command!")
    
    def analytics(self):
        while True:
            self.print_analytics_menu()
            cmd = input(">>> ").strip().lower()
            if cmd == "1":
                self.get_average_price()
            elif cmd == "2":
                self.get_top_books()
            elif cmd == "3":
                self.get_value_score()
            elif cmd == "4":
                self.get_median_price_by_genre()
            elif cmd == "5":
                self.most_popular_genre()
            elif cmd == "6":
                self.print_main_menu()
                break
            else:("Please select a valid analytics command!")

    def print_main_menu(self):
        print(
            "All commands\n"
            "1. Print All Records  2. Check in/out  3. Add Book\n"
            "4. Remove Book        5. Update Book   6. Find By Name\n"
            "7. Analytics Menu     8. Exit\n"
        )
    
    def print_analytics_menu(self):
        print(
            "All Analytics Services\n"
            "1. Average Price\n"
            "2. Top Books\n"  
            "3. Value Scores\n"
            "4. Avg Price by Genre\n"  
            "5. Most Popular Genre\n"
            "6. Back to Main Menu\n"
        )

    def check_in_out(self):
        repo = CheckoutHistoryRepository("checkout_history.json")

        book_id = input("Enter book ID to check out/in: ").strip()
        if not book_id:
            print("No book ID provided.")
            return

        books = self.book_service.get_all_books()
        book = next((b for b in books if getattr(b, "book_id", None) == book_id), None)
        if not book:
            print("No book found with that ID."); return

        currently_available = True if getattr(book, "available", None) is None else bool(book.available)

        try:
            if currently_available:
                user_id = input("User id (optional): ").strip() or None
                self.book_service.update_book(book.book_id, {"available": False})
                record = CheckoutRecord(book_id=book.book_id, user_id=user_id, checkout_at=datetime.utcnow())
                repo.add_record(record)
                print(f"Book {book.book_id} checked out (record {record.record_id}).")
            else:
                self.book_service.update_book(book.book_id, {"available": True})
                raw = repo.find_by_book_id(book.book_id)  # may be CheckoutRecord or dict
                # normalize to CheckoutRecord
                records = [r if isinstance(r, CheckoutRecord) else CheckoutRecord.from_dict(r) for r in raw]
                open_records = [r for r in records if not r.is_returned()]
                if not open_records:
                    print("Book checked in, but no open checkout record found."); return
                latest = max(open_records, key=lambda r: r.checkout_at)
                latest.mark_returned()
                repo.update_record(latest.record_id, {"returned_at": latest.returned_at})
                print(f"Book {book.book_id} checked in (record {latest.record_id} updated).")
        except Exception as e:
            print(f"Error during check in/out: {e}")

    def most_popular_genre(self):
        pass

    def get_median_price_by_genre(self):
        books = self.book_service.get_all_books()
        median = self.book_analytics_service.median_price_by_genre(books)
        print(median)

    def get_average_price(self):
        books = self.book_service.get_all_books()
        avg_price = self.book_analytics_service.average_price(books)
        print(avg_price)

    def get_top_books(self):
        books = self.book_service.get_all_books()
        top_rated_books = self.book_analytics_service.top_rated_with_pandas(books)
        print(top_rated_books)

    def get_value_score(self):
        books = self.book_service.get_all_books()
        value_scores = self.book_analytics_service.value_scores_with_pandas(books)
        print(value_scores)

    def get_all_records(self):
        books = self.book_service.get_all_books()
        print(books)

    def add_book(self):
        try:
            print("Enter book details:")
            title = input("Title: ")
            if title == "":
                print("No books added.")
                return
            author = input("Author: ")

            titles = [t.strip() for t in title.split(",")] if "," in title else [title]
            authors = (
                [a.strip() for a in author.split(",")] if "," in author else [author]
            )

            max_len = max(len(titles), len(authors))
            to_add = []
            for i in range(max_len):
                t = titles[i] if i < len(titles) else titles[-1]
                a = authors[i] if i < len(authors) else authors[-1]
                to_add.append(Book(title=t, author=a))

            payload = to_add if len(to_add) > 1 else to_add[0]
            self.book_service.add_book(payload)

            if isinstance(to_add, list) and len(to_add) > 1:
                print("Books added:")
                for b in to_add:
                    print(f"- {b.title} by {b.author}")
            else:
                b = to_add[0]
                print(f"Book added: {b.title} by {b.author}")
        except Exception as e:
            print(f"Error adding book: {e}")

    def find_book_by_name(self):
        query = input("Enter book title to search: ")
        books = self.book_service.find_book_by_name(query)
        print(books)

    def delete_book(self):
        try:
            book_id = input("Enter book ID to delete: ")
            result = self.book_service.delete_book(book_id)
            if result:
                print(f"Book {book_id} deleted.")
            else:
                print("No book found with that ID.")
        except Exception as e:
            print(f"Error deleting book: {e}")

    def update_book(self):
        try:
            book_id = input("Enter book ID to update: ")
            if book_id == "":
                print("No book ID provided.")
                return

            print("Enter fields to update. Leave field name empty to finish.")
            data = {}
            while True:
                key = input("Field name (e.g., title): ")
                if key == "":
                    break
                value = input(f"New value for {key}: ")
                data[key] = value

            if not data:
                print("No updates provided.")
                return

            result = self.book_service.update_book(book_id, data)
            if result:
                print(f"Book {book_id} updated.")
            else:
                print("No book found with that ID.")
        except Exception as e:
            print(f"Error updating book: {e}")


if __name__ == "__main__":
    generate_books_json()
    get_bad_books()
    repo = BookRepository("books.json")
    book_svc = BookService(repo)
    book_analytics_svc = BookAnalyticsService()
    repl = BookREPL(book_svc, book_analytics_svc)
    repl.start()
