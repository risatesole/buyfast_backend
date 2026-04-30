from ....account.user.models.customer_profile import Customer_model as Customer_model
from ....account.user.models.employee_profile import Employee
from ....product.models.model_product import Product
from ....product.models.price_model import Price
from ....inventory.models.provider_model import Provider
def inventory_stock(products):
    inventory = []

    for product in products:
        inventory.append({
            "id": product.id,
            "name": product.name,
            "stock": getattr(product, "stock", 0),
            "unit": "kg",
            "status": "Low" if getattr(product, "stock", 0) < 20 else "Normal",
        })

    return inventory

def backoffice_view_context_handler():
    customers = Customer_model.objects.select_related("user").all()
    employees = Employee.objects.select_related("user").all()

    products = Product.objects.prefetch_related("prices").all()
    providers = Provider.objects.all()

    for product in products:
        latest_price = product.prices.first() # type: ignore
        product.current_price = latest_price.value if latest_price else 0 # type: ignore

    context = {
        "customers": customers,
        "employees": employees,
        "providers": providers,
        "products": products,
        "inventory": inventory_stock(products),
        "project":{
            "name": "Duck"
        }
    }

    return context
