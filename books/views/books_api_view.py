from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from api.utils import CsrfExemptSessionAuthentication
from books.handlers.books_handler_get import books_get_handler
from books.handlers.books_handler_post import books_post_handler
from books.handlers.books_patch_handler import books_patch_handler
from books.services.book_service import BookService


@api_view(['GET', 'POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def books(request):
    if request.method == 'GET':
        return Response(books_get_handler(request))
    
    if request.method == 'POST':
        return books_post_handler(request)


@api_view(['GET', 'PATCH'])
@authentication_classes([CsrfExemptSessionAuthentication])
def book_detail(request, book_id):
    if request.method == 'GET':
        service = BookService()
        book = service.getBookDetails(book_id)

        if book is None:
            return Response({"status": "error", "message": "Book not found"}, status=404)

        return Response({"status": "ok", "data": book})

    if request.method == 'PATCH':
        return books_patch_handler(request, book_id)
