import os
from datetime import date

import django

# Change "yourproject" to the folder name that contains your settings.py
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_club.settings")
django.setup()

# Change "myapp" to your app's name
from members.models import Member, Book, ReadingLog

members_data = [
    {"firstname": "Anna", "lastname": "Silva", "email": "anna@example.com",
     "phone": 912345678, "joined_date": date(2024, 1, 15)},
    {"firstname": "Ben", "lastname": "Costa", "email": "ben@example.com",
     "phone": 923456789, "joined_date": date(2024, 3, 2)},
    {"firstname": "Carla", "lastname": "Santos", "email": "carla@example.com",
     "phone": 934567890, "joined_date": date(2024, 6, 20)},
]

books_data = [
    {"title": "Dune", "author": "Frank Herbert", "pages": 412, "published_year": 1965},
    {"title": "1984", "author": "George Orwell", "pages": 328, "published_year": 1949},
    {"title": "The Hobbit", "author": "J.R.R. Tolkien", "pages": 310, "published_year": 1937},
    {"title": "Emma", "author": "Jane Austen", "pages": 474, "published_year": 1815},
]

# (member email, book title, date finished)
readings_data = [
    ("anna@example.com", "Dune", date(2024, 2, 10)),
    ("anna@example.com", "1984", date(2024, 4, 5)),
    ("ben@example.com", "The Hobbit", date(2024, 5, 1)),
    ("ben@example.com", "Dune", date(2024, 7, 12)),
    ("carla@example.com", "Emma", date(2024, 8, 30)),
]

for data in members_data:
    Member.objects.get_or_create(email=data["email"], defaults=data)

for data in books_data:
    Book.objects.get_or_create(
        title=data["title"], author=data["author"], defaults=data
    )

for email, title, finished in readings_data:
    ReadingLog.objects.get_or_create(
        member=Member.objects.get(email=email),
        book=Book.objects.get(title=title),
        defaults={"date_finished": finished},
    )

print(
    f"Done: {Member.objects.count()} members, "
    f"{Book.objects.count()} books, "
    f"{ReadingLog.objects.count()} reading logs."
)
