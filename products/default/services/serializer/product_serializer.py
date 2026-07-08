
def product_serializer(product):
    product_category_serialize = {
        "id": product.category.id,
        "name": product.category.name,
        "slug": product.category.slug,
        "image": None,
        "status": product.category.status,
    }if product.category else None

    product_book = {
        "title": product.books.first().title,
        "synopsis": product.books.first().synopsis,
        "isbn": product.books.first().isbn,
        "release_date": product.books.first().release_date,
        "publisher": product.books.first().publisher.name,
        "author": product.books.first().author.fullname,
        "genre": product.books.first().genre.name,

    } if product.books.exists() else None

    product_base = {
        "id": product.products_base.first().id,
        "name": product.products_base.first().name,
        "description": product.products_base.first().description,
        "sku": product.products_base.first().sku,
    } if product.products_base.exists() else None

    return {
        "name": product.name,
        "type": product.product_type.slug,
        "tags": [tag.name for tag in product.tags.all()],
        "category": product_category_serialize,
        "thumbnail": product.thumbnail,
        "book": product_book,
        "base": None,
    }
