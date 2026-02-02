from .services.book_generator_service_V2 import generate_books_json
from .services.book_generator_bad_data_service import generate_books as get_bad_books
from .domain.book import Book
from .services.book_service import BookService
from .services.book_analytics_services import BookAnalyticsService
from .repositories.book_repository import BookRepository
import requests

class BookREPL:
    def __init__(self, book_service, book_analytics_service):
        self.running = True
        self.book_service = book_service
        self.book_analytics_service = book_analytics_service

    def start(self):
        print("Welcome to the book app! Type 'Help' for a list of commands!")
        while self.running:
            cmd = input(">>>").strip()
            self.handle_command(cmd)

    def handle_command(self, cmd):
        if cmd == "exit":
            self.running = False
            print("Goodbye!")
        elif cmd == "getAllRecords":
            self.get_all_records()
        elif cmd == "addBook":
            self.add_book()
        elif cmd == "findByName":
            self.find_book_by_name()
        elif cmd == "getJoke":
            self.get_joke()
        elif cmd == "deleteBook":
            self.delete_book()
        elif cmd == "updateBook":
            self.update_book()
        elif cmd == 'getAveragePrice':
            self.get_average_price()
        elif cmd == 'getTopBooks':
            self.get_top_books()
        elif cmd == 'getValueScore':
            self.get_value_score()
        elif cmd == 'getMedianPriceByGenre':
            self.get_median_price_by_genre()
        elif cmd == 'getPopularityZscores':
            self.get_popularity_zscores()
        elif cmd == "help":
            print(
                "Available commands: addBook, getAllRecords, findByName, deleteBook, updateBook, getJoke, getAveragePrice, getTopBooks, getValueScore, getMedianPriceByGenre, getPopularityZscores, help, exit"
            )
        else:
            print("Please use a valid command!")

    def get_popularity_zscores(self):
        books = self.book_service.get_all_books()
        zscore = self.book_analytics_service.popularity_zscores(books)
        print(zscore)

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

    def get_joke(self):
        try:
            url = "https://api.chucknorris.io/jokes/random"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            print(response.json()["value"])
        except requests.exceptions.Timeout:
            print("The request timed out.")
        except requests.exceptions.RequestException as e:
            print(f"HTTP Error: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Something else went wrong: {e}")

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
