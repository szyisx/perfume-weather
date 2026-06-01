from django.urls import path

from . import views

urlpatterns = [
    path("perfumes/", views.PerfumeListView.as_view(), name="perfume_list"),
    path("perfumes/<int:pk>/", views.PerfumeDetailView.as_view(), name="perfume_detail"),
    path("collection/", views.collection_list_stub, name="collection_list"),
]
