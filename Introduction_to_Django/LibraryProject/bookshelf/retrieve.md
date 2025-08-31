
# Retrieve the Book instance
'''python
from myapp.model import book

#Retrieve the created Book

book = Book.objects.get(title = "1984)
book.title, book.author, book.publication_year


#excpected output
('1984', 'George Orwell', 1949)
