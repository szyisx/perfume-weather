from django.contrib.auth import logout
from django.shortcuts import redirect, render


def login_stub(request):
    return render(request, "accounts/login.html")


def register_stub(request):
    return render(request, "accounts/register.html")


def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("home")
