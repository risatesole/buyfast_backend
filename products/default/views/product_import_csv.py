"""
example csv:
product_name,product_slug,category,product_type,thumbnail,tags,variant_name,variant_description,variant_number,variant_slug,variant_sku,selling_price,tax_rate,variant_status,image_url,image_type,image_alt_text,image_order
"Scientific Calculator FX-991","scientific-calculator-fx-991","electronics","physical","https://example.com/thumb-calculator.jpg","calculator,scientific,engineering,uasd","Black Edition","High precision scientific calculator with 991 functions",1,"fx991-black-edition","FX991-BLK",45.99,18.00,TRUE,"https://example.com/calculator-hero.jpg","HERO","Scientific Calculator front view",1
"Scientific Calculator FX-991","scientific-calculator-fx-991","electronics","physical","https://example.com/thumb-calculator.jpg","calculator,scientific,engineering,uasd","Blue Edition","High precision scientific calculator with 991 functions",2,"fx991-blue-edition","FX991-BLU",47.99,0.18,TRUE,"https://example.com/calculator-detail1.jpg","DETAIL","Side view with buttons",2
"Introduction to Economics","intro-to-economics","books_manuals","physical","https://example.com/thumb-economics.jpg","economics,textbook,uasd,freshman","Paperback Edition","UASD Introduction to Economics textbook",1,"econ101-paperback","ECON101-PB",29.99,0.00,TRUE,"https://example.com/economics-hero.jpg","HERO","Book cover front",1
"Introduction to Economics","intro-to-economics","books_manuals","physical","https://example.com/thumb-economics.jpg","economics,textbook,uasd,freshman","Hardcover Edition","UASD Introduction to Economics textbook - deluxe",2,"econ101-hardcover","ECON101-HC",39.99,0.00,TRUE,"https://example.com/economics-hardcover.jpg","HERO","Hardcover edition",1
"Adobe Photoshop License","adobe-photoshop-license","electronics","digital","https://example.com/thumb-software.jpg","software,design,creative,photoshop","1-Year Annual Subscription","Full Photoshop license for one year",1,"photoshop-annual","PS-ANN-2026",239.88,18.00,TRUE,"https://example.com/software-hero.jpg","HERO","Photoshop box art",1
"Adobe Photoshop License","adobe-photoshop-license","electronics","digital","https://example.com/thumb-software.jpg","software,design,creative,photoshop","3-Year Subscription","Full Photoshop license for three years",2,"photoshop-3year","PS-3YR-2026",599.88,18.00,TRUE,"https://example.com/software-detail.jpg","DETAIL","Detailed view of subscription",2
"UASD Polo Shirt","uasd-polo-shirt","uniforms","physical","https://example.com/thumb-polo.jpg","uniform,uasd,official,clothing","Small - White","Official UASD polo shirt size S",1,"polo-s-white","POLO-S-WHT",19.99,18.00,TRUE,"https://example.com/polo-hero.jpg","HERO","White polo front",1
"UASD Polo Shirt","uasd-polo-shirt","uniforms","physical","https://example.com/thumb-polo.jpg","uniform,uasd,official,clothing","Medium - White","Official UASD polo shirt size M",2,"polo-m-white","POLO-M-WHT",19.99,18.00,TRUE,"https://example.com/polo-white.jpg","COLOR","White color swatch",2
"UASD Polo Shirt","uasd-polo-shirt","uniforms","physical","https://example.com/thumb-polo-blue.jpg","uniform,uasd,official,clothing","Medium - Blue","Official UASD polo shirt size M - Blue",3,"polo-m-blue","POLO-M-BLU",22.99,18.00,TRUE,"https://example.com/polo-blue.jpg","COLOR","Blue color swatch",3


"""
import csv
import logging
from decimal import Decimal
from io import TextIOWrapper
from typing import Dict, List, Tuple, Any
from collections import defaultdict

from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from products.default.models.product_model import Product
from products.default.models.product_variant_model import ProductVariant
from products.default.models.product_image_model import ProductImage
from taggit.models import Tag

logger = logging.getLogger(__name__)


def is_employee(user):
    """Check if user has employee role."""
    return user.is_authenticated and user.role == 'employee'


def validate_csv_headers(headers: List[str]) -> Tuple[bool, List[str]]:
    """Validate CSV has all required columns."""
    required_fields = {
        'product_name', 'product_slug', 'category', 'product_type',
        'variant_name', 'variant_number', 'variant_slug', 'variant_sku',
        'selling_price'
    }
    
    missing = required_fields - set(headers)
    if missing:
        return False, [f"Missing required columns: {', '.join(missing)}"]
    
    return True, []


def validate_product_row(row: Dict[str, str], row_num: int) -> List[Dict[str, Any]]:
    """
    Validate individual row data.
    Returns list of error dicts with field and message.
    """
    errors = []
    
    # Required fields validation
    required_fields = [
        'product_name', 'product_slug', 'category', 'product_type',
        'variant_name', 'variant_number', 'variant_slug', 'variant_sku',
        'selling_price'
    ]
    
    for field in required_fields:
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
    
    # Check category
    valid_categories = [choice[0] for choice in Product.Category.choices]
    if row.get('category'):
        if row['category'] not in valid_categories:
            errors.append({
                'field': 'category',
                'message': f"Invalid category '{row['category']}'. Must be one of: {', '.join(valid_categories)}",
                'row': row_num
            })
    
    # Check product type
    valid_types = [choice[0] for choice in Product.ProductType.choices]
    if row.get('product_type'):
        if row['product_type'] not in valid_types:
            errors.append({
                'field': 'product_type',
                'message': f"Invalid product type '{row['product_type']}'. Must be one of: {', '.join(valid_types)}",
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
        except (ValueError, TypeError) as e:
            errors.append({
                'field': 'selling_price',
                'message': f'Invalid selling price format: {row.get("selling_price")}',
                'row': row_num
            })
    
    # Check variant number
    if row.get('variant_number'):
        try:
            variant_num = int(row.get('variant_number', '0'))
            if variant_num < 0:
                errors.append({
                    'field': 'variant_number',
                    'message': f'Variant number cannot be negative: {variant_num}',
                    'row': row_num
                })
        except (ValueError, TypeError):
            errors.append({
                'field': 'variant_number',
                'message': f'Invalid variant number: {row.get("variant_number")}',
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
    
    # Check variant SKU format
    variant_sku = row.get('variant_sku', '').strip()
    if variant_sku:
        if len(variant_sku) > 500:
            errors.append({
                'field': 'variant_sku',
                'message': f'Variant SKU exceeds 500 characters: {len(variant_sku)}',
                'row': row_num
            })
        if ' ' in variant_sku:
            errors.append({
                'field': 'variant_sku',
                'message': 'Variant SKU cannot contain spaces',
                'row': row_num
            })
    
    # Check tax rate (optional) - accept both formats
    if row.get('tax_rate', '').strip():
        try:
            tax = Decimal(row.get('tax_rate', '0'))
            # Check if it's a valid tax rate (0-100% or 0-1)
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
        except (ValueError, TypeError):
            errors.append({
                'field': 'tax_rate',
                'message': f'Invalid tax rate format: {row.get("tax_rate")}',
                'row': row_num
            })
    
    # Check image URL if provided
    if row.get('image_url', '').strip():
        image_url = row['image_url'].strip()
        if len(image_url) > 2000:
            errors.append({
                'field': 'image_url',
                'message': f'Image URL exceeds 2000 characters: {len(image_url)}',
                'row': row_num
            })
        if not image_url.startswith(('http://', 'https://')):
            errors.append({
                'field': 'image_url',
                'message': f'Image URL must start with http:// or https://: {image_url[:50]}...',
                'row': row_num
            })
    
    # Check image type if provided
    if row.get('image_type', '').strip():
        valid_image_types = [choice[0] for choice in ProductImage.ImageType.choices]
        if row['image_type'] not in valid_image_types:
            errors.append({
                'field': 'image_type',
                'message': f"Invalid image type '{row['image_type']}'. Must be one of: {', '.join(valid_image_types)}",
                'row': row_num
            })
    
    # Check image order if provided
    if row.get('image_order', '').strip():
        try:
            order = int(row['image_order'])
            if order < 0:
                errors.append({
                    'field': 'image_order',
                    'message': f'Image order cannot be negative: {order}',
                    'row': row_num
                })
        except (ValueError, TypeError):
            errors.append({
                'field': 'image_order',
                'message': f'Invalid image order: {row.get("image_order")}',
                'row': row_num
            })
    
    return errors


def process_row_with_validation(row: Dict[str, str], row_num: int) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Convert CSV row to model data with validation.
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
            # If value > 100, could be 1800% - reject
            elif tax_decimal > 100:
                errors.append({
                    'field': 'tax_rate',
                    'message': f'Tax rate too high: {tax_rate_raw}% (max 100%)',
                    'row': row_num
                })
                tax_decimal = Decimal('0')
        except (ValueError, TypeError):
            tax_decimal = Decimal('0')
    else:
        tax_decimal = Decimal('0')
    
    data = {
        'product_name': row.get('product_name', '').strip(),
        'product_slug': row.get('product_slug', '').strip().lower(),
        'category': row.get('category', '').strip(),
        'product_type': row.get('product_type', '').strip(),
        'thumbnail': row.get('thumbnail', '').strip(),
        'tags': [t.strip() for t in row.get('tags', '').split(',') if t.strip()],
        
        'variant_name': row.get('variant_name', '').strip(),
        'variant_description': row.get('variant_description', '').strip(),
        'variant_number': int(row.get('variant_number', 0)) if row.get('variant_number', '').strip() else 0,
        'variant_slug': row.get('variant_slug', '').strip(),
        'variant_sku': row.get('variant_sku', '').strip(),
        'variant_status': is_active,
        'selling_price': Decimal(row.get('selling_price', '0')),
        'tax_rate': tax_decimal,
        
        'image_url': row.get('image_url', '').strip(),
        'image_type': row.get('image_type', 'HERO').strip(),
        'image_alt_text': row.get('image_alt_text', '').strip(),
        'image_order': int(row.get('image_order', 0)) if row.get('image_order', '').strip() else 0,
    }
    
    return data, errors


def check_duplicate_variant_skus(rows_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Check for duplicate variant SKUs within the CSV data.
    """
    errors = []
    seen_skus = {}
    
    for row in rows_data:
        sku = row['variant_sku']
        if sku in seen_skus:
            errors.append({
                'field': 'variant_sku',
                'message': f"Duplicate variant SKU '{sku}' found in CSV.",
                'row': row.get('_row_num', 'unknown'),
                'duplicate_row': seen_skus[sku]
            })
        else:
            seen_skus[sku] = row.get('_row_num', 'unknown')
    
    return errors


def check_existing_product_slugs(rows_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Check if product slugs already exist in database.
    This is a warning, not an error.
    """
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
    """
    Check if variant SKUs already exist in database.
    """
    warnings = []
    skus = [row['variant_sku'] for row in rows_data]
    
    existing_variants = ProductVariant.objects.filter(sku__in=skus).values('sku', 'name')
    existing_skus = {v['sku']: v['name'] for v in existing_variants}
    
    for row in rows_data:
        if row['variant_sku'] in existing_skus:
            warnings.append({
                'field': 'variant_sku',
                'message': f"Variant SKU '{row['variant_sku']}' already exists in database (variant: {existing_skus[row['variant_sku']]}). Will be updated.",
                'row': row.get('_row_num', 'unknown'),
                'warning': True
            })
    
    return warnings


def check_variant_slug_uniqueness(rows_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Check for duplicate variant slugs within the same product.
    """
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


def check_variant_number_uniqueness(rows_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Check for duplicate variant numbers within the same product.
    """
    errors = []
    product_variants = defaultdict(list)
    
    for row in rows_data:
        product_slug = row['product_slug']
        variant_number = row['variant_number']
        product_variants[product_slug].append({
            'variant_number': variant_number,
            'row': row.get('_row_num', 'unknown'),
            'sku': row['variant_sku']
        })
    
    for product_slug, variants in product_variants.items():
        seen_numbers = {}
        for variant in variants:
            number = variant['variant_number']
            if number in seen_numbers:
                errors.append({
                    'field': 'variant_number',
                    'message': f"Duplicate variant number '{number}' for product '{product_slug}'. Variants must have unique numbers within a product.",
                    'row': variant['row'],
                    'duplicate_row': seen_numbers[number]['row']
                })
            else:
                seen_numbers[number] = variant
    
    return errors


def check_variant_slug_db_conflict(rows_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Check if variant slugs already exist in database for the same product.
    """
    warnings = []
    
    # Get all products in the CSV
    product_slugs = set(row['product_slug'] for row in rows_data)
    existing_products = {p.slug: p for p in Product.objects.filter(slug__in=product_slugs)}
    
    # For each row, check if variant slug exists in DB for that product
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
        product, created = Product.objects.get_or_create(
            slug=product_data['product_slug'],
            defaults={
                'name': product_data['product_name'],
                'category': product_data['category'],
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
            if product.category != product_data['category']:
                product.category = product_data['category']
                updated = True
            if product.product_type != product_data['product_type']:
                product.product_type = product_data['product_type']
                updated = True
            if product.thumbnail != product_data.get('thumbnail', ''):
                product.thumbnail = product_data.get('thumbnail', '')
                updated = True
            
            if updated:
                product.save()
        
        # Handle tags
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
    """Get or create product variant from validated data."""
    errors = []
    
    try:
        variant, created = ProductVariant.objects.get_or_create(
            sku=variant_data['variant_sku'],
            defaults={
                'product': product,
                'name': variant_data['variant_name'],
                'description': variant_data.get('variant_description', ''),
                'variantnumber': variant_data['variant_number'],
                'slug': variant_data['variant_slug'],
                'selling_price': variant_data['selling_price'],
                'tax_rate': variant_data.get('tax_rate', Decimal('0')),
                'status': variant_data['variant_status'],
            }
        )
        
        # Check for duplicate variant number within same product (if created new)
        if created:
            existing = ProductVariant.objects.filter(
                product=product,
                variantnumber=variant_data['variant_number']
            ).exclude(pk=variant.pk)
            
            if existing.exists():
                errors.append({
                    'field': 'variant_number',
                    'message': f"Variant number {variant_data['variant_number']} already exists for product {product.slug} in database.",
                    'row': variant_data.get('_row_num', 'unknown')
                })
                variant.delete()
                return None, False, errors
        
        # If variant exists, update if fields differ
        if not created:
            updated = False
            if variant.name != variant_data['variant_name']:
                variant.name = variant_data['variant_name']
                updated = True
            if variant.description != variant_data.get('variant_description', ''):
                variant.description = variant_data.get('variant_description', '')
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
            if variant.variantnumber != variant_data['variant_number']:
                variant.variantnumber = variant_data['variant_number']
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


def create_image(variant: ProductVariant, image_data: Dict[str, Any]) -> Tuple[ProductImage, bool, List[Dict[str, Any]]]:
    """Create product image from validated data."""
    errors = []
    
    if not image_data.get('image_url'):
        return None, False, [{
            'field': 'image_url',
            'message': 'No image URL provided',
            'row': image_data.get('_row_num', 'unknown')
        }]
    
    try:
        image, created = ProductImage.objects.get_or_create(
            product_variant=variant,
            image=image_data['image_url'],
            defaults={
                'image_type': image_data.get('image_type', 'HERO'),
                'alt_text': image_data.get('image_alt_text', ''),
                'order': image_data.get('image_order', 0),
            }
        )
        
        # If image exists, update if needed
        if not created:
            updated = False
            if image.image_type != image_data.get('image_type', 'HERO'):
                image.image_type = image_data.get('image_type', 'HERO')
                updated = True
            if image.alt_text != image_data.get('image_alt_text', ''):
                image.alt_text = image_data.get('image_alt_text', '')
                updated = True
            if image.order != image_data.get('image_order', 0):
                image.order = image_data.get('image_order', 0)
                updated = True
            if updated:
                image.save()
        
        return image, created, errors
    except Exception as e:
        errors.append({
            'field': 'image',
            'message': f"Error creating image: {str(e)}",
            'row': image_data.get('_row_num', 'unknown')
        })
        return None, False, errors


# ========== DRF VIEW ==========

class ImportProductsCSVView(APIView):
    """
    Import products from CSV file.
    Only accessible to users with 'employee' role.
    
    ## Required CSV Columns:
    - product_name: Name of the product (max 255 chars)
    - product_slug: Unique slug identifier (alphanumeric with - and _)
    - category: stationery, books_manuals, medical_lab, architecture_arts, electronics, uniforms, snacks_beverages
    - product_type: physical, digital, service
    - variant_name: Name of the variant (max 500 chars)
    - variant_number: Integer identifier for the variant (must be unique per product)
    - variant_slug: Unique slug for the variant (alphanumeric with - and _)
    - variant_sku: Unique SKU for the variant (max 500 chars)
    - selling_price: Decimal price (e.g., 29.99)
    
    ## Optional CSV Columns:
    - thumbnail: URL for product thumbnail
    - tags: Comma-separated tags (e.g., "electronics,calculators,scientific")
    - variant_description: Description of the variant
    - tax_rate: Tax rate (accepts 18 or 0.18 format)
    - variant_status: TRUE/FALSE (defaults to TRUE)
    - image_url: URL for product image
    - image_type: HERO, DETAIL, THUMBNAIL, GALLERY, SIZE, COLOR, LIFESTYLE, PACKAGING, OTHER
    - image_alt_text: Alt text for the image
    - image_order: Integer for sorting images
    """
    
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, *args, **kwargs):
        """
        Upload and import CSV file.
        """
        # Check if user is employee
        if request.user.role != 'employee':
            return Response(
                {
                    'success': False,
                    'error': f'Only employees can import products. Your role: {request.user.role}'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if file is present
        if 'file' not in request.FILES:
            return Response({
                'success': False,
                'error': 'No file uploaded. Please provide a file with key "file".'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        csv_file = request.FILES['file']
        
        # Validate file type
        if not csv_file.name.endswith('.csv'):
            return Response({
                'success': False,
                'error': f'File must be a CSV. Got: {csv_file.name}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file size (10MB limit)
        max_size = 10 * 1024 * 1024
        if csv_file.size > max_size:
            return Response({
                'success': False,
                'error': f'File too large. Maximum size is {max_size / 1024 / 1024}MB'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse CSV
        try:
            decoded_file = TextIOWrapper(csv_file, encoding='utf-8-sig')
            reader = csv.DictReader(decoded_file)
            
            # Validate headers
            valid, header_errors = validate_csv_headers(reader.fieldnames or [])
            if not valid:
                return Response({
                    'success': False,
                    'errors': header_errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Process all rows with validation
            rows_data = []
            validation_errors = []
            
            for row_num, row in enumerate(reader, start=2):
                data, errors = process_row_with_validation(row, row_num)
                data['_row_num'] = row_num  # Store row number for error reporting
                if errors:
                    validation_errors.extend(errors)
                rows_data.append(data)
            
            # If there are validation errors, return them without creating anything
            if validation_errors:
                # Group errors by row for better readability
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
            csv_errors = []
            # NOTE: Duplicate product slugs are ALLOWED (multiple variants per product)
            # csv_errors.extend(check_duplicate_product_slugs(rows_data))  # DISABLED
            csv_errors.extend(check_duplicate_variant_skus(rows_data))
            csv_errors.extend(check_variant_slug_uniqueness(rows_data))
            csv_errors.extend(check_variant_number_uniqueness(rows_data))
            
            # Check database conflicts (warnings only)
            db_warnings = []
            db_warnings.extend(check_existing_product_slugs(rows_data))
            db_warnings.extend(check_existing_variant_skus(rows_data))
            db_warnings.extend(check_variant_slug_db_conflict(rows_data))
            
            # Separate errors from warnings
            csv_errors_only = [e for e in csv_errors if not e.get('warning', False)]
            csv_warnings = [e for e in csv_errors if e.get('warning', False)]
            db_warnings_only = [e for e in db_warnings if e.get('warning', False)]
            
            # If there are CSV errors, return them
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
            
            # Process data in a transaction
            stats = {
                'products_created': 0,
                'products_updated': 0,
                'variants_created': 0,
                'variants_updated': 0,
                'images_created': 0,
                'images_updated': 0,
                'images_skipped': 0,
                'total_rows': len(rows_data),
                'errors': [],
                'warnings': csv_warnings + db_warnings_only
            }
            
            # Group rows by product_slug
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
                            continue
                        
                        if product_created:
                            stats['products_created'] += 1
                        else:
                            stats['products_updated'] += 1
                        
                        # Process variants for this product
                        for variant_row in rows:
                            variant, variant_created, variant_errors = get_or_create_variant(
                                product, variant_row
                            )
                            
                            if variant_errors:
                                stats['errors'].extend(variant_errors)
                                continue
                            
                            if variant_created:
                                stats['variants_created'] += 1
                            else:
                                stats['variants_updated'] += 1
                            
                            # Process image for this variant
                            if variant_row.get('image_url'):
                                image, image_created, image_errors = create_image(
                                    variant, variant_row
                                )
                                
                                if image_errors:
                                    stats['errors'].extend(image_errors)
                                elif image_created:
                                    stats['images_created'] += 1
                                else:
                                    stats['images_updated'] += 1
                                
                    except Exception as e:
                        error_msg = {
                            'field': 'product',
                            'message': f"Error processing product {product_slug}: {str(e)}",
                            'row': product_row.get('_row_num', 'unknown')
                        }
                        stats['errors'].append(error_msg)
                        logger.error(f"Error processing product {product_slug}: {str(e)}", exc_info=True)
            
            # Prepare response
            response_data = {
                'success': len(stats['errors']) == 0,
                'stats': {
                    'products_created': stats['products_created'],
                    'products_updated': stats['products_updated'],
                    'variants_created': stats['variants_created'],
                    'variants_updated': stats['variants_updated'],
                    'images_created': stats['images_created'],
                    'images_updated': stats['images_updated'],
                    'images_skipped': stats['images_skipped'],
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
    
