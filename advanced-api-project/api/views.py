from django.shortcuts import render
from rest_framework.exceptions import PermissionDenied
from .models import Book
from .serializers import BookSerializer
from rest_framework import permissions, generics, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework
from rest_framework import generics
# Create your views here.

class BookListView(generics.ListAPIView):
    """
    Read-only list endpoint for all books.
    Anonymous users CAN read.
    Adds simple search/filter/order to help testing.
    """
    queryset = Book.objects.select_related('author').all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]

filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

filterset_fields = ['title', 'author', 'publication_year']

search_fields = ['title', 'author__name']

ordering_fields = ['title', 'publication_year', 'id']
ordering = ['title']  

class BookDetailView(generics.RetrieveAPIView):
    """
    Read-only detail endpoint for a single book.
    Anonymous users CAN read.
    """
    queryset = Book.objects.select_related('author').all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]


class BookCreateView(generics.CreateAPIView):
    """
    Create a new book.
    Only authenticated users CAN create.
    Uses serializer validation + perform_create hook for extra checks.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if not (user.is_staff or user.is_superuser):
            raise PermissionDenied("Only staff can add books in this environment.")
        serializer.save()

class BookUpdateView(generics.UpdateAPIView):
    """
    Update an existing book.
    Only authenticated users CAN update.
    Adds a perform_update hook (e.g., to run extra validation or side-effects).
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        user = self.request.user
        if not (user.is_staff or user.is_superuser):
            raise PermissionDenied("Only staff can update books in this environment.")
        serializer.save()


class BookDeleteView(generics.DestroyAPIView):
    """
    Delete a book.
    Only authenticated users CAN delete.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.is_staff or user.is_superuser):
            raise PermissionDenied("Only staff can delete books in this environment.")
        instance.delete()

class BookUpdateByQueryView(BookUpdateView):
    
    def get_object(self):
        pk = self.request.query_params.get('id') or self.request.data.get('id')
        if not pk:

            return f'please give a real id'


class BookDeleteByQueryView(BookDeleteView):
    def get_object(self):
        pk = self.request.query_params.get('id') or self.request.data.get('id')
        if not pk:
            return f'please give a real id'
