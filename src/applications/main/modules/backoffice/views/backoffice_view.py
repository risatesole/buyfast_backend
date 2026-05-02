
from django.shortcuts import render,redirect, get_object_or_404
from ...product.models.model_product import Product
from ...product.models.price_model import Price
from ...customer.models.customer_model import Customer_model
from ...employee.models.employee_model import employee_model, EmployeePosition
from ...account.user.models.model_user import User
from django.contrib import messages
from ...inventory.services.inventory_service import InventoryService
from ...auth.is_employee_challenge import is_employee_challenge
from ...inventory.models.provider_model import Provider
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
@user_passes_test(is_employee_challenge)
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
@user_passes_test(is_employee_challenge)
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
@user_passes_test(is_employee_challenge)
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
@user_passes_test(is_employee_challenge)
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
@user_passes_test(is_employee_challenge)
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
@user_passes_test(is_employee_challenge)
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
