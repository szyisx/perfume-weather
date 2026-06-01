from django.urls import path

from . import views

urlpatterns = [
    path("perfumes/", views.perfume_list_stub, name="perfume_list"),
    path("perfumes/<int:pk>/", views.perfume_detail_stub, name="perfume_detail"),
    path("collection/", views.collection_list_stub, name="collection_list"),
]
