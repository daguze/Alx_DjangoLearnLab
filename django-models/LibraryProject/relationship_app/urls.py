from django.urls import path,include
from .views import list_books
from .views import LibraryDetailview

urlpatterns = [
    path('books/', list_books, name='list_books'),
    path('library/<int:pk>/', LibraryDetailview.as_view(), name='library_detail'),
]