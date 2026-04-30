from ....customer.models.customer_model import Customer_model as Customer_model
from ....employee.models.employee_model import employee_model
from ....product.models.model_product import Product
from ....product.models.price_model import Price
from ....inventory.models.provider_model import Provider
from ....inventory.services.inventory_service import InventoryService

def backoffice_view_context_handler():
    customers = Customer_model.objects.select_related("user").all()
    employees = employee_model.objects.select_related("user").all()

    products = Product.objects.prefetch_related("prices").all()
    providers = Provider.objects.all()

    # Add current price to products
    for product in products:
        latest_price = product.prices.first()  # type: ignore
        product.current_price = latest_price.value if latest_price else 0  # type: ignore

    context = {
        "customers": customers,
        "employees": employees,
        "providers": providers,
        "products": products,
        "inventory": None, 
        "stock_movement":InventoryService.list_stock_movements(),
        "project": {
            "name": "Duck"
        }
    }

    return context