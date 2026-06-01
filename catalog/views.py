from django.db.models import Q
from django.views.generic import DetailView, ListView

from .models import Brand, Family, Perfume


class PerfumeListView(ListView):
    """Каталог парфюмов с фильтрами и пагинацией."""

    model = Perfume
    template_name = "catalog/perfume_list.html"
    context_object_name = "perfumes"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            Perfume.objects.select_related("brand")
            .prefetch_related("families", "notes")
        )

        params = self.request.GET

        q = params.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q)
                | Q(brand__name__icontains=q)
                | Q(description__icontains=q)
            )

        brand = params.get("brand")
        if brand:
            qs = qs.filter(brand_id=brand)

        family = params.get("family")
        if family:
            qs = qs.filter(families__id=family)

        gender = params.get("gender")
        if gender in {choice.value for choice in Perfume.Gender}:
            qs = qs.filter(gender=gender)

        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["brands"] = Brand.objects.order_by("name")
        ctx["families"] = Family.objects.order_by("name")
        ctx["genders"] = Perfume.Gender.choices
        ctx["selected"] = {
            "q": self.request.GET.get("q", ""),
            "brand": self.request.GET.get("brand", ""),
            "family": self.request.GET.get("family", ""),
            "gender": self.request.GET.get("gender", ""),
        }
        return ctx


class PerfumeDetailView(DetailView):
    model = Perfume
    template_name = "catalog/perfume_detail.html"
    context_object_name = "perfume"

    def get_queryset(self):
        return (
            Perfume.objects.select_related("brand", "brand__country")
            .prefetch_related("families", "notes")
        )


def collection_list_stub(request):
    """Заглушка коллекции (заполнится на этапе 5/6)."""

    from django.shortcuts import render

    return render(request, "collection/list.html")
