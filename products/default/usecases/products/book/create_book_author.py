from products.books.models import Author

def create_book_author(fullname):
    author = Author.objects.create(
        fullname=fullname
    )
    return author
