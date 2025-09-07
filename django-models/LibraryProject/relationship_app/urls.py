from django.urls import path,include
from . import views

urlpatterns = [
    path('books/', views.list_books, name='list_books'),
    path('library/<int:pk>/', views.libraryDetailview.as_view(), name='library_detail'),
]