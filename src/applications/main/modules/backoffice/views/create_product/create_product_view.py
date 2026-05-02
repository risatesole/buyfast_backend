from django.contrib.auth.decorators import login_required, user_passes_test
from ....auth.is_employee_challenge import is_employee_challenge
from django.shortcuts import render,redirect
from ....product.models.model_product import Product
from ....product.models.price_model import Price
from ....inventory.services.inventory_service import InventoryService
from ....employee.models.employee_model import employee_model, EmployeePosition

@login_required
@user_passes_test(is_employee_challenge)
def backoffice_create_product_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        category = request.POST.get("category")
        image = request.FILES.get("image")
        price_value = request.POST.get("price")
        brand = request.POST.get("brand")
        metric_unit=request.POST.get("metric_unit")
        initial_inventory_existance = request.POST.get("initial_inventory_existance") # i want to add this value to the inventory if it returns number more than 0 and put it into inventory
        status = request.POST.get("status")
        product = Product.objects.create(
            name=name,
            description=description,
            category=category,
            image=image,
            status=status,
            brand=brand,
            metric_unit = metric_unit
        )

        # 2. crear precio relacionado
        if price_value:
            Price.objects.create(
                product=product,
                value=price_value
            )

         # 3. Add initial inventory if needed
        if initial_inventory_existance:
            try:
                qty = int(float(initial_inventory_existance))

                if qty > 0:
                    employee = employee_model.objects.get(user=request.user)

                    InventoryService.add_inventory_entry(
                        product=product,
                        provider=None,  # or allow selecting provider later
                        quantity=qty,
                        cost_per_unit=0,  # or request field if you want
                        added_by=employee,
                        note="Initial inventory"
                    )

            except ValueError:
                pass  # ignore invalid input silently or show message if you prefer

        return redirect("backoffice")
    return render(request, "backoffice/create/createproduct.html")
