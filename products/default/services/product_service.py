from django.db.models import Q
from ..models import Category, Product, ProductImage, ProductType


class ProductService:

    def get_category_object(self,id):
        try:
            return Category.objects.get(id=id)
        except Category.DoesNotExist:
            return None

    def get_book_product_type(self):
        obj, created = ProductType.objects.get_or_create(
            name='book',
            defaults={
                'description': 'a book'
            }
        )
        return obj

    def get_book_product_category(self):
        obj, created = Category.objects.get_or_create(
            name='books',
            defaults={
                'slug': 'books',
                'description': 'books yeah',
                'image': 'https://example.com',
                'status': True
            }
        )
        return obj


    def get_default_product_type(self):
        obj, created = ProductType.objects.get_or_create(
            name='default',
            defaults={
                'description': 'A normal product'
            }
        )
        return obj
    
    def get_default_product_category(self):
        obj, created = Category.objects.get_or_create(
            name='default',
            defaults={
                'slug': 'default',
                'description': 'default product category',
                'image': 'https://example.com',
                'status': True
            }
        )
        return obj

    def setProduct(self, name, description, category: Category = None, brand=None,
                   selling_price=None, purchase_price =  None, status=None, tags=None, images=None):

        product_type = self.get_default_product_type()

        if category is None:
            category = self.get_default_product_category()
        
        if status is None:
            status = True

        product = Product.objects.create(
            name=name,
            description=description,
            category=category,
            brand=brand,
            product_type = product_type,
            status = status,
            selling_price=selling_price,
        )

        if tags:
            product.tags.set(tags)

        if images:
            for img in images:
                ProductImage.objects.create(
                    product=product,
                    image=img.get("url"),
                    image_type=img.get("type", "HERO")
                )
        return self._serialize(product)

    def getProductDetails(self, id):
        try:
            product = Product.objects.select_related("category").get(id=id)
        except Product.DoesNotExist:
            return None

        return self._serialize(product)

    def getProductViaQuery(self, status=None, sort=None, limit=None,
                           offset=0, tags=None, search=None,
                           category_id=None):

        qs = self.getProductQueryset(
            status=status,
            sort=sort,
            search=search,
            tags=tags,
            category_id=category_id,
        )

        MAX_LIMIT = 100
        DEFAULT_LIMIT = 20
        MAX_OFFSET = 10000

        limit = min(limit, MAX_LIMIT) if limit else DEFAULT_LIMIT
        offset = min(int(offset), MAX_OFFSET)

        return [self._serialize(p) for p in qs[offset:offset + limit]]

    def getProductQueryset(self, status=None, sort=None, search=None,
                           tags=None, category_id=None):
        """
        Returns a filtered, ordered QuerySet of Product instances.
        Does NOT slice — used by cursor pagination and getProductViaQuery.
        Always includes -id as a stable tie-breaker for consistent pagination.
        """
        ALLOWED_SORT_FIELDS = {"id", "name", "selling_price", "brand", "category__name"}

        qs = Product.objects.select_related("category").prefetch_related("images", "tags")

        if status is not None:
            qs = qs.filter(status=status)

        if category_id is not None:
            qs = qs.filter(category_id=category_id)

        if search and len(search) >= 2:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(brand__icontains=search) |
                Q(category__name__icontains=search) |
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

    def serializeProducts(self, products):
        """
        Serializes a list or queryset slice of Product instances.
        Reuses _serialize so the shape is identical to getProductViaQuery.
        """
        return [self._serialize(p) for p in products]

    def _serialize(self, product):

        ###############
        product_images = {}

        for img in product.images.all():
            product_images[img.image_type.lower()] = {
                "original": img.image,
                "small": img.image_small,
                "medium": img.image_medium,
                "large": img.image_large,
            }

        product_category_serialize = {
            "id": product.category.id,
            "name": product.category.name,
            "slug": product.category.slug,
            "image": product.category.image,
            "status": product.category.status,
        }if product.category else None

        product_serialize = {
            "id": product.id,
            "name": product.name,
        }

        product_attribute = {
            "type": product.product_type.name
        }

        return {
            "info": product_serialize,
            "category": product_category_serialize,
            "attributes": product_attribute,
            "images": product_images,
        }

    def updateProduct(self, product_id, name=None, description=None,
                    category_id=None, brand=None, selling_price=None,
                    status=None, tags=None, images=None):

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValueError(f"Product with id {product_id} does not exist")

        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if brand is not None:
            product.brand = brand
        if selling_price is not None:
            product.selling_price = selling_price
        if status is not None:
            product.status = status

        if category_id is not None:
            try:
                product.category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                raise ValueError(f"Category with id {category_id} does not exist")

        product.save()

        if tags is not None:
            product.tags.set(tags)

        if images:
            for img in images:
                ProductImage.objects.update_or_create(
                    product=product,
                    image_type=img.get("type"),
                    defaults={"image": img.get("url")},
                )

        return self._serialize(product)
    