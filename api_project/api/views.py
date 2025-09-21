from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from .permissions import permissions
# Create your views here.


class BookList(generics.ListAPIView):
    queryset = Book.objects.all() 
    serializer_class = BookSerializer
    permission_classes = []

    
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = []  # handled per-action

    def get_permissions(self):
        if self.action in ['list', 'public_books']:
            return [permissions.AllowAny()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action == 'destroy':
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny()])
    def public_books(self, request):
        books = Book.objects.all()
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated()])
    def mark_favorite(self, request, pk=None):
        book = self.get_object()
        # Implement favorite logic here
        return Response({'status': 'book marked as favorite'})