from .contexts.backoffice_context_handler import backoffice_view_context_handler
from django.shortcuts import render,redirect, get_object_or_404
from ...product.models.model_product import Product
from ...product.models.price_model import Price
from ...customer.models.customer_model import Customer_model
from ...employee.models.employee_model import employee_model, EmployeePosition
from ...account.user.models.model_user import User
from django.contrib import messages
from ...inventory.services.inventory_service import InventoryService

from ...inventory.models.provider_model import Provider

from django.contrib.auth.decorators import login_required, user_passes_test
def is_employee(user):
    return user.is_authenticated and user.role == "employee"

@login_required
@user_passes_test(is_employee)
def backoffice_view(request):
    """HANDLE POST ACTIONS"""
    return render(request, "backoffice/page.html", backoffice_view_context_handler())

@login_required
@user_passes_test(is_employee)
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

@login_required
@user_passes_test(is_employee)
def backoffice_customer_edit_view(request, customer_id):
    customer = Customer_model.objects.select_related("user").filter(id=customer_id).first()

    if not customer or customer.user.role != "customer":
        return redirect("backoffice")

    if request.method == "POST":
        user = customer.user
        user.email = request.POST.get("email")
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.role = request.POST.get("role", user.role)
        user.status = request.POST.get("status")
        user.save()

        customer.phone = request.POST.get("phone")
        customer.address = request.POST.get("address")
        customer.save()

        return redirect("backoffice")

    return render(request, "backoffice/edit/customer_edit.html", {
        "customer": customer
    })

@login_required
@user_passes_test(is_employee)
def backoffice_create_employee_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name", "")
        last_name = request.POST.get("last_name", "")
        position = request.POST.get("position")

        if not email or not password:
            messages.error(request, "Email and password are required")
            return render(request, "create_employee.html", {
                "positions": EmployeePosition.choices
            })

        try:
            # 1. Create user
            user = User.objects.create_user( # type: ignore
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role="employee",
                is_staff=True,
            )

            # 2. Create employee profile
            employee_model.objects.create(
                user=user,
                position=position or EmployeePosition.STORE_MANAGER
            )

            messages.success(request, "Employee created successfully")
            return redirect("backoffice")

        except Exception as e:
            messages.error(request, str(e))

    return render(request, "backoffice/create/create_employee.html", {
        "positions": EmployeePosition.choices
    })

@login_required
@user_passes_test(is_employee)
def backoffice_edit_employee_view(request, employee_id):
    employee = employee_model.objects.select_related("user").filter(id=employee_id).first()

    if not employee or employee.user.role != "employee":
        return redirect("backoffice")

    if request.method == "POST":
        user = employee.user

        # Update user fields
        user.email = request.POST.get("email")
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.role = request.POST.get("role")
        user.save()

        # Update employee fields
        employee.position = request.POST.get("position")
        employee.save()

        messages.success(request, "Employee updated successfully")
        return redirect("backoffice")

    return render(request, "backoffice/edit/employee_edit.html", {
        "employee": employee,
        "positions": EmployeePosition.choices
    })

@login_required
@user_passes_test(is_employee)
def backoffice_edit_product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    price = Price.objects.filter(product=product).first()
    if request.method == "POST":
        product.name = request.POST.get("name")
        product.description = request.POST.get("description")
        product.category = request.POST.get("category")
        product.brand = request.POST.get("brand")
        product.metric_unit = request.POST.get("metric_unit")
        product.status = request.POST.get("status")
        if request.FILES.get("image"):
            product.image = request.FILES.get("image")

        product.save()

        price_value = request.POST.get("price")

        if price:
            price.value = price_value
            price.save()
        else:
            Price.objects.create(
                product=product,
                value=price_value
            )
        return redirect("backoffice")

    context = {
        "product": product,
        "price": price
    }
    return render(request, "backoffice/edit/editproduct.html", context)




@login_required
@user_passes_test(is_employee)
def backoffice_create_provider(request):
    if request.method == "POST":
        Provider.objects.create(
            name=request.POST.get("name"),
            phone_number=request.POST.get("phone_number"),
            address=request.POST.get("address"),
            email=request.POST.get("email"),
            description=request.POST.get("description"),
        )
        return redirect("backoffice")
    
    return render(request, "backoffice/create/create_provider.html")


@login_required
@user_passes_test(is_employee)
def backoffice_edit_provider(request, provider_id):
    provider = get_object_or_404(Provider, id=provider_id)

    if request.method == "POST":
        provider.name = request.POST.get("name")
        provider.phone_number = request.POST.get("phone_number")
        provider.address = request.POST.get("address")
        provider.email = request.POST.get("email")
        provider.description = request.POST.get("description")

        provider.save()

        messages.success(request, "Provider updated successfully")
        return redirect("backoffice")

    return render(request, "backoffice/edit/edit_provider.html", {
        "provider": provider
    })
