
def product_serializer(product):
    product_category_serialize = {
        "id": product.category.id,
        "name": product.category.name,
        "slug": product.category.slug,
        "image": None,
        "status": product.category.status,
    }if product.category else None

    product_serialize = {
        "id": product.id,
        "name": product.name,
        "thumbnail": product.thumbnail,
        "tags": [tag.name for tag in product.tags.all()],
        "type": {
            "name": product.product_type.name,
            "description": product.product_type.description,
            "slug": product.product_type.slug,
        }
    }
    
    product_book = {
        "title": product.books.first().title,
        "synopsis": product.books.first().synopsis,
        "isbn": product.books.first().isbn,
        "release_date": product.books.first().release_date,
        "publisher": product.books.first().publisher.name,
        "author": product.books.first().author.fullname,
        "genre": product.books.first().genre.name,

    } if product.books.exists() else None

    return {
        "info": product_serialize,
        "category": product_category_serialize,
        "book": product_book,
    }