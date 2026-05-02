from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from ..models.model_user import User

def signin_view(request):
    error = None

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Django does NOT authenticate by email by default
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            print(f"Debug: User doesnt exists")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("storefront")
        else:
            error = "Invalid email or password"

    return render(request, "user/signin.html", {"error": error})