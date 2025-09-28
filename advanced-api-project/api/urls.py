from django.urls import path
from .views import (BookListView,BookDetailView,BookCreateView,BookUpdateView,BookDeleteView,BookUpdateByQueryView,BookDeleteByQueryView)

urlpatterns = [
    
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('books/create/', BookCreateView.as_view(), name='book-create'),
    path('books/<int:pk>/update/', BookUpdateView.as_view(), name='book-update'),
    path('books/<int:pk>/delete/', BookDeleteView.as_view(), name='book-delete'),
    path('books/update', BookUpdateByQueryView.as_view(), name='book-update-plain'),
    path('books/delete', BookDeleteByQueryView.as_view(), name='book-delete-plain'),
]