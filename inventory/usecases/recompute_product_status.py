from products.default.models import ProductVariant
from ..queries import get_variant_current_stock


def recompute_product_status(product_id):
    """
    Sums the current stock across every variant of a product and stamps
    that aggregate's active/inactive state onto every variant's `status`:
    0 total stock -> False, > 0 -> True.
    """
    variant_ids = list(
        ProductVariant.objects.filter(product_id=product_id).values_list("id", flat=True)
    )
    if not variant_ids:
        return

    total_stock = sum(get_variant_current_stock(variant_id) for variant_id in variant_ids)
    ProductVariant.objects.filter(id__in=variant_ids).update(status=total_stock > 0)
