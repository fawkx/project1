import json
import random
import uuid
import re
from datetime import datetime, timedelta

genres = ["History", "Science Fiction", "Fantasy", "Technology", "Biography", "Mystery", "Romance"]
languages = ["English", "english", "Eng", "French", "Spanish", "German"]
formats = ["Paperback", "Hardcover", "Audiobook", "Ebook", "Audio Book"]
publishers = ["North Star Press", "Galactic Books", "Old Tree Publishing", "Sunshine Media", ""]

tlds = ["com", "net", "org", "io", "edu", "co.uk", "info", "biz", "us", "ca", "de", "fr", "tech"]
subdomains = ["www", "mail", "mx", "kr", "eu", "support", "shop", "news"]
random_words = ["alpha", "omega", "prime", "core", "node", "sky", "terra", "lumen", "byte", "paper"]


def random_date():
    base = datetime.today()
    delta = timedelta(days=random.randint(-365*5, 0))
    return (base + delta).isoformat()

def _clean_domain_part(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r'[^a-z0-9]+', '', s)
    return s or None

def _random_local_part(publisher_short: str) -> str:
    choices = []
    # common inboxes
    choices += ["info", "contact", "support", "sales", "hello", "team"]
    # publisher-based local parts
    if publisher_short:
        choices += [f"{publisher_short}", f"press.{publisher_short}", f"{publisher_short}.dept", f"{publisher_short}info"]
    # person-like parts
    first = random.choice(["john","jane","alex","sam","kr","lee","pat","chris"])
    last = random.choice(["doe","smith","lee","wright","nguyen","garcia","khan"])
    choices += [f"{first}.{last}", f"{first}{last}", f"{first[0]}{last}", f"{first}_{last}"]
    # random words and seeds
    choices += [random.choice(random_words), f"{random.choice(random_words)}{random.randint(1,99)}"]
    # ensure dots are allowed but not at ends
    local = random.choice(choices)
    local = re.sub(r'[^a-z0-9._-]', '', local.lower())
    local = local.strip("._-")
    if not local:
        local = "info"
    # sometimes add an extra dot segment like "kr.something"
    if random.random() < 0.2:
        extra = re.sub(r'[^a-z0-9]+', '', random.choice(random_words))
        local = f"{random.choice(['kr','mx','eu','jp','us'])}.{local}" if extra else local
    return local

def generate_publisher_email(publisher: str) -> str:
    pub_short = _clean_domain_part(publisher)
    # fallback domains if publisher empty or too short
    fallback_domains = ["northstar", "galacticbooks", "oldtree", "sunshine", "blueoak", "redrock"]
    domain_base = pub_short or random.choice(fallback_domains)
    # sometimes add a suffix to domain to increase variety
    if random.random() < 0.25:
        domain_base = domain_base + random.choice(["", "books", "press", "media", str(random.randint(1,99))])
    # optionally add an extra domain segment for subdomain-like domains: e.g., press.northstar
    if random.random() < 0.2:
        extra = re.sub(r'[^a-z0-9]+', '', random.choice(random_words))
        domain = f"{domain_base}.{extra}"
    else:
        domain = domain_base
    tld = random.choice(tlds)
    # optionally include a subdomain before the domain (like mail.publisher.net)
    if random.random() < 0.35:
        sub = random.choice(subdomains)
        domain_full = f"{sub}.{domain}.{tld}"
    else:
        domain_full = f"{domain}.{tld}"
    local = _random_local_part(pub_short)
    # Ensure no accidental double dots
    domain_full = domain_full.replace("..", ".")
    email = f"{local}@{domain_full}"
    return email

def generate_books():
    records = []

    for i in range(500):
        publisher_choice = random.choice(publishers)
        record = {
            "book_id": str(uuid.uuid4()),
            "title": f"Book Title {random.randint(1, 20)}",
            "author": f"Author {random.randint(1, 30)}",
            "genre": random.choice(genres),
            "publication_year": random.choice([random.randint(1750, 2030), "Unknown", None]),
            "page_count": random.choice([random.randint(50, 1000), -5, "N/A", None]),
            "average_rating": random.choice([round(random.uniform(0, 6), 2), "N/A", None]),
            "ratings_count": random.choice([random.randint(0, 5000), "Unknown", None]),
            "price_usd": random.choice([round(random.uniform(-10, 200), 2), "N/A", None]),
            "publisher": random.choice(publishers),
            "language": random.choice(languages),
            "format": random.choice(formats),
            "in_print": random.choice([True, False, "true", "false", None]),
            "sales_millions": random.choice([round(random.uniform(-5, 20), 2), "Unknown", None]),
            "last_checkout": random.choice([random_date(), "", "N/A", None]),
            "available": random.choice([True, False, "true", "false", None]),
            "publisher_email": generate_publisher_email(publisher_choice)
        }
        records.append(record)

    with open("books_dirty.json", "w") as f:
        json.dump(records, f, indent=2)
