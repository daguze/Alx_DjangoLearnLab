from django.shortcuts import render
from django.http import HttpResponse
from .models import Author, Book, Library
from django.views.generic import DetailView


# Create your views here.

def list_books(request):
    books = Book.objects.all()
    book_list = [f"{book.title} by {book.author.name}" for book in books]
    return HttpResponse(f"{book_list}")

class libraryDetailview(DetailView):
    model = Library
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'library'
    
