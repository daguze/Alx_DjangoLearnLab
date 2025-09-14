

# UPdate the Book instance

from  bookshelf.models import book

book = Book.objects.get(title = "1984")
book.title = "Nineteen Eighty-Four'
book.save()

book.title

#excpected output
'Nineteen Eighty-Four'
