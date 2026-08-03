import json

from django.db.models import Q, Prefetch

from ..entities.product_attributes_normal import ProductAttributesNormal
from ..entities.product_entity import ProductEntity
from ..entities.product_images_entity import ProductImages
from ..entities.product_variant import ProductVariant as ProductVariantEntity
from ..models import Product
from ..models import Category
from ..models import ProductVariant as ProductVariantModel
from ..models.product_image_model import ProductImage
from ..value_objects.product_category import ProductCategory
from ..value_objects.product_created_at import CreatedAt
from ..value_objects.product_description import ProductDescription
from ..value_objects.product_name import ProductName
from ..value_objects.product_selling_price import SellingPrice
from ..value_objects.product_sku import SKU
from ..value_objects.product_slug import Slug
from ..value_objects.product_tags import Tags
from ..value_objects.product_taxrate import TaxRate
from ..value_objects.product_type import ProductType
from ..value_objects.product_updated_at import UpdatedAt
from decimal import Decimal


class ProductRepository:
    def save(self, productentity: ProductEntity):
        """Save a product entity with all its variants and images to the database."""
        name = productentity.name.value
        category = Category.objects.get(slug=productentity.category.value)
        tags = productentity.tags
        thumbnail = productentity.thumbnail
        product_type = productentity.product_type
        slug = productentity.slug.value

        product_db = Product.objects.create(
            name=name,
            category=category,
            tags=tags,
            thumbnail=thumbnail,
            product_type=product_type,
            slug=slug,
        )

        productentity.id = product_db.id

        if productentity.product_type.value == "normal":
            for idx, variant in enumerate(productentity.variants, 1):
                variant_name = variant.attributes.name.value
                variant_description = variant.attributes.description.value
                variant_variantnumber = variant.variantnumber
                variant_thumbnail = variant.thumbnail
                variant_sku = variant.sku.value
                variant_slug = variant.slug.value
                variant_price = variant.SellingPrice.value
                variant_tax_rate = variant.tax_rate.value
                variant_status = bool(variant.status)

                # Create the ProductVariant in DB
                productvariant_db = ProductVariantModel.objects.create(
                    product=product_db,
                    name=variant_name,
                    description=variant_description,
                    slug=variant_slug,
                    sku=variant_sku,
                    selling_price=variant_price,
                    tax_rate=variant_tax_rate,
                    variantnumber=variant_variantnumber,
                    status=variant_status,
                )

                thumbnail = ProductImage.objects.create(
                    product_variant=productvariant_db,
                    image=variant_thumbnail,
                    image_type="THUMBNAIL",
                    alt_text=f"{productvariant_db.name} - THUMBNAIL",
                )

                # Process images array - convert domain objects to database records
                product_images_list = []

                if variant.images:
                    for img_idx, image in enumerate(variant.images):
                        # Create ProductImage record in DB
                        image_db = ProductImage.objects.create(
                            product_variant=productvariant_db,
                            image=image.url,  # Store the URL string
                            image_type=image.type,  # Use the type from the image object
                            alt_text=f"{productvariant_db.name} - {image.type}",
                            order=img_idx,  # Maintain order of images
                        )

                        # Recreate the domain object from the saved record
                        product_image_entity = ProductImages(
                            type=image_db.image_type,
                            url=image_db.image,  # Use the saved image URL
                        )
                        product_images_list.append(product_image_entity)

                # Store the images array in the variant entity
                variant.images = product_images_list if product_images_list else None

                # Update variant attributes with DB values
                # IMPORTANT: Wrap DB values back into value objects
                variant.attributes.id = productvariant_db.id
                variant.attributes.name = ProductName(productvariant_db.name)
                variant.attributes.description = ProductDescription(
                    productvariant_db.description
                )
                variant.attributes.created_at = CreatedAt(productvariant_db.created_at)
                variant.attributes.updated_at = UpdatedAt(productvariant_db.updated_at)

                # Note: sku and slug are left as strings because they were already extracted as .value
                variant.sku = SKU(productvariant_db.sku)
                variant.slug = Slug(productvariant_db.slug)

                variant.id = productvariant_db.id

        return productentity

    def _build_variant_entity(self, variant_db: ProductVariantModel) -> ProductVariantEntity:
        """
        Helper method to convert a ProductVariantModel to ProductVariantEntity.
        Assumes all related data (images) is already prefetched on variant_db.

        Keeps every non-THUMBNAIL image type (GALLERY, HERO, LIFESTYLE, SIZE,
        COLOR, PACKAGING, OTHER, etc.) in the `images` list. THUMBNAIL is
        pulled out separately since it's exposed as `thumbnail`.
        """
        thumbnail_image = None
        image_list = []

        for img in variant_db.images.all():
            if img.image_type == "THUMBNAIL":
                thumbnail_image = img
            else:
                image_list.append(ProductImages(type=img.image_type, url=img.image))

        product_attributes_normal = ProductAttributesNormal(
            id=variant_db.id,
            name=ProductName(variant_db.name),
            description=ProductDescription(variant_db.description),
            created_at=CreatedAt(variant_db.created_at),
            updated_at=UpdatedAt(variant_db.updated_at),
        )

        return ProductVariantEntity(
            variantnumber=variant_db.variantnumber,
            sku=SKU(variant_db.sku),
            slug=Slug(variant_db.slug),
            images=image_list if image_list else None,
            attributes=product_attributes_normal,
            thumbnail=thumbnail_image.image if thumbnail_image else None,
            status=variant_db.status,
            id=variant_db.id,
            SellingPrice=SellingPrice(variant_db.selling_price),
            tax_rate=TaxRate(variant_db.tax_rate),
        )

    def get_product_by_id(self, product_id: int) -> ProductEntity:
        """
        Retrieve a product by ID and reconstruct it as a ProductEntity with all variants.
        OPTIMIZED: Uses select_related and prefetch_related to avoid N+1 queries.
        """
        # Prefetch all related data at once
        product_db = Product.objects.select_related("category").prefetch_related(
            Prefetch(
                "variants",
                queryset=ProductVariantModel.objects.prefetch_related(
                    Prefetch(
                        "images",
                        queryset=ProductImage.objects.all().order_by("order", "uploaded_at"),
                    )
                ),
            ),
            "tags",  # Prefetch tags for the product
        ).get(id=product_id)

        product_name = ProductName(product_db.name)
        product_category = ProductCategory(product_db.category.slug)
        product_thumbnail = product_db.thumbnail
        product_slug = Slug(product_db.slug)
        product_tags = list(product_db.tags.values_list("name", flat=True))
        created_at = CreatedAt(product_db.created_at)
        updated_at = UpdatedAt(product_db.updated_at)

        variants = [
            self._build_variant_entity(variant_db) for variant_db in product_db.variants.all()
        ]

        product_entity = ProductEntity(
            id=product_db.id,
            name=product_name,
            slug=product_slug,
            category=product_category,
            thumbnail=product_thumbnail,
            tags=product_tags,
            variants=variants,
            created_at=created_at,
            updated_at=updated_at,
        )

        return product_entity

    def get_product_by_slug(self, product_slug: str) -> ProductEntity:
        """
        Retrieve a product by slug and reconstruct it as a ProductEntity with all variants.
        OPTIMIZED: Uses select_related and prefetch_related to avoid N+1 queries.
        """
        # Prefetch all related data at once
        product_db = Product.objects.select_related("category").prefetch_related(
            Prefetch(
                "variants",
                queryset=ProductVariantModel.objects.prefetch_related(
                    Prefetch(
                        "images",
                        queryset=ProductImage.objects.all().order_by("order", "uploaded_at"),
                    )
                ),
            ),
            "tags",
        ).get(slug=product_slug)

        product_name = ProductName(product_db.name)
        product_category = ProductCategory(product_db.category.slug)
        product_thumbnail = product_db.thumbnail
        product_slug = Slug(product_db.slug)
        product_tags = list(product_db.tags.values_list("name", flat=True))
        created_at = CreatedAt(product_db.created_at)
        updated_at = UpdatedAt(product_db.updated_at)

        variants = [
            self._build_variant_entity(variant_db) for variant_db in product_db.variants.all()
        ]

        product_entity = ProductEntity(
            id=product_db.id,
            name=product_name,
            slug=product_slug,
            category=product_category,
            thumbnail=product_thumbnail,
            tags=product_tags,
            variants=variants,
            created_at=created_at,
            updated_at=updated_at,
        )

        return product_entity

    def get_product_via_query(
        self,
        sort: str = None,
        status: bool = None,
        limit: int = None,
        offset: int = None,
        tag: str = None,
        category: str = None,
        search: str = None,
        slug: str = None,
        variantslug: str = None,
    ):
        """
        Get products via query parameters.
        OPTIMIZED: Uses prefetch_related to avoid N+1 queries on variants and images.

        If variantslug is provided, search for products by variant slug and return only those.
        Otherwise, apply standard filters.
        """

        # Handle variantslug separately - it has priority
        if variantslug:
            # Find the variant with the matching slug
            variant_db = ProductVariantModel.objects.select_related("product").prefetch_related(
                Prefetch(
                    "images",
                    queryset=ProductImage.objects.all().order_by("order", "uploaded_at"),
                )
            ).filter(slug=variantslug).first()

            if not variant_db:
                return []  # Return empty list if no variant found

            # Get the product associated with this variant
            product_db = variant_db.product

            # Prefetch all variants and images for the product
            product_db = Product.objects.select_related("category").prefetch_related(
                Prefetch(
                    "variants",
                    queryset=ProductVariantModel.objects.prefetch_related(
                        Prefetch(
                            "images",
                            queryset=ProductImage.objects.all().order_by("order", "uploaded_at"),
                        )
                    ),
                ),
                "tags",
            ).get(id=product_db.id)

            product_name = ProductName(product_db.name)
            product_category = ProductCategory(product_db.category.slug)
            product_thumbnail = product_db.thumbnail
            product_slug = Slug(product_db.slug)
            product_tags = list(product_db.tags.values_list("name", flat=True))
            created_at = CreatedAt(product_db.created_at)
            updated_at = UpdatedAt(product_db.updated_at)

            # Build variants using helper method
            variants = [
                self._build_variant_entity(variant) for variant in product_db.variants.all()
            ]

            # Create and return the product entity
            entity = ProductEntity(
                id=product_db.id,
                name=product_name,
                category=product_category,
                thumbnail=product_thumbnail,
                slug=product_slug,
                tags=product_tags,
                variants=variants,
                created_at=created_at,
                updated_at=updated_at,
            )

            return [entity]  # Return as a list to maintain consistency

        # Standard query logic (existing behavior) - OPTIMIZED
        filter_params = {}
        q_objects = Q()

        if category:
            filter_params["category__slug"] = category

        if tag:
            # TaggableManager search
            filter_params["tags__name__icontains"] = tag

        if slug:
            # If slug is provided, filter by slug that starts with the given value
            filter_params["slug__istartswith"] = slug

        if search:
            q_objects |= Q(name__icontains=search)

        # Apply filters with prefetch_related to avoid N+1 queries
        products = Product.objects.filter(**filter_params).select_related("category").prefetch_related(
            Prefetch(
                "variants",
                queryset=ProductVariantModel.objects.prefetch_related(
                    Prefetch(
                        "images",
                        queryset=ProductImage.objects.all().order_by("order", "uploaded_at"),
                    )
                ),
            ),
            "tags",
        )

        if q_objects:
            products = products.filter(q_objects)

        if sort:
            products = products.order_by(sort)

        if limit:
            if offset:
                products = products[offset : offset + limit]
            else:
                products = products[:limit]

        # Build entities using helper method
        entities = []
        for p in products:
            variant_entities = [
                self._build_variant_entity(variant) for variant in p.variants.all()
            ]

            entity = ProductEntity(
                id=p.id,
                name=ProductName(p.name),
                category=ProductCategory(p.category.slug),
                thumbnail=p.thumbnail,
                slug=Slug(p.slug),
                tags=list(p.tags.values_list("name", flat=True)),
                variants=variant_entities,
                created_at=CreatedAt(p.created_at),
                updated_at=UpdatedAt(p.updated_at),
            )
            entities.append(entity)

        return entities

    def delete_product_by_id(self, product_id: int) -> bool:
        """
        Delete a product by ID along with all its variants and images.
        Returns True if deletion was successful, False if product not found.
        """
        try:
            product_db = Product.objects.get(id=product_id)
            product_db.delete()
            return True
        except Product.DoesNotExist:
            return False

    def update_product(self, product_id: int, data: dict) -> ProductEntity:
        """
        Partially update a product and/or its variants.
        Only fields present in `data` are changed. Variants must include their
        `id` to be matched to an existing row; variants without an id are skipped.
        """
        try:
            product_db = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValueError(f"Product with id {product_id} does not exist")

        # --- Top-level product fields ---
        if "name" in data:
            product_db.name = ProductName(str(data["name"])).value
        if "category" in data:
            category_slug = ProductCategory(data["category"]).value
            product_db.category = Category.objects.get(slug=category_slug)
        if "slug" in data:
            product_db.slug = Slug(data["slug"]).value
        if "thumbnail" in data:
            product_db.thumbnail = data["thumbnail"]
        if "tags" in data:
            tags_value = Tags(data["tags"]).value if data["tags"] else []
            product_db.tags.set(tags_value)

        product_db.save()

        # --- Variants (matched by id, partial per-variant update) ---
        if "variants" in data:
            for variant_data in data["variants"]:
                variant_id = variant_data.get("id")
                if not variant_id:
                    continue  # PATCH only touches existing variants

                try:
                    variant_db = ProductVariantModel.objects.get(
                        id=variant_id, product=product_db
                    )
                except ProductVariantModel.DoesNotExist:
                    continue

                if "name" in variant_data:
                    variant_db.name = ProductName(str(variant_data["name"])).value
                if "description" in variant_data:
                    variant_db.description = ProductDescription(
                        str(variant_data["description"])
                    ).value
                if "variantnumber" in variant_data:
                    variant_db.variantnumber = variant_data["variantnumber"]
                if "slug" in variant_data:
                    variant_db.slug = Slug(variant_data["slug"]).value
                if "sku" in variant_data:
                    variant_db.sku = SKU(variant_data["sku"]).value
                if "selling_price" in variant_data:
                    variant_db.selling_price = SellingPrice(
                        Decimal(str(variant_data["selling_price"]))
                    ).value
                if "tax_rate" in variant_data:
                    variant_db.tax_rate = TaxRate(
                        Decimal(str(variant_data["tax_rate"]))
                    ).value
                # status is derived from stock (see inventory/signals.py),
                # never accepted from the client.

                variant_db.save()

                # thumbnail is stored as its own ProductImage row.
                # NOTE: update_or_create() does an internal get(), which
                # raises MultipleObjectsReturned if duplicate THUMBNAIL rows
                # already exist for this variant (possible from data created
                # before this was guarded against). Collapse to a single row
                # explicitly so this can never crash.
                if "thumbnail" in variant_data:
                    existing_thumbnails = list(
                        ProductImage.objects.filter(
                            product_variant=variant_db,
                            image_type="THUMBNAIL",
                        ).order_by("-uploaded_at")
                    )

                    if len(existing_thumbnails) > 1:
                        # Keep the most recently uploaded row, drop the rest
                        stale_ids = [img.id for img in existing_thumbnails[1:]]
                        ProductImage.objects.filter(id__in=stale_ids).delete()
                        existing_thumbnails = existing_thumbnails[:1]

                    if existing_thumbnails:
                        thumb = existing_thumbnails[0]
                        thumb.image = variant_data["thumbnail"]
                        thumb.alt_text = f"{variant_db.name} - THUMBNAIL"
                        thumb.save(update_fields=["image", "alt_text"])
                    else:
                        ProductImage.objects.create(
                            product_variant=variant_db,
                            image=variant_data["thumbnail"],
                            image_type="THUMBNAIL",
                            alt_text=f"{variant_db.name} - THUMBNAIL",
                        )

                # Replace gallery/other images wholesale if provided
                if "images" in variant_data:
                    ProductImage.objects.filter(
                        product_variant=variant_db
                    ).exclude(image_type="THUMBNAIL").delete()

                    for img_idx, image_data in enumerate(variant_data["images"]):
                        img_type = image_data.get("type", "GALLERY")

                        # The thumbnail is managed exclusively via the
                        # dedicated `thumbnail` field above (update_or_create
                        # on image_type="THUMBNAIL"). Skip any THUMBNAIL
                        # entries coming from the images array to avoid
                        # creating a duplicate/orphan THUMBNAIL row that
                        # would silently disappear from `images` on the
                        # next read (see _build_variant_entity).
                        if img_type == "THUMBNAIL":
                            continue

                        ProductImage.objects.create(
                            product_variant=variant_db,
                            image=image_data.get("url"),
                            image_type=img_type,
                            alt_text=f"{variant_db.name} - {img_type}",
                            order=img_idx,
                        )

        # Re-hydrate a fresh, fully-loaded entity to return
        return self.get_product_by_id(product_id)
