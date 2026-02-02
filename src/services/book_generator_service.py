import json
import random
import uuid
from datetime import datetime, timedelta

def generate_books_json(filename='books.json', count=500):
    genres = [
        'Fantasy',
        'Sci-Fi',
        'Non-Fiction',
        'Mystery',
        'Romance',
        'Technology',
        'History'
    ]

    publishers = [
        'North Star Press',
        'Emerald House',
        'Atlas Publishing',
        'Blue River Books'
    ]

    formats = [
        'Hardcover',
        'Paperback',
        'Ebook',
        'Audiobook'
    ]

    books = []
    now = datetime.now()
    six_months_ago = now - timedelta(days = 182)    

    for i in range(1, count + 1):

        random_days = random.randint(0, 182)
        random_seconds = random.randint(0, 80000)
        last_checkout = six_months_ago + timedelta(days = random_days, seconds = random_seconds)
        books.append(
            {
                'book_id': str(uuid.uuid4()),
                'title': f'Book Title {i}',
                'author': f'Author {random.randint(1, 80)}',
                'genre': random.choice(genres),
                'publication_year': random.randint(1850, 2025),
                'page_count': random.randint(120, 1100),
                'average_rating': round(random.uniform(1.5, 4.9), 2),
                'ratings_count': random.randint(25, 10000),
                'price_usd': round(random.uniform(7.99, 149.99), 2),
                'publisher': random.choice(publishers),
                'language': 'English',
                'format': random.choice(formats),
                'in_print': random.choice([True, True, True, True, False]),
                'sales_millions': round(random.uniform(0.01, 15), 2),
                'last_checkout': last_checkout.isoformat(),
                'available': random.choice([True, False])
            }
        )

    with open(filename, 'w', encoding = 'utf-8') as f:
        json.dump(books, f, indent = 2)