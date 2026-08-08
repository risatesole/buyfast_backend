"""
This view imports products from the CSV export produced by the store's product
spreadsheet ("Products - Sheet1.csv"). One row = one product variant. Rows that
share the same `product_slug` are grouped together and treated as variants of
the same product.

example csv:
SKU,initial inventory,selling_price,tax_rate,total_price,product_name,product_slug,category,product_type,variant_atribute,variant_name,variant_description,variant_slug,variant_status,image_thumbnail,image_thumbnail_alt_text,image_01,image_01_alt_text,image_02,image_02_alt_text,image_03,image_03_alt_text,image_04,image_04_alt_text
ARC-4P-001,100,500,0.05,525,Archivador Carta,archivador-carta,papeleria,normal,4 Pulgadas,Archivador Carta - 4 Pulgadas,Archivador resistente tamaño carta,archivador-4-pulgadas,TRUE,https://example.com/thumb.jpg,imagen del thumbnail,https://example.com/img1.jpg,imagen 1,https://example.com/img2.jpg,imagen 2,,,,
ARC-8P-001,100,700,0.05,735,Archivador Carta,archivador-carta,papeleria,normal,8 Pulgadas,Archivador Carta - 8 Pulgadas,Archivador resistente tamaño carta,archivador-8-pulgadas,TRUE,https://example.com/thumb.jpg,imagen del thumbnail,https://example.com/img1.jpg,imagen 1,,,,,,

Notes on this format, compared to a "classic" product-import CSV:
    - The variant SKU column is simply called `SKU` (not `variant_sku`).
    - There is no `variant_number` column. A variant number is instead
      auto-assigned (per product) in the order variants are first created.
    - There is no product-level `thumbnail` or `tags` column.
    - There IS a `variant_atribute` column (e.g. "Rojo", "4 Pulgadas", "Talla M")
      which is stored on ProductVariant.attribute.
    - `category` / `product_type` use the Spanish slugs from the spreadsheet
      (e.g. "papeleria", "normal") instead of the internal model codes
      (e.g. "stationery", "physical"). Both the Spanish spreadsheet values and
      the internal model codes are accepted - see CATEGORY_ALIASES / TYPE_ALIASES.
    - Instead of one `image_url` / `image_type` / `image_alt_text` / `image_order`
      set of columns, there are up to five image "slots" per row:
      image_thumbnail, image_01, image_02, image_03, image_04 (each with a
      matching `_alt_text` column). Any slot left blank is skipped.
    - `initial inventory` (quantity) is used to create the opening stock
      movement for newly created variants via the `inventory` app.
    - `total_price` is informational only (selling_price + tax) and is not
      stored anywhere; it is not validated against selling_price/tax_rate.

Column headers are matched case-insensitively and with spaces/hyphens treated
as underscores, so "SKU", "sku", "initial inventory" and "Initial Inventory"
all work.
"""
import csv
import logging
from decimal import Decimal, InvalidOperation
from io import TextIOWrapper
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict

from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Max

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from products.default.models.product_model import Product
from products.default.models.product_category_model import Category
from products.default.models.product_variant_model import ProductVariant
from products.default.models.product_image_model import ProductImage
from inventory.inventory import create_initial_inventory
from taggit.models import Tag

logger = logging.getLogger(__name__)


def is_employee(user):
    """Check if user has employee role."""
    return user.is_authenticated and user.role == 'employee'


# ========== HEADER / VALUE NORMALIZATION ==========

def normalize_header(header: str) -> str:
    """Normalize a CSV header so 'SKU', 'sku', 'initial inventory', etc. all match."""
    return header.strip().lower().replace(' ', '_').replace('-', '_')


# Spanish spreadsheet category slugs -> internal Category slugs.
# Internal slugs are also accepted as-is (identity mapping).
CATEGORY_ALIASES = {
    'papeleria': 'stationery',
    'libros_manuales': 'books_manuals',
    'laboratorio_medicina': 'medical_lab',
    'medicina_laboratorio': 'medical_lab',
    'arquitectura_arte': 'architecture_arts',
    'arquitectura_artes': 'architecture_arts',
    'electronicos': 'electronics',
    'electronica': 'electronics',
    'uniformes': 'uniforms',
    'snacks_bebidas': 'snacks_beverages',
    'bebidas_snacks': 'snacks_beverages',
}

# Spanish spreadsheet product-type slugs -> internal Product.ProductType values.
TYPE_ALIASES = {
    'normal': Product.ProductType.PHYSICAL,
    'fisico': Product.ProductType.PHYSICAL,
    'físico': Product.ProductType.PHYSICAL,
    'digital': Product.ProductType.DIGITAL,
    'servicio': Product.ProductType.SERVICE,
}


def normalize_category(raw_value: str) -> Optional[str]:
    """Map a raw CSV category value to an internal Category slug."""
    value = (raw_value or '').strip().lower()
    if not value:
        return None
    valid_categories = set(Category.objects.values_list('slug', flat=True))
    if value in valid_categories:
        return value
    return CATEGORY_ALIASES.get(value)


def normalize_product_type(raw_value: str) -> Optional[str]:
    """Map a raw CSV product_type value to an internal Product.ProductType value."""
    value = (raw_value or '').strip().lower()
    if not value:
        return None
    valid_types = {choice[0] for choice in Product.ProductType.choices}
    if value in valid_types:
        return value
    return TYPE_ALIASES.get(value)


# Each image "slot" in the CSV: (url_column, alt_text_column, image_type, default_order)
IMAGE_SLOTS = [
    ('image_thumbnail', 'image_thumbnail_alt_text', ProductImage.ImageType.THUMBNAIL, 0),
    ('image_01', 'image_01_alt_text', ProductImage.ImageType.HERO, 1),
    ('image_02', 'image_02_alt_text', ProductImage.ImageType.GALLERY, 2),
    ('image_03', 'image_03_alt_text', ProductImage.ImageType.GALLERY, 3),
    ('image_04', 'image_04_alt_text', ProductImage.ImageType.GALLERY, 4),
]

REQUIRED_FIELDS = [
    'product_name', 'product_slug', 'category', 'product_type',
    'variant_name', 'variant_slug', 'sku', 'selling_price',
]


def validate_csv_headers(headers: List[str]) -> Tuple[bool, List[str]]:
    """Validate CSV has all required columns (header names are normalized first)."""
    normalized = {normalize_header(h) for h in headers}
    missing = set(REQUIRED_FIELDS) - normalized
    if missing:
        return False, [f"Missing required columns: {', '.join(sorted(missing))}"]

    return True, []


def validate_product_row(row: Dict[str, str], row_num: int) -> List[Dict[str, Any]]:
    """
    Validate individual (already header-normalized) row data.
    Returns list of error dicts with field and message.
    """
    errors = []

    for field in REQUIRED_FIELDS:
        if not row.get(field, '').strip():
            errors.append({
                'field': field,
                'message': f'{field} is required and cannot be empty',
                'row': row_num
            })

    # Check product_name length
    if row.get('product_name', '').strip():
        if len(row['product_name'].strip()) > 255:
            errors.append({
                'field': 'product_name',
                'message': f'Product name exceeds 255 characters: {len(row["product_name"])}',
                'row': row_num
            })

    # Check product_slug format
    product_slug = row.get('product_slug', '').strip().lower()
    if product_slug:
        if ' ' in product_slug:
            errors.append({
                'field': 'product_slug',
                'message': 'Product slug cannot contain spaces',
                'row': row_num
            })
        if not product_slug.replace('-', '').replace('_', '').isalnum():
            errors.append({
                'field': 'product_slug',
                'message': 'Product slug can only contain letters, numbers, hyphens and underscores',
                'row': row_num
            })

    # Check category (accepts either the Spanish spreadsheet slug or the internal code)
    if row.get('category', '').strip():
        if normalize_category(row['category']) is None:
            valid_categories = list(Category.objects.values_list('slug', flat=True))
            errors.append({
                'field': 'category',
                'message': (
                    f"Invalid category '{row['category']}'. Must be one of: "
                    f"{', '.join(valid_categories)} (or one of their spreadsheet aliases: "
                    f"{', '.join(sorted(CATEGORY_ALIASES.keys()))})"
                ),
                'row': row_num
            })

    # Check product type (accepts either the Spanish spreadsheet slug or the internal code)
    if row.get('product_type', '').strip():
        if normalize_product_type(row['product_type']) is None:
            valid_types = [choice[0] for choice in Product.ProductType.choices]
            errors.append({
                'field': 'product_type',
                'message': (
                    f"Invalid product type '{row['product_type']}'. Must be one of: "
                    f"{', '.join(valid_types)} (or one of their spreadsheet aliases: "
                    f"{', '.join(sorted(TYPE_ALIASES.keys()))})"
                ),
                'row': row_num
            })

    # Check selling price
    if row.get('selling_price'):
        try:
            price = Decimal(row.get('selling_price', '0'))
            if price < 0:
                errors.append({
                    'field': 'selling_price',
                    'message': f'Selling price cannot be negative: {price}',
                    'row': row_num
                })
            if price > 99999999.99:
                errors.append({
                    'field': 'selling_price',
                    'message': f'Selling price too high (max 99,999,999.99): {price}',
                    'row': row_num
                })
        except Exception:
            errors.append({
                'field': 'selling_price',
                'message': f'Invalid selling price format: {row.get("selling_price")}',
                'row': row_num
            })

    # Check variant slug format
    variant_slug = row.get('variant_slug', '').strip()
    if variant_slug:
        if ' ' in variant_slug:
            errors.append({
                'field': 'variant_slug',
                'message': 'Variant slug cannot contain spaces',
                'row': row_num
            })
        if not variant_slug.replace('-', '').replace('_', '').isalnum():
            errors.append({
                'field': 'variant_slug',
                'message': 'Variant slug can only contain letters, numbers, hyphens and underscores',
                'row': row_num
            })

    # Check SKU format
    sku = row.get('sku', '').strip()
    if sku:
        if len(sku) > 500:
            errors.append({
                'field': 'sku',
                'message': f'SKU exceeds 500 characters: {len(sku)}',
                'row': row_num
            })
        if ' ' in sku:
            errors.append({
                'field': 'sku',
                'message': 'SKU cannot contain spaces',
                'row': row_num
            })

    # Check tax rate (optional) - accept both formats
    if row.get('tax_rate', '').strip():
        try:
            tax = Decimal(row.get('tax_rate', '0'))
            if tax < 0:
                errors.append({
                    'field': 'tax_rate',
                    'message': f'Tax rate cannot be negative: {tax}',
                    'row': row_num
                })
            elif tax > 100:
                errors.append({
                    'field': 'tax_rate',
                    'message': f'Tax rate too high (max 100%): {tax}%',
                    'row': row_num
                })
        except (ValueError, TypeError, InvalidOperation):
            errors.append({
                'field': 'tax_rate',
                'message': f'Invalid tax rate format: {row.get("tax_rate")}',
                'row': row_num
            })

    # Check initial inventory (optional)
    if row.get('initial_inventory', '').strip():
        try:
            qty = int(row['initial_inventory'])
            if qty < 0:
                errors.append({
                    'field': 'initial_inventory',
                    'message': f'Initial inventory cannot be negative: {qty}',
                    'row': row_num
                })
        except (ValueError, TypeError):
            errors.append({
                'field': 'initial_inventory',
                'message': f'Invalid initial inventory: {row.get("initial_inventory")}',
                'row': row_num
            })

    # Check image URLs for each image slot, if provided
    for url_field, alt_field, _image_type, _order in IMAGE_SLOTS:
        image_url = row.get(url_field, '').strip()
        if image_url:
            if len(image_url) > 2000:
                errors.append({
                    'field': url_field,
                    'message': f'Image URL exceeds 2000 characters: {len(image_url)}',
                    'row': row_num
                })
            if not image_url.startswith(('http://', 'https://')):
                errors.append({
                    'field': url_field,
                    'message': f'Image URL must start with http:// or https://: {image_url[:50]}...',
                    'row': row_num
                })

    return errors


def process_row_with_validation(row: Dict[str, str], row_num: int) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Convert a header-normalized CSV row to model data with validation.
    Returns (data_dict, errors_list)
    """
    errors = validate_product_row(row, row_num)

    # Parse variant status
    status = row.get('variant_status', 'TRUE').upper()
    is_active = status in ['TRUE', '1', 'YES', 'ACTIVE']

    # Handle tax rate - convert percentage to decimal if needed
    tax_rate_raw = row.get('tax_rate', '').strip()
    if tax_rate_raw:
        try:
            tax_decimal = Decimal(tax_rate_raw)
            # If value > 1, treat as percentage (18.00 -> 0.18)
            if tax_decimal > 1:
                tax_decimal = tax_decimal / 100
            elif tax_decimal > 100:
                errors.append({
                    'field': 'tax_rate',
                    'message': f'Tax rate too high: {tax_rate_raw}% (max 100%)',
                    'row': row_num
                })
                tax_decimal = Decimal('0')
        except (ValueError, TypeError, InvalidOperation):
            tax_decimal = Decimal('0')
    else:
        tax_decimal = Decimal('0')

    # Selling price / initial inventory (safe fallbacks if validation already flagged them)
    try:
        selling_price = Decimal(row.get('selling_price', '0') or '0')
    except Exception:
        selling_price = Decimal('0')

    try:
        initial_inventory = int(row.get('initial_inventory', '').strip()) if row.get('initial_inventory', '').strip() else 0
    except (ValueError, TypeError):
        initial_inventory = 0

    # Collect the (up to 5) images defined for this row
    images = []
    for url_field, alt_field, image_type, default_order in IMAGE_SLOTS:
        image_url = row.get(url_field, '').strip()
        if image_url:
            images.append({
                'image_url': image_url,
                'image_type': image_type,
                'image_alt_text': row.get(alt_field, '').strip(),
                'image_order': default_order,
            })

    data = {
        'product_name': row.get('product_name', '').strip(),
        'product_slug': row.get('product_slug', '').strip().lower(),
        'category': normalize_category(row.get('category', '')) or row.get('category', '').strip(),
        'product_type': normalize_product_type(row.get('product_type', '')) or row.get('product_type', '').strip(),
        # There's no product-level thumbnail column in this format - fall back to the
        # variant's own thumbnail image so the product still gets a usable thumbnail.
        'thumbnail': row.get('image_thumbnail', '').strip(),
        'tags': [t.strip() for t in row.get('tags', '').split(',') if t.strip()],

        'variant_name': row.get('variant_name', '').strip(),
        'variant_description': row.get('variant_description', '').strip(),
        'variant_attribute': (row.get('variant_atribute') or row.get('variant_attribute') or '').strip(),
        'variant_slug': row.get('variant_slug', '').strip(),
        'variant_sku': row.get('sku', '').strip(),
        'variant_status': is_active,
        'selling_price': selling_price,
        'tax_rate': tax_decimal,
        'initial_inventory': initial_inventory,

        'images': images,
    }

    return data, errors


def check_duplicate_variant_skus(rows_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Check for duplicate variant SKUs within the CSV data."""
    errors = []
    seen_skus = {}

    for row in rows_data:
        sku = row['variant_sku']
        if sku in seen_skus:
            errors.append({
                'field': 'sku',
                'message': f"Duplicate SKU '{sku}' found in CSV.",
                'row': row.get('_row_num', 'unknown'),
                'duplicate_row': seen_skus[sku]
            })
        else:
            seen_skus[sku] = row.get('_row_num', 'unknown')

    return errors


def check_existing_product_slugs(rows_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Check if product slugs already exist in database. This is a warning, not an error."""
    warnings = []
    slugs = [row['product_slug'] for row in rows_data]

    existing_products = Product.objects.filter(slug__in=slugs).values('slug', 'name')
    existing_slugs = {p['slug']: p['name'] for p in existing_products}

    for row in rows_data:
        if row['product_slug'] in existing_slugs:
            warnings.append({
                'field': 'product_slug',
                'message': f"Product slug '{row['product_slug']}' already exists in database (product: {existing_slugs[row['product_slug']]}). Will be updated.",
                'row': row.get('_row_num', 'unknown'),
                'warning': True
            })

    return warnings


def check_existing_variant_skus(rows_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Check if variant SKUs already exist in database."""
    warnings = []
    skus = [row['variant_sku'] for row in rows_data]

    existing_variants = ProductVariant.objects.filter(sku__in=skus).values('sku', 'name')
    existing_skus = {v['sku']: v['name'] for v in existing_variants}

    for row in rows_data:
        if row['variant_sku'] in existing_skus:
            warnings.append({
                'field': 'sku',
                'message': f"SKU '{row['variant_sku']}' already exists in database (variant: {existing_skus[row['variant_sku']]}). Will be updated.",
                'row': row.get('_row_num', 'unknown'),
                'warning': True
            })

    return warnings


def check_variant_slug_uniqueness(rows_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Check for duplicate variant slugs within the same product."""
    errors = []
    product_variants = defaultdict(list)

    for row in rows_data:
        product_slug = row['product_slug']
        variant_slug = row['variant_slug']
        product_variants[product_slug].append({
            'variant_slug': variant_slug,
            'row': row.get('_row_num', 'unknown'),
            'sku': row['variant_sku']
        })

    for product_slug, variants in product_variants.items():
        seen_slugs = {}
        for variant in variants:
            slug = variant['variant_slug']
            if slug in seen_slugs:
                errors.append({
                    'field': 'variant_slug',
                    'message': f"Duplicate variant slug '{slug}' for product '{product_slug}'. Variants must have unique slugs within a product.",
                    'row': variant['row'],
                    'duplicate_row': seen_slugs[slug]['row']
                })
            else:
                seen_slugs[slug] = variant

    return errors


def check_variant_slug_db_conflict(rows_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Check if variant slugs already exist in database for the same product."""
    warnings = []

    product_slugs = set(row['product_slug'] for row in rows_data)
    existing_products = {p.slug: p for p in Product.objects.filter(slug__in=product_slugs)}

    for row in rows_data:
        product = existing_products.get(row['product_slug'])
        if product:
            variant_exists = ProductVariant.objects.filter(
                product=product,
                slug=row['variant_slug']
            ).exclude(sku=row['variant_sku']).exists()

            if variant_exists:
                warnings.append({
                    'field': 'variant_slug',
                    'message': f"Variant slug '{row['variant_slug']}' already exists for product '{row['product_slug']}' in database.",
                    'row': row.get('_row_num', 'unknown'),
                    'warning': True
                })

    return warnings


def get_or_create_product(product_data: Dict[str, Any]) -> Tuple[Product, bool, List[Dict[str, Any]]]:
    """Get or create product from validated data."""
    errors = []

    try:
        category = Category.objects.get(slug=product_data['category'])

        product, created = Product.objects.get_or_create(
            slug=product_data['product_slug'],
            defaults={
                'name': product_data['product_name'],
                'category': category,
                'product_type': product_data['product_type'],
                'thumbnail': product_data.get('thumbnail', ''),
            }
        )

        # Update product fields if it already exists
        if not created:
            updated = False
            if product.name != product_data['product_name']:
                product.name = product_data['product_name']
                updated = True
            if product.category_id != category.id:
                product.category = category
                updated = True
            if product.product_type != product_data['product_type']:
                product.product_type = product_data['product_type']
                updated = True
            if product_data.get('thumbnail') and product.thumbnail != product_data['thumbnail']:
                product.thumbnail = product_data['thumbnail']
                updated = True

            if updated:
                product.save()
        elif not product.thumbnail and product_data.get('thumbnail'):
            product.thumbnail = product_data['thumbnail']
            product.save(update_fields=['thumbnail'])

        # Handle tags (optional - this CSV format usually won't have any)
        if product_data.get('tags'):
            for tag_name in product_data['tags']:
                try:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    product.tags.add(tag)
                except Exception as e:
                    errors.append({
                        'field': 'tags',
                        'message': f"Error adding tag '{tag_name}': {str(e)}",
                        'row': product_data.get('_row_num', 'unknown')
                    })

        return product, created, errors

    except ValidationError as e:
        errors.append({
            'field': 'product',
            'message': f"Validation error: {str(e)}",
            'row': product_data.get('_row_num', 'unknown')
        })
        return None, False, errors
    except Exception as e:
        errors.append({
            'field': 'product',
            'message': f"Error creating product: {str(e)}",
            'row': product_data.get('_row_num', 'unknown')
        })
        return None, False, errors


def get_or_create_variant(product: Product, variant_data: Dict[str, Any]) -> Tuple[ProductVariant, bool, List[Dict[str, Any]]]:
    """
    Get or create product variant from validated data.

    There's no `variant_number` column in this CSV format, so when a new
    variant is created its number is auto-assigned as
    (current max variantnumber for this product) + 1.
    """
    errors = []

    try:
        existing = ProductVariant.objects.filter(sku=variant_data['variant_sku']).first()

        if existing is None:
            next_number = (
                ProductVariant.objects.filter(product=product)
                .aggregate(Max('variantnumber'))
                .get('variantnumber__max') or 0
            ) + 1

            variant = ProductVariant.objects.create(
                product=product,
                name=variant_data['variant_name'],
                description=variant_data.get('variant_description', ''),
                attribute=variant_data.get('variant_attribute', ''),
                variantnumber=next_number,
                slug=variant_data['variant_slug'],
                sku=variant_data['variant_sku'],
                selling_price=variant_data['selling_price'],
                tax_rate=variant_data.get('tax_rate', Decimal('0')),
                status=variant_data['variant_status'],
            )
            created = True

            # Record the opening stock movement for the new variant
            initial_qty = variant_data.get('initial_inventory', 0)
            if initial_qty:
                try:
                    create_initial_inventory(variant.id, initial_qty)
                except Exception as e:
                    errors.append({
                        'field': 'initial_inventory',
                        'message': f"Error creating initial inventory for SKU '{variant.sku}': {str(e)}",
                        'row': variant_data.get('_row_num', 'unknown')
                    })
        else:
            variant = existing
            created = False
            updated = False
            if variant.name != variant_data['variant_name']:
                variant.name = variant_data['variant_name']
                updated = True
            if variant.description != variant_data.get('variant_description', ''):
                variant.description = variant_data.get('variant_description', '')
                updated = True
            if variant.attribute != variant_data.get('variant_attribute', ''):
                variant.attribute = variant_data.get('variant_attribute', '')
                updated = True
            if variant.slug != variant_data['variant_slug']:
                variant.slug = variant_data['variant_slug']
                updated = True
            if variant.selling_price != variant_data['selling_price']:
                variant.selling_price = variant_data['selling_price']
                updated = True
            if variant.tax_rate != variant_data.get('tax_rate', Decimal('0')):
                variant.tax_rate = variant_data.get('tax_rate', Decimal('0'))
                updated = True
            if variant.status != variant_data['variant_status']:
                variant.status = variant_data['variant_status']
                updated = True
            if variant.product_id != product.id:
                variant.product = product
                updated = True

            if updated:
                variant.save()

        return variant, created, errors

    except ValidationError as e:
        errors.append({
            'field': 'variant',
            'message': f"Validation error: {str(e)}",
            'row': variant_data.get('_row_num', 'unknown')
        })
        return None, False, errors
    except Exception as e:
        errors.append({
            'field': 'variant',
            'message': f"Error creating variant: {str(e)}",
            'row': variant_data.get('_row_num', 'unknown')
        })
        return None, False, errors


def sync_variant_images(variant: ProductVariant, variant_data: Dict[str, Any]) -> Tuple[int, int, List[Dict[str, Any]]]:
    """
    Create/update all images (from the image_thumbnail/image_01.../image_04 slots)
    for a variant. Returns (created_count, updated_count, errors).
    """
    errors = []
    created_count = 0
    updated_count = 0

    for image_data in variant_data.get('images', []):
        try:
            image, created = ProductImage.objects.get_or_create(
                product_variant=variant,
                image=image_data['image_url'],
                defaults={
                    'image_type': image_data.get('image_type', ProductImage.ImageType.HERO),
                    'alt_text': image_data.get('image_alt_text', ''),
                    'order': image_data.get('image_order', 0),
                }
            )

            if created:
                created_count += 1
            else:
                updated = False
                if image.image_type != image_data.get('image_type', ProductImage.ImageType.HERO):
                    image.image_type = image_data.get('image_type', ProductImage.ImageType.HERO)
                    updated = True
                if image.alt_text != image_data.get('image_alt_text', ''):
                    image.alt_text = image_data.get('image_alt_text', '')
                    updated = True
                if image.order != image_data.get('image_order', 0):
                    image.order = image_data.get('image_order', 0)
                    updated = True
                if updated:
                    image.save()
                    updated_count += 1

        except Exception as e:
            errors.append({
                'field': 'image',
                'message': f"Error creating image: {str(e)}",
                'row': variant_data.get('_row_num', 'unknown')
            })

    return created_count, updated_count, errors


# ========== DRF VIEW ==========

class ImportProductsCSVView(APIView):
    """
    Import products from the store's product spreadsheet CSV export.
    Only accessible to users with 'employee' role.

    One CSV row = one product variant. Rows sharing the same `product_slug`
    become variants of the same product.

    ## Required CSV Columns:
    - SKU: Unique SKU for the variant (max 500 chars)
    - product_name: Name of the product (max 255 chars)
    - product_slug: Unique slug identifier (alphanumeric with - and _)
    - category: papeleria, libros_manuales, laboratorio_medicina,
      arquitectura_arte, electronicos, uniformes (or the internal codes:
      stationery, books_manuals, medical_lab, architecture_arts, electronics,
      uniforms, snacks_beverages)
    - product_type: normal (or the internal codes: physical, digital, service)
    - variant_name: Name of the variant (max 500 chars)
    - variant_slug: Unique slug for the variant (alphanumeric with - and _)
    - selling_price: Decimal price (e.g., 29.99)

    ## Optional CSV Columns:
    - initial inventory: Opening stock quantity for newly created variants
    - tax_rate: Tax rate (accepts 18 or 0.18 format)
    - total_price: Informational only, not stored
    - variant_atribute: The variant's distinguishing attribute (e.g. "Rojo", "4 Pulgadas")
    - variant_description: Description of the variant
    - variant_status: TRUE/FALSE (defaults to TRUE)
    - image_thumbnail / image_thumbnail_alt_text
    - image_01 / image_01_alt_text
    - image_02 / image_02_alt_text
    - image_03 / image_03_alt_text
    - image_04 / image_04_alt_text
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        """Upload and import CSV file."""
        if request.user.role != 'employee':
            return Response(
                {
                    'success': False,
                    'error': f'Only employees can import products. Your role: {request.user.role}'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if 'file' not in request.FILES:
            return Response({
                'success': False,
                'error': 'No file uploaded. Please provide a file with key "file".'
            }, status=status.HTTP_400_BAD_REQUEST)

        csv_file = request.FILES['file']

        if not csv_file.name.endswith('.csv'):
            return Response({
                'success': False,
                'error': f'File must be a CSV. Got: {csv_file.name}'
            }, status=status.HTTP_400_BAD_REQUEST)

        max_size = 10 * 1024 * 1024
        if csv_file.size > max_size:
            return Response({
                'success': False,
                'error': f'File too large. Maximum size is {max_size / 1024 / 1024}MB'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_file = TextIOWrapper(csv_file, encoding='utf-8-sig')
            reader = csv.DictReader(decoded_file)

            raw_fieldnames = reader.fieldnames or []
            valid, header_errors = validate_csv_headers(raw_fieldnames)
            if not valid:
                return Response({
                    'success': False,
                    'errors': header_errors
                }, status=status.HTTP_400_BAD_REQUEST)

            # Map from normalized header -> original header, so every row's keys
            # get normalized the same way the header validation did.
            header_map = {normalize_header(h): h for h in raw_fieldnames}

            rows_data = []
            validation_errors = []

            for row_num, raw_row in enumerate(reader, start=2):
                row = {
                    normalized: (raw_row.get(original) or '')
                    for normalized, original in header_map.items()
                }
                data, errors = process_row_with_validation(row, row_num)
                data['_row_num'] = row_num
                if errors:
                    validation_errors.extend(errors)
                rows_data.append(data)

            if validation_errors:
                errors_by_row = defaultdict(list)
                for error in validation_errors:
                    errors_by_row[error.get('row', 'unknown')].append(error)

                return Response({
                    'success': False,
                    'error': f'Validation errors found in CSV ({len(validation_errors)} errors)',
                    'validation_errors': validation_errors,
                    'errors_by_row': dict(errors_by_row),
                    'total_rows_processed': len(rows_data),
                    'rows_with_errors': len(errors_by_row)
                }, status=status.HTTP_400_BAD_REQUEST)

            # Additional CSV-level validations
            # NOTE: Duplicate product slugs are ALLOWED (multiple variants per product)
            csv_errors = []
            csv_errors.extend(check_duplicate_variant_skus(rows_data))
            csv_errors.extend(check_variant_slug_uniqueness(rows_data))

            db_warnings = []
            db_warnings.extend(check_existing_product_slugs(rows_data))
            db_warnings.extend(check_existing_variant_skus(rows_data))
            db_warnings.extend(check_variant_slug_db_conflict(rows_data))

            csv_errors_only = [e for e in csv_errors if not e.get('warning', False)]
            csv_warnings = [e for e in csv_errors if e.get('warning', False)]
            db_warnings_only = [e for e in db_warnings if e.get('warning', False)]

            if csv_errors_only:
                errors_by_row = defaultdict(list)
                for error in csv_errors_only:
                    errors_by_row[error.get('row', 'unknown')].append(error)

                return Response({
                    'success': False,
                    'error': f'CSV structure errors found ({len(csv_errors_only)} errors)',
                    'validation_errors': csv_errors_only,
                    'errors_by_row': dict(errors_by_row),
                    'warnings': csv_warnings + db_warnings_only,
                }, status=status.HTTP_400_BAD_REQUEST)

            stats = {
                'products_created': 0,
                'products_updated': 0,
                'variants_created': 0,
                'variants_updated': 0,
                'images_created': 0,
                'images_updated': 0,
                'total_rows': len(rows_data),
                'errors': [],
                'warnings': csv_warnings + db_warnings_only
            }

            product_groups = defaultdict(list)
            for row in rows_data:
                product_groups[row['product_slug']].append(row)

            with transaction.atomic():
                for product_slug, rows in product_groups.items():
                    try:
                        product_row = rows[0]
                        product, product_created, product_errors = get_or_create_product(product_row)

                        if product_errors:
                            stats['errors'].extend(product_errors)
                        if product is None:
                            continue

                        if product_created:
                            stats['products_created'] += 1
                        else:
                            stats['products_updated'] += 1

                        for variant_row in rows:
                            variant, variant_created, variant_errors = get_or_create_variant(
                                product, variant_row
                            )

                            if variant_errors:
                                stats['errors'].extend(variant_errors)
                            if variant is None:
                                continue

                            if variant_created:
                                stats['variants_created'] += 1
                            else:
                                stats['variants_updated'] += 1

                            if variant_row.get('images'):
                                images_created, images_updated, image_errors = sync_variant_images(
                                    variant, variant_row
                                )
                                stats['images_created'] += images_created
                                stats['images_updated'] += images_updated
                                if image_errors:
                                    stats['errors'].extend(image_errors)

                    except Exception as e:
                        error_msg = {
                            'field': 'product',
                            'message': f"Error processing product {product_slug}: {str(e)}",
                            'row': rows[0].get('_row_num', 'unknown')
                        }
                        stats['errors'].append(error_msg)
                        logger.error(f"Error processing product {product_slug}: {str(e)}", exc_info=True)

            response_data = {
                'success': len(stats['errors']) == 0,
                'stats': {
                    'products_created': stats['products_created'],
                    'products_updated': stats['products_updated'],
                    'variants_created': stats['variants_created'],
                    'variants_updated': stats['variants_updated'],
                    'images_created': stats['images_created'],
                    'images_updated': stats['images_updated'],
                    'total_rows': stats['total_rows'],
                }
            }

            if stats['warnings']:
                response_data['warnings'] = stats['warnings']
                response_data['warning_count'] = len(stats['warnings'])

            if stats['errors']:
                response_data['errors'] = stats['errors']
                response_data['error_count'] = len(stats['errors'])
                response_data['partial_success'] = True
                return Response(response_data, status=status.HTTP_207_MULTI_STATUS)

            return Response(response_data, status=status.HTTP_201_CREATED)

        except UnicodeDecodeError:
            return Response({
                'success': False,
                'error': 'File encoding error. Please ensure the file is UTF-8 encoded.'
            }, status=status.HTTP_400_BAD_REQUEST)
        except csv.Error as e:
            return Response({
                'success': False,
                'error': f'CSV parsing error: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in import_products_csv: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
