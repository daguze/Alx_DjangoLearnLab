from django.shortcuts import redirect, render
from django.contrib.auth.decorators import permission_required
from .models import Book
# Create your views here.

@permission_required('bookshelf.can_view', raise_exception=True)
def list_books(request):
    books = Book.objects.all()
    return render(request, 'book/book_list.html', {'books': books})

@permission_required('bookshelf.can_create', raise_exception=True)
def create_book(request):
    return render(request, 'book/create_book.html')

@permission_required('bookshelf.can_edit', raise_exception=True)
def edit_book(request, book_id):
    books = Book.objects.all()
    return render(request, 'book/edit_book.html', {'books': books})

@permission_required('bookshelf.can_delete', raise_exception=True)
def delete_book(request, book_id):
    book = Book.objects.get(id=book_id)
    books = Book.objects.all()
    book.delete()
    return redirect('list_books')

from django.http import HttpResponse

def my_view(request):
    response = HttpResponse("Hello CSP!")
    response['Content-Security-Policy'] = "default-src 'self'; script-src 'self'"
    return response
