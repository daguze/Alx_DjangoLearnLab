
# Delete the Book instance

```python
from myapp.models import Book

book = Book.objects.get(title="Nineteen Eighty-Four")
book.delete()

# Try retrieving all books again
Book.objects.all()
