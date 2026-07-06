from django.db.models import Q
from ..models import Book, Author, BookImage


class BookService:

    def setBook(self, title, synopsis, author_id, selling_price, purchase_cost,
                tax_rate=0.18, status="ACTIVE", release_date=None, tags=None, images=None):

        if not author_id:
            raise ValueError("author_id is required")

        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            raise ValueError(f"Author with id {author_id} does not exist")

        book = Book.objects.create(
            title=title,
            synopsis=synopsis,
            author=author,
            selling_price=selling_price,
            purchase_cost=purchase_cost,
            tax_rate=tax_rate,
            status=status,
            release_date=release_date,
        )

        if tags:
            book.tags.set(tags)

        if images:
            for img in images:
                BookImage.objects.create(
                    book=book,
                    image=img.get("url"),
                    image_type=img.get("type", "FRONT_COVER")
                )

        return self._serialize(book)

    def getBookDetails(self, id):
        try:
            book = Book.objects.select_related("author").prefetch_related("images", "tags").get(id=id)
        except Book.DoesNotExist:
            return None

        return self._serialize(book)

    def getBookViaQuery(self, status=None, sort=None, limit=None,
                        offset=0, tags=None, search=None, author_id=None):

        qs = self.getBookQueryset(
            status=status,
            sort=sort,
            search=search,
            tags=tags,
            author_id=author_id,
        )

        MAX_LIMIT = 100
        DEFAULT_LIMIT = 20
        MAX_OFFSET = 10000

        limit = min(limit, MAX_LIMIT) if limit else DEFAULT_LIMIT
        offset = min(int(offset), MAX_OFFSET)

        return [self._serialize(b) for b in qs[offset:offset + limit]]

    def getBookQueryset(self, status=None, sort=None, search=None,
                        tags=None, author_id=None):
        """
        Returns a filtered, ordered QuerySet of Book instances.
        Does NOT slice — used by cursor pagination and getBookViaQuery.
        Always includes -id as a stable tie-breaker for consistent pagination.
        """
        ALLOWED_SORT_FIELDS = {"id", "title", "selling_price", "purchase_cost", "author__fullname", "release_date"}

        qs = Book.objects.select_related("author").prefetch_related("images", "tags")

        if status is not None:
            qs = qs.filter(status=status)

        if author_id is not None:
            qs = qs.filter(author_id=author_id)

        if search and len(search) >= 2:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(synopsis__icontains=search) |
                Q(author__fullname__icontains=search) |
                Q(tags__name__icontains=search)
            ).distinct()

        if tags:
            qs = qs.filter(tags__name__in=tags).distinct()

        if sort:
            field = sort.lstrip("-")
            if field in ALLOWED_SORT_FIELDS:
                # Always append -id as a tie-breaker so cursor position is stable
                qs = qs.order_by(sort, "-id")
        else:
            qs = qs.order_by("-id")

        return qs

    def serializeBooks(self, books):
        """
        Serializes a list or queryset slice of Book instances.
        Reuses _serialize so the shape is identical to getBookViaQuery.
        """
        return [self._serialize(b) for b in books]

    def _serialize(self, book):
        return {
            "id": book.id,
            "title": book.title,
            "synopsis": book.synopsis,
            "selling_price": float(book.selling_price),
            "purchase_cost": float(book.purchase_cost),
            "tax_rate": float(book.tax_rate),
            "status": book.status,
            "release_date": book.release_date.isoformat() if book.release_date else None,

            "author": {
                "id": book.author.id,
                "fullname": book.author.fullname,
            } if book.author else None,

            "images": [
                {
                    "url": img.image,
                    "type": img.image_type
                }
                for img in book.images.all()
            ],

            "tags": list(book.tags.names())
        }

    def updateBook(self, book_id, title=None, synopsis=None, author_id=None,
                   selling_price=None, purchase_cost=None, tax_rate=None,
                   status=None, release_date=None, tags=None, images=None):

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            raise ValueError(f"Book with id {book_id} does not exist")

        if title is not None:
            book.title = title
        if synopsis is not None:
            book.synopsis = synopsis
        if selling_price is not None:
            book.selling_price = selling_price
        if purchase_cost is not None:
            book.purchase_cost = purchase_cost
        if tax_rate is not None:
            book.tax_rate = tax_rate
        if status is not None:
            book.status = status
        if release_date is not None:
            book.release_date = release_date

        if author_id is not None:
            try:
                book.author = Author.objects.get(id=author_id)
            except Author.DoesNotExist:
                raise ValueError(f"Author with id {author_id} does not exist")

        book.save()

        if tags is not None:
            book.tags.set(tags)

        if images:
            for img in images:
                BookImage.objects.update_or_create(
                    book=book,
                    image_type=img.get("type"),
                    defaults={"image": img.get("url")},
                )

        return self._serialize(book)
