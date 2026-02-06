import webbrowser
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

from src.services.book_generator_service_V2 import generate_books_json
from src.domain.book import Book
from src.domain.checkout_history import CheckoutRecord
from src.services.book_service import BookService
from src.services.book_analytics_services import BookAnalyticsService
from src.repositories.book_repository import BookRepository
from src.repositories.checkout_history_repository import CheckoutHistoryRepository


class BookREPL:
    """
    BookREPL is the application layer
    
    Responsibilities:
        - Handle user input and menu navigation (REPL loop)
        - Call service -layer methods for CRUD and checkout operations
        - Display results and generate visualizations (matplotlib)

    Business logic lives in BookService
    Analytics calculations live in BookAnalyicsService
    This class handles I/O and presentation only
    """
    def __init__(self, book_service, book_analytics_service):
        self.running = True
        self.book_service = book_service
        self.book_analytics_service = book_analytics_service

    def start(self):
        """
        Start the main REPL loop.
        Continues until the user selects Exit.
        """
        print("Welcome to the book app!")
        while self.running:
            self.print_main_menu()
            cmd = input(">>> ").strip()
            self.handle_command(cmd)

    def handle_command(self, cmd):
        """
        Dispatch main-menu commands to the appropriate handler.
        This keeps start() simple and avoids long logic blocks.
        """
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
        """
        Secondary loop for analytics features.
        User remains in this menu until selecting '0' to return.
        """
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
                self.highest_rated_genres()
            elif cmd == "7":
                self.price_vs_rating()
            elif cmd == "8":
                self.books_released_by_year_chart()
            elif cmd == "9":
                self.availability_pie_chart()
            elif cmd == '0':    
                self.print_main_menu()
                break
            else:
                print("Please select a valid analytics command!")

    def print_main_menu(self):
        """Print the main application menu."""
        print(
            "All commands\n"
            "1. Print All Records  2. Check in/out  3. Add Book\n"
            "4. Remove Book        5. Update Book   6. Find By Name\n"
            "7. Analytics Menu     8. Exit\n"
        )

    def print_analytics_menu(self):
        """Print the analytics menu."""
        print(
            "All Analytics Services\n"
            "1. Average Price\n"
            "2. Top Books\n"
            "3. Value Scores\n"
            "4. Avg Price by Genre\n"
            "5. Most Popular Genre\n"
            "6. Highest Rated Genres\n"
            "7. Price vs Rating\n"
            "8. Books Released by Year\n"
            "9. Availability\n"
            "0. Back to Main Menu\n"
        )

    def check_in_out(self):
        """
        Checkout/check-in flow.

        Steps:
        - Display all books and current availability
        - Ask user for book_id and action ('out' or 'in')
        - Delegate the actual operation to BookService
        (service updates repo and writes to checkout history if enabled)
        """
        try:
            books = self.book_service.get_all_books()
            if not books:
                print("No books available.")
                return
            print("Books:")
            for b in books:
                print(f"- {b.book_id}: {b.title} (available={b.available})")
            book_id = input("Enter book ID to check in/out: ").strip()
            if book_id == "":
                print("No book ID provided.")
                return
            action = (
                input("Type 'out' to check out or 'in' to check in: ").strip().lower()
            )
            if action not in ("out", "in"):
                print("Invalid action.")
                return
            if action == "out":
                self.book_service.check_out(book_id)
                print(f"Book {book_id} checked out.")
            else:
                self.book_service.check_in(book_id)
                print(f"Book {book_id} checked in.")
        except Exception as e:
            print(f"Error checking in/out: {e}")

    def most_popular_genre(self):
        """
        Display a bar chart showing the number of books per genre.
        Uses precomputed genre counts from BookAnalyticsService.
        """
        try:
            books = self.book_service.get_all_books()
            if not books:
                print("No books available.")
                return

            # Get genre frequency data
            counts = self.book_analytics_service.most_common_genres(books)
            if not counts:
                print("No genre data available.")
                return

            # Print raw data for transparency
            print("Genre counts:")
            for genre, count in counts.items():
                print(f"- {genre}: {count}")

            # Prepare chart data
            genres = list(counts.keys())
            values = list(counts.values())

            # Create bar chart
            plt.figure(figsize=(10, 6))
            plt.bar(genres, values)
            plt.xticks(rotation=45, ha="right")
            plt.ylabel("Count")
            plt.title("Most Popular Genres")
            plt.tight_layout()

            # Save chart
            filename = "genre_counts.png"
            plt.savefig(filename, dpi=200, bbox_inches="tight")
            plt.close()

            # Open image automatically
            if os.name == "nt":
                os.startfile(filename)
            else:
                try:
                    webbrowser.open(filename)
                except Exception:
                    pass

            print(f"Genre chart saved to {filename}")

        except Exception as e:
            print(f"Error generating genre chart: {e}")
    
    def highest_rated_genres(self, m: int = 80):
        """
        Create a bar chart ranking genres by Bayesian weighted rating.
        """
        try:
            books = self.book_service.get_all_books()
            if not books:
                print("No books available.")
                return

            scores = self.book_analytics_service.bayesian_weighted_rating_by_genre(books, m=m)
            if not scores:
                print("No rating data available to compute Bayesian genre ratings.")
                return

            print(f"Bayesian weighted rating by genre (m={m}):")
            for g, s in scores.items():
                print(f"- {g}: {s:.3f}")

            genres = list(scores.keys())
            values = list(scores.values())

            plt.figure(figsize=(10, 6))
            plt.bar(genres, values)
            plt.xticks(rotation=45, ha="right")
            plt.ylabel("Bayesian Weighted Rating")
            plt.title(f"Genres Rated Highest (Bayesian Avg, m={m})")
            plt.tight_layout()

            filename = "genre_bayesian_ratings.png"
            plt.savefig(filename, dpi=200, bbox_inches="tight")
            plt.close()

            if os.name == "nt":
                os.startfile(filename)
            else:
                try:
                    webbrowser.open(filename)
                except Exception:
                    pass

            print(f"Saved chart to {filename}")

        except Exception as e:
            print(f"Error generating Bayesian genre chart: {e}")
    
    def price_vs_rating(self):
        """
        Scatter plot to visualize the relationship between
        book price and average rating.
        """
        try:
            books = self.book_service.get_all_books()

            # Delegate data extraction to analytics service
            prices, ratings = self.book_analytics_service.price_vs_rating_points(books)

            if not prices:
                print("No valid price/rating data.")
                return

            plt.figure(figsize=(8, 6))
            plt.scatter(prices, ratings, alpha=0.6)
            plt.xlabel("Price (USD)")
            plt.ylabel("Average Rating")
            plt.title(f"Price vs Rating")
            plt.tight_layout()

            filename = "price_vs_rating.png"
            plt.savefig(filename, dpi=200, bbox_inches="tight")
            plt.close()

            if os.name == "nt":
                os.startfile(filename)

            print(f"Saved scatter plot to {filename}")

        except Exception as e:
            print(f"Error generating scatter plot: {e}")

    def books_released_by_year_chart(self):
        """
        Generate a line chart showing how many books were released per year.

        The analytics service returns a mapping of year ->, and this method handles the plotting
        and saving the image.
        """
        try:
            books = self.book_service.get_all_books()
            if not books:
                print("No books available.")
                return

            counts = self.book_analytics_service.books_released_by_year(books)
            if not counts:
                print("No publication year data available.")
                return

            # Sort by year(left to right)
            years = sorted(counts.keys())
            values = [counts[y] for y in years]

            plt.figure(figsize=(10, 6))
            plt.plot(years, values, marker="o")
            plt.xlabel("Publication Year")
            plt.ylabel("Number of Books Released")
            plt.title("Books Released by Year")
            plt.tight_layout()

            filename = "books_released_by_year.png"
            plt.savefig(filename, dpi=200, bbox_inches="tight")
            plt.close()

            if os.name == "nt":
                os.startfile(filename)

            print(f"Saved line chart to {filename}")

        except Exception as e:
            print(f"Error generating books-by-year chart: {e}")

    def availability_pie_chart(self): 
        """
        Pie chart showing checked-out vs available books.
        Represents current state, not historical usage.
        """
        try:
            books = self.book_service.get_all_books()
            if not books:
                print("No books available.")
                return

            counts = self.book_analytics_service.availability_counts(books)
            if sum(counts.values()) == 0:
                print("No availability data.")
                return

            labels = list(counts.keys())
            sizes = list(counts.values())

            plt.figure(figsize=(6, 6))
            plt.pie(
                sizes,
                labels=labels,
                autopct="%1.1f%%",
                startangle=90
            )
            plt.title("Book Availability Status")
            plt.tight_layout()

            filename = "availability_pie_chart.png"
            plt.savefig(filename, dpi=200, bbox_inches="tight")
            plt.close()

            if os.name == "nt":
                os.startfile(filename)

            print(f"Saved pie chart to {filename}")

        except Exception as e:
            print(f"Error generating availability pie chart: {e}")

    def get_median_price_by_genre(self):
        """
        Display the median book price grouped by genre.
        Delegates aggregation logic to BookAnalyticsService
        and prints the resulting mapping.
        """
        books = self.book_service.get_all_books()
        median = self.book_analytics_service.median_price_by_genre(books)
        print(median)

    def get_average_price(self):
        """
        Compute and display the average price of all books
        using the analytics service.
        """
        books = self.book_service.get_all_books()
        avg_price = self.book_analytics_service.average_price(books)
        print(avg_price)

    def get_top_books(self):
        """
        Display the highest-rated books that meet a minimum
        ratings threshold.
        Uses pandas-based analytics for sorting and filtering.
        """
        books = self.book_service.get_all_books()
        top_rated_books = self.book_analytics_service.top_rated_with_pandas(books)
        print(top_rated_books)

    def get_value_score(self):
        """
        Display value scores for books based on rating,
        ratings count, and price.
        Higher score indicates better value.
        """
        books = self.book_service.get_all_books()
        value_scores = self.book_analytics_service.value_scores_with_pandas(books)
        print(value_scores)

    def get_all_records(self):
        """
        Retrieve and display all books currently stored
        in the repository.
        """
        books = self.book_service.get_all_books()
        print(books)

    def add_book(self):
        """
        Add one or more books to the system.
        Supports comma-separated titles/authors for bulk entry.
        """
        try:
            print("Enter book details:")
            title = input("Title: ").strip()
            if title == "":
                print("No books added.")
                return
            author = input("Author: ").strip()

            to_add = self.book_service.build_books_from_input(title, author)
            if not to_add:
                print("No valid books to add.")
                return

            payload = to_add if len(to_add) > 1 else to_add[0]
            self.book_service.add_book(payload)

            if len(to_add) > 1:
                print("Books added: ")
                for b in to_add:
                    print(f"- {b.title} by {b.author}")
            else:
                b = to_add[0]       
                print(f"Book added: {b.title} by {b.author}")
        except Exception as e:
            print(f"Error adding book: {e}")     

    def find_book_by_name(self):
        """
        Search for books whose titles match a user-provided query.
        """
        query = input("Enter book title to search: ").strip()
        books = self.book_service.find_book_by_name(query)
        print(books)

    def delete_book(self):
        """
        Remove a book from the system by its unique ID.
        """
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
        """
        Update one or more fields of an existing book.
        User enters key-value pairs until finished.
        """
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
    repo = BookRepository("books.json")
    history_repo = CheckoutHistoryRepository("checkout_history.json")
    book_svc = BookService(repo, history_repo)
    book_analytics_svc = BookAnalyticsService()
    repl = BookREPL(book_svc, book_analytics_svc)
    repl.start()
