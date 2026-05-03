from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from ..models.model_user import User

def signin_view(request):
    error = None

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Authenticate user
        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.status == "deactivated": # type: ignore
                error = "Account deactivated"
                return render(request, "user/signin.html", {"error": error})

            login(request, user)
            return redirect("storefront")

        else:
            error = "Invalid email or password"

    return render(request, "user/signin.html", {"error": error})