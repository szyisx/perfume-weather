from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_stub, name="login"),
    path("register/", views.register_stub, name="register"),
    path("logout/", views.logout_view, name="logout"),
]
