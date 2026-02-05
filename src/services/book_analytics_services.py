import numpy as np
import pandas as pd
from src.domain.book import Book

# Ground rules for numpy:
# 1. keep numpy in service layer only
#   - if you see numpy imports anywhere else, this is a design smell!
# 2. notice how methods take in books, and return normal datatypes NOT ndarrays
#   - this service and numpy are ISOLATED, this will keep our functions PURE and


class BookAnalyticsService:

    def average_price(self, books: list[Book]) -> float:
        prices = np.array([b.price_usd for b in books], dtype=float)
        return float(prices.mean())

    def top_rated(self, books: list[Book], min_ratings: int = 1000, limit: int = 10):
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
        # Group books by genre, compute median price per genre.
        # Return mapping genre -> median price.
        # Edge: genres with no priced books; single-book genres.
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

    def top_rated_with_pandas(self, books: list, min_ratings: int = 1000, limit: int = 10) -> list:
        df = pd.DataFrame([{
            'book': b,
            'avg': b.average_rating,
            'count': b.ratings_count
        } for b in books])
        filtered = df[df['count'] >= min_ratings].sort_values('avg', ascending=False)
        return filtered['book'].tolist()[:limit]

    def value_scores_with_pandas(self, books: list, limit: int = 10) -> dict[str, float]:
        df = pd.DataFrame([{
            'book_id': b.book_id,
            'avg': b.average_rating,
            'count': b.ratings_count,
            'price': b.price_usd
        } for b in books])
        df['score'] = df['avg'] * np.log1p(df['count']) / df['price']
        # set_index() sets book_id as the index
        # we do this because we want to end up with a dict[str, float]
        # where book_id is the key and the value score is the float
        # sometimes numpy works with float64, but we need to return float,
        # hence the defensive use of .astype()
        return (
            df
            .sort_values('score', ascending=False)
            .head(limit)
            .set_index('book_id')['score']
            .astype(float).to_dict()
        ) 