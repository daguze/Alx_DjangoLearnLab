from relationship_app.models import Author,Book,Library,Librarian




def books_by_author(author_name):
    author = Author.objects.get(name=author_name)
    books = Book.objects.filter(author=author)
    return [book.title for book in books]
def books_in_library(library_name):
    library = Library.objects.get(name=library_name)
    books = library.books.all()
    return [book.title for book in books]
def librarians_in_library(library_name):
    library = Library.objects.get(name=library_name)
    librarian = Librarian.objects.get(library=library)
    return librarian.name

if __name__ == "__main__":
    print("Books by J.K. Rowling:", books_by_author("J.K. Rowling"))
    print("Books in Central Library:", books_in_library("Central Library"))
    print("Librarian of Central Library:", librarians_in_library("Central Library"))