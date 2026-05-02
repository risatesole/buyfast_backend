from ....product.models.model_product import Product
from ....inventory.services.inventory_service import InventoryService
from ....employee.models.employee_model import employee_model
from django.contrib import messages
from django.shortcuts import render,redirect
from ....inventory.models.provider_model import Provider


def backoffice_add_stock_entry_view(request): 
    products = Product.objects.all()
    providers = InventoryService.list_providers()

    if request.method == "POST":
        try:
            product_id = request.POST.get("product")
            provider_id = request.POST.get("provider")
            
            quantity_str = request.POST.get("quantity")
            cost_str = request.POST.get("cost_per_unit")
            note = request.POST.get("note")

            # --- VALIDATION ---
            if not quantity_str:
                messages.error(request, "Quantity is required.")
                return redirect("add_stock_entry")

            try:
                quantity = int(float(quantity_str))
            except ValueError:
                messages.error(request, "Quantity must be a valid number.")
                return redirect("add_stock_entry")

            if quantity <= 0:
                messages.error(request, "Quantity must be greater than 0.")
                return redirect("add_stock_entry")

            if not cost_str:
                messages.error(request, "Cost per unit is required.")
                return redirect("add_stock_entry")

            from decimal import Decimal, InvalidOperation
            try:
                cost_per_unit = Decimal(cost_str)
            except (InvalidOperation, ValueError):
                messages.error(request, "Cost must be a valid number (e.g. 10.50).")
                return redirect("add_stock_entry")

            # --- FETCH OBJECTS ---

            product = Product.objects.get(id=product_id)

            provider = None
            if provider_id:
                provider = Provider.objects.get(id=provider_id)

            # 🔥 Direct mapping (since you guarantee it's always an employee)
            employee = employee_model.objects.get(user=request.user)

            # --- SERVICE CALL ---

            InventoryService.add_inventory_entry(
                product=product,
                provider=provider,
                quantity=quantity,
                cost_per_unit=cost_per_unit,
                added_by=employee,
                note=note
            )

            messages.success(request, "Stock entry added successfully.")
            return redirect("backoffice")

        except Product.DoesNotExist:
            messages.error(request, "Invalid product selected.")
        except Provider.DoesNotExist:
            messages.error(request, "Invalid provider selected.")
        except employee_model.DoesNotExist:
            messages.error(request, "Employee profile not found.")
        except ValueError as e:
            messages.error(request, f"Value error: {str(e)}")
        except Exception as e:
            messages.error(request, f"Unexpected error: {str(e)}")

    return render(request, "backoffice/create/create_stock_entry.html", {
        "products": products,
        "providers": providers
    })
