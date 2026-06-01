from django.urls import path

from . import views

urlpatterns = [
    path("perfumes/", views.PerfumeListView.as_view(), name="perfume_list"),
    path("perfumes/new/", views.PerfumeCreateView.as_view(), name="perfume_create"),
    path("perfumes/<int:pk>/", views.PerfumeDetailView.as_view(), name="perfume_detail"),
    path("perfumes/<int:pk>/edit/", views.PerfumeUpdateView.as_view(), name="perfume_update"),
    path("perfumes/<int:pk>/delete/", views.PerfumeDeleteView.as_view(), name="perfume_delete"),
    path("perfumes/<int:pk>/collect/", views.collection_add, name="collection_add"),
    path("perfumes/<int:pk>/uncollect/", views.collection_remove, name="collection_remove"),
    path("collection/", views.collection_list, name="collection_list"),
]
