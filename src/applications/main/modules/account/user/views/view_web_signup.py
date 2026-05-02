from django.shortcuts import render, redirect
from django.contrib.auth import login
from ..services.user.user_service import UserService, emailExistsError

def form_action_signup(request, first_name, last_name, email, password):
    """SIGNUP USER WITH CUSTOMER ROLE"""
    service = UserService()
    try:
        user, customer = service.createCustomer(
            first_name, last_name, email, password
        )
        login(request, user)
        return redirect("storefront")

    except emailExistsError:
        print("Email already exists")
        return render(request, "user/signup.html", {
            "error": "Email already exists"
        })

def signup_view(request):
    """ENTRY POINT FOR SIGNUP"""
    if request.user.is_authenticated:
        return redirect("storefront")

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        return form_action_signup(request, first_name, last_name, email, password)

    return render(request, "user/signup.html")
