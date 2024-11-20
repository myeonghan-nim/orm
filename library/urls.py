from django.urls import path

from .views import LibraryView, AuthorView, BookView

urlpatterns = [
    path('library/', LibraryView.as_view(), name='library-list'),
    path("authors/", AuthorView.as_view(), name="authors-list"),
    path("books/", BookView.as_view(), name="books-list"),
    path("books/<int:book_id>/", BookView.as_view(), name="book-detail"),
]
