import numpy as np
import pandas as pd
from src.domain.book import Book
from collections import Counter

# Ground rules for numpy:
# 1. keep numpy in service layer only
#   - if you see numpy imports anywhere else, this is a design smell!
# 2. notice how methods take in books, and return normal datatypes NOT ndarrays
#   - this service and numpy are ISOLATED, this will keep our functions PURE and


class BookAnalyticsService:
    """
    Analytics layer: computes statistics/aggregations over Book objects.
    """
    def average_price(self, books: list[Book]) -> float:
        """
        Compute the mean book price across all books.
        Note: if any prices are None, dtype=float converts them to nan.
        """
        prices = np.array([b.price_usd for b in books], dtype=float)
        return float(prices.mean())

    def top_rated(self, books: list[Book], min_ratings: int = 1000, limit: int = 10):
        """
        Return the top-rated books that have at least `min_ratings` ratings.

        Steps:
        - Build arrays of ratings_count (for filtering)
        - Filter the book list with a boolean mask
        - Sort by score descending
        with numpy
        """
        ratings = np.array([b.ratings_count for b in books])
        counts = np.array([b.ratings_count for b in books])

        # what we have now:
        # books -> books objects
        # ratings -> numbers for ALL books
        # counts -> numbers for ALL books
        # filtered books contains all books that have at least 1000 ratings
        mask = counts >= min_ratings
        filteredBooks = np.array(books)[mask]
        # now scores is only the ratings for the filtered books i.e. over 1000 ratings
        scores = ratings[mask]
        sorted_idx = np.argsort(scores)[::-1]
        return filteredBooks[sorted_idx].tolist()[limit]

    # value score = rating * log(ratings_count) / price
    def value_scores(self, books: list[Book]) -> dict[str, float]:
        """
        Compute a "value score" per book:
            score = average_rating * log(1 + ratings_count) / price

        Higher score means:
        - higher ratings
        - more rating confidence (more reviews)
        - cheaper price
        with numpy
        """
        ratings = np.array([b.average_rating for b in books])
        counts = np.array([b.ratings_count for b in books])
        prices = np.array([b.price_usd for b in books])

        scores = (ratings * np.log1p(counts)) / prices

        return {
            # zip() iterates both lists in parallel
            # pairing each book with its corresponding score
            # zip() will stop automatically if one list is shorter
            # - if the same key appears more than once, later entries overwrites earlier entries
            book.book_id: float(score)
            for book, score in zip(books, scores)
        }

    def median_price_by_genre(self, books: list[Book]) -> dict[str, float]:
        """
        Compute the median price per genre.

        Edge cases handled:
        - missing/None prices (filtered out)
        - genres with no valid prices return NaN
        """
        prices = np.array([b.price_usd for b in books], dtype=float)
        genres = np.array([b.genre for b in books])
        result = {}

        # Loop over each unique genre
        for g in np.unique(genres):
            genre = str(g)
            # boolean mask - “Which books belong to this genre?”
            mask = genres == g
            # Select prices for this genre
            vals = prices[mask]
            # Remove missing prices
            vals = vals[~np.isnan(vals)]

            # Compute median
            if vals.size > 0:
                result[genre] = float(np.nanmedian(vals))
            else:
                result[genre] = float("nan")
        return result

    def top_rated_with_pandas(
        self, books: list, min_ratings: int = 1000, limit: int = 10
    ) -> list:
        """
        Pandas version of top rated:
        - build DataFrame (book object + avg + count)
        - filter by count threshold
        - sort by avg desc
        - return the book objects
        """
        df = pd.DataFrame(
            [
                {"book": b, "avg": b.average_rating, "count": b.ratings_count}
                for b in books
            ]
        )
        filtered = df[df["count"] >= min_ratings].sort_values("avg", ascending=False)
        return filtered["book"].tolist()[:limit]

    def most_common_genres(self, books: list[Book], top_n: int | None = None) -> dict[str, int]:
        """
        Count how many books exist in each genre.

        Returns an ordered mapping genre -> count (most common first).
        Missing genres are normalized to "Unknown".
        """
        # Normalize missing genres to a readable label
        genres = [b.genre if (b.genre is not None and b.genre != "") else "Unknown" for b in books]
        counts = Counter(genres)
        most = counts.most_common(top_n)
        return {g: c for g, c in most}

    def value_scores_with_pandas(
        self, books: list, limit: int = 10
    ) -> dict[str, float]:
        """
        Pandas version of value_scores:
        - compute score column
        - sort
        - return top N as dict[book_id] -> score
        """
        df = pd.DataFrame(
            [
                {
                    "book_id": b.book_id,
                    "avg": b.average_rating,
                    "count": b.ratings_count,
                    "price": b.price_usd,
                }
                for b in books
            ]
        )
        df["score"] = df["avg"] * np.log1p(df["count"]) / df["price"]
        # set_index() sets book_id as the index
        # we do this because we want to end up with a dict[str, float]
        # where book_id is the key and the value score is the float
        # sometimes numpy works with float64, but we need to return float,
        # hence the defensive use of .astype()
        return (
            df.sort_values("score", ascending=False)
            .head(limit)
            .set_index("book_id")["score"]
            .astype(float)
            .to_dict()
        )

    def bayesian_weighted_rating_by_genre(
        self,
        books: list[Book],
        m: int = 50,                 # minimum ratings threshold (50-100 recommended)
        min_books_per_genre: int = 3
    ) -> dict[str, float]:
        """
        Compute Bayesian-weighted rating per genre.

        Why Bayesian:
        - Small sample sizes can inflate averages.
        - Bayesian smoothing blends the genre mean with the global mean.

        Variables:
        - C: global mean rating across all books
        - R: mean rating within the genre
        - v: median ratings_count for the genre (confidence proxy)
        - m: minimum confidence threshold (50–100 recommended)

        weighted = (v/(v+m))*R + (m/(v+m))*C

        Returns:
        - ordered mapping genre -> weighted rating (descending)
        """
        rows = []
        for b in books:
            # Skip bad/missing values
            if b.average_rating is None or b.ratings_count is None:
                continue
            if b.genre is None or str(b.genre).strip() == "":
                genre = "Unknown"
            else:
                genre = str(b.genre).strip()

            rows.append({"genre": genre, "avg": float(b.average_rating), "count": int(b.ratings_count)})

        if not rows:
            return {}

        df = pd.DataFrame(rows)

        # Global mean across ALL books
        C = float(df["avg"].mean())

        # Per-genre aggregates
        grp = (
            df.groupby("genre")
            .agg(mean_average_rating=("avg", "mean"),
                 median_ratings_count=("count", "median"),
                 n_books=("avg", "size"))
            .reset_index()
        )

        # Bayesian weighted rating
        v = grp["median_ratings_count"]
        R = grp["mean_average_rating"]
        grp["weighted_rating"] = (v / (v + m)) * R + (m / (v + m)) * C

        # Sort descending
        grp = grp.sort_values("weighted_rating", ascending=False)

        # Return ordered mapping genre -> weighted_rating
        return {row["genre"]: float(row["weighted_rating"]) for _, row in grp.iterrows()}

    def price_vs_rating_points(self, books: list[Book]) -> tuple[list[float], list[float]]:
        """
        Extract paired (price, rating) points for scatter plotting.
        Skips books missing either value.
        """
        prices = []
        ratings = []

        for b in books:
            if b.price_usd is None or b.average_rating is None:
                continue
            prices.append(float(b.price_usd))
            ratings.append(float(b.average_rating))
        return prices, ratings
    
    def books_released_by_year(self, books: list[Book]) -> dict[int, int]:
        """
        Count how many books were published each year.

        Returns:
            dict[year] -> count
        """
        years = []

        for b in books:
            if b.publication_year is None:
                continue
            years.append(int(b.publication_year))

        if not years:
            return {}

        # Count occurrences
        unique, counts = np.unique(years, return_counts=True)

        return {int(year): int(count) for year, count in zip(unique, counts)}

    def availability_counts(self, books: list[Book]) -> dict[str, int]:
        """
        Count current availability status.

        Note:
        - This reflects current state only.
        - History/trends require CheckoutHistoryRepository data.
        """
        available = 0
        checked_out = 0

        for b in books:
            if getattr(b, "available", False):
                available += 1
            else:
                checked_out += 1

        return {
            "Available": available,
            "Checked Out": checked_out,
        }