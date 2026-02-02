import json
import random
import uuid
from datetime import datetime, timedelta
import numpy as np

def generate_books_json(filename='books.json', count=500, seed=None):
    rng = np.random.default_rng(seed)
    random.seed(seed)

    genres = [
        'Fantasy',
        'Sci-Fi',
        'Non-Fiction',
        'Mystery',
        'Romance',
        'Technology',
        'History'
    ]
    # make Fantasy and Sci-Fi more popular
    genre_weights = np.array([0.28, 0.24, 0.12, 0.10, 0.08, 0.10, 0.08])
    genre_weights = genre_weights / genre_weights.sum()

    publishers = [
        'North Star Press',
        'Emerald House',
        'Atlas Publishing',
        'Blue River Books'
    ]

    formats = ['Hardcover', 'Paperback', 'Ebook', 'Audiobook']

    # Publication year distribution: fewer before 1950, increasing after 1950
    years = np.arange(1850, 2026)
    year_weights = np.where(years <= 1950, 0.2, 1.0 + (years - 1950) / (2025 - 1950))
    year_weights = year_weights / year_weights.sum()

    # Build correlated latent variables:
    # z0 -> price latent, z1 -> average_rating latent, z2 -> ratings_count latent
    cov = np.array([
        [1.0, 0.7, 0.3],
        [0.7, 1.0, 0.6],
        [0.3, 0.6, 1.0]
    ])
    z = rng.multivariate_normal(mean=np.zeros(3), cov=cov, size=count)

    price_raw = z[:, 0]
    rating_raw = z[:, 1]
    rc_raw = z[:, 2]

    # Transform rating_raw -> average_rating in [1.0, 5.0] (target ~ mean 3.2, sd ~0.6)
    rating = (rating_raw - rating_raw.mean()) / (rating_raw.std() + 1e-9)
    average_rating = np.clip(np.round(rating * 0.6 + 3.2, 2), 1.0, 5.0)

    # Transform price_raw -> price_usd (log-scale so higher latent => substantially higher price)
    price_norm = (price_raw - price_raw.mean()) / (price_raw.std() + 1e-9)
    price_usd = np.round(np.clip(np.exp(price_norm * 0.45 + 2.2), 3.99, 299.99), 2)

    # Transform rc_raw -> ratings_count (positive, heavy-tail via exp)
    rc_norm = (rc_raw - rc_raw.mean()) / (rc_raw.std() + 1e-9)
    ratings_count = np.round(np.clip(np.exp(rc_norm * 0.9 + 4.5), 0, 200000)).astype(int)

    # sales_millions tends to be higher with average_rating + ratings_count
    # combine rating and log1p(ratings_count), then scale and add some noise
    score = (average_rating / 5.0) * 0.6 + (np.log1p(ratings_count) / np.log1p(ratings_count).max()) * 0.4
    sales_loc = score * 10.0  # base scale so typical values are in 0..10 range
    sales_millions = np.round(np.clip(rng.normal(loc=sales_loc, scale=1.5), 0.01, 200.0), 2)

    books = []
    now = datetime.now()
    six_months_ago = now - timedelta(days=182)

    for i in range(1, count + 1):
        # publication year from weighted distribution
        pub_year = int(rng.choice(years, p=year_weights))

        random_days = int(rng.integers(0, 183))
        random_seconds = int(rng.integers(0, 80000))
        last_checkout = six_months_ago + timedelta(days=random_days, seconds=random_seconds)

        idx = i - 1
        books.append(
            {
                'book_id': str(uuid.uuid4()),
                'title': f'Book Title {i}',
                'author': f'Author {rng.integers(1, 80)}',
                'genre': str(rng.choice(genres, p=genre_weights)),
                'publication_year': pub_year,
                'page_count': int(rng.integers(80, 1200)),
                'average_rating': float(average_rating[idx]),
                'ratings_count': int(ratings_count[idx]),
                'price_usd': float(price_usd[idx]),
                'publisher': random.choice(publishers),
                'language': 'English',
                'format': random.choice(formats),
                'in_print': bool(rng.choice([True, True, True, True, False])),
                'sales_millions': float(sales_millions[idx]),
                'last_checkout': last_checkout.isoformat(),
                'available': bool(rng.choice([True, False]))
            }
        )

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(books, f, indent=2)