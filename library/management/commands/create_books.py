import random

from faker import Faker
from django.core.management.base import BaseCommand

from library.models import Author, Book


class Command(BaseCommand):
    help = "Generate random Book and Author instances"

    def add_arguments(self, parser):
        parser.add_argument("author_count", type=int, help="Number of Author instances to create")
        parser.add_argument("book_count", type=int, help="Number of Book instances to create")

    def handle(self, *args, **kwargs):
        author_count = kwargs["author_count"]
        book_count = kwargs["book_count"]

        fake = Faker()

        authors = [Author(name=fake.name(), birth_date=fake.date_of_birth(minimum_age=20, maximum_age=80), country=fake.country()) for _ in range(author_count)]
        Author.objects.bulk_create(authors)
        self.stdout.write(self.style.SUCCESS(f"Successfully created {author_count} author(s)."))

        authors = list(Author.objects.all())
        books = [
            Book(title=fake.sentence(nb_words=5), author=random.choice(authors), published_date=fake.date_between(start_date="-10y", end_date="today")) for _ in range(book_count)
        ]
        Book.objects.bulk_create(books)
        self.stdout.write(self.style.SUCCESS(f"Successfully created {book_count} book(s)."))
