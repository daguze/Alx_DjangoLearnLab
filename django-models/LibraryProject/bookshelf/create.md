# Create a Book instance

```python
from bookshelf.models import Book

# Create a new book
book = Book.objects.create(title="1984", author="George Orwell", publication_year=1949)
book

#Excpected outcome
<Book: 1984 by George Orwell>
