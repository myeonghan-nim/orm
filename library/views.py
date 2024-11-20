import csv
import json
import os

from django.db import connection
from django.db.models import Count, Avg, Min, Max
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import Author, Book

CSV_FILE_PATH = os.path.join(settings.BASE_DIR, "analyze-queries.csv")


def clear_queries():
    connection.queries.clear()


def write_queries_to_csv(queries):
    with open(CSV_FILE_PATH, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not os.path.isfile(CSV_FILE_PATH):
            writer.writerow(["SQL", "Time"])
        for query in queries:
            writer.writerow([query.get("sql", ""), query.get("time", "")])


class LibraryView(View):
    CACHE_KEY = "library_data"
    CACHE_TIMEOUT = 60 * 15

    def get(self, request):
        clear_queries()

        library = cache.get(self.CACHE_KEY)
        if not library:
            authors = list(Author.objects.only("name", "country").defer("birth_date").values("name", "country"))
            books = list(Book.objects.only("title", "author").select_related("author").values("title", "author__name"))
            library = {"authors": authors, "books": books}
            cache.set(self.CACHE_KEY, library, self.CACHE_TIMEOUT)

        write_queries_to_csv(connection.queries)

        authors = library["authors"]
        books = library["books"]
        return JsonResponse({"authors": authors, "books": books})


class AuthorView(View):
    ERROR_MESSAGE_404 = "Author with the specified %s does not exist."

    def get(self, request):
        clear_queries()

        try:
            author_id = request.GET.get("id", None)
            name = request.GET.get("name", None)
            country = request.GET.get("country", None)
            exclude_name = request.GET.get("exclude_name", None)
            exclude_country = request.GET.get("exclude_country", None)

            aggregates = request.GET.get("aggregate", "")
            annotations = request.GET.get("annotate", "")

            if author_id:
                try:
                    author = Author.objects.get(id=author_id)
                    return JsonResponse(
                        {
                            "author": {
                                "id": author.id,
                                "name": author.name,
                                "birth_date": author.birth_date,
                                "country": author.country,
                            }
                        }
                    )
                except Author.DoesNotExist:
                    return JsonResponse({"error": self.ERROR_MESSAGE_404 % "id"}, status=404)
            if name:
                try:
                    author = Author.objects.get(name=name)
                    return JsonResponse(
                        {
                            "author": {
                                "id": author.id,
                                "name": author.name,
                                "birth_date": author.birth_date,
                                "country": author.country,
                            }
                        }
                    )
                except Author.DoesNotExist:
                    return JsonResponse({"error": self.ERROR_MESSAGE_404 % "name"}, status=404)

            authors = Author.objects.all()
            if country:
                authors = authors.filter(country=country)
            if exclude_country:
                authors = authors.exclude(country=exclude_country)
            if exclude_name:
                authors = authors.exclude(name=exclude_name)

            aggregates_list = [agg.strip() for agg in aggregates.split(",") if agg]
            if aggregates_list:
                available_aggregates = {
                    "count": Count("id"),
                    "average_books": Avg("books__id"),
                    "min_birth_date": Min("birth_date"),
                    "max_birth_date": Max("birth_date"),
                }
                aggregate_result = {}
                for agg in aggregates_list:
                    if agg in available_aggregates:
                        aggregate_result[agg] = authors.aggregate(result=available_aggregates[agg])["result"]
                return JsonResponse({"aggregate": aggregate_result})

            annotations_list = [ann.strip() for ann in annotations.split(",") if ann]
            if annotations_list:
                available_annotations = {
                    "book_count": Count("books__id"),
                    "country_count": Count("id"),
                }
                for annotation in annotations_list:
                    if annotation in available_annotations:
                        authors = authors.values("country").annotate(**{annotation: available_annotations[annotation]})
                return JsonResponse({"annotated_authors": list(authors)})

            author_list = list(authors.values("id", "name", "birth_date", "country"))
            return JsonResponse({"authors": author_list})
        finally:
            write_queries_to_csv(connection.queries)


@method_decorator(csrf_exempt, name="dispatch")
class BookView(View):
    def post(self, request):
        clear_queries()

        try:
            data = json.loads(request.body)

            title = data.get("title")
            published_date = data.get("published_date")
            author_id = data.get("author_id")

            if not (title and published_date and author_id):
                return JsonResponse({"error": "Missing fields"}, status=400)

            try:
                author = Author.objects.get(id=author_id)
            except Author.DoesNotExist:
                return JsonResponse({"error": "Author not found"}, status=404)

            book = Book.objects.create(title=title, published_date=published_date, author=author)
            return JsonResponse({"message": "Book created", "book_id": book.id}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        finally:
            write_queries_to_csv(connection.queries)

    def put(self, request, book_id):
        clear_queries()

        try:
            data = json.loads(request.body)

            title = data.get("title")
            published_date = data.get("published_date")
            author_id = data.get("author_id")

            try:
                book = Book.objects.get(id=book_id)
            except Book.DoesNotExist:
                return JsonResponse({"error": "Book not found"}, status=404)

            if title:
                book.title = title
            if published_date:
                book.published_date = published_date
            if author_id:
                try:
                    author = Author.objects.get(id=author_id)
                    book.author = author
                except Author.DoesNotExist:
                    return JsonResponse({"error": "Author not found"}, status=404)

            book.save()
            return JsonResponse({"message": "Book updated", "book_id": book.id}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        finally:
            write_queries_to_csv(connection.queries)

    def delete(self, request, book_id):
        clear_queries()

        try:
            try:
                book = Book.objects.get(id=book_id)
            except Book.DoesNotExist:
                return JsonResponse({"error": "Book not found"}, status=404)

            book.delete()
            return JsonResponse({"message": "Book deleted", "book_id": book_id}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        finally:
            write_queries_to_csv(connection.queries)
