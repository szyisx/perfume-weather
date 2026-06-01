from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import PerfumeForm
from .models import Brand, Collection, Family, Perfume


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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["in_collection"] = (
            user.is_authenticated
            and Collection.objects.filter(user=user, perfume=self.object).exists()
        )
        return ctx


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Доступ только для is_staff."""

    def test_func(self) -> bool:
        return self.request.user.is_authenticated and self.request.user.is_staff


class PerfumeCreateView(StaffRequiredMixin, CreateView):
    model = Perfume
    form_class = PerfumeForm
    template_name = "catalog/perfume_form.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_title"] = "Новый парфюм"
        ctx["submit_label"] = "Создать"
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Парфюм создан.")
        return super().form_valid(form)


class PerfumeUpdateView(StaffRequiredMixin, UpdateView):
    model = Perfume
    form_class = PerfumeForm
    template_name = "catalog/perfume_form.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_title"] = f"Редактирование: {self.object.name}"
        ctx["submit_label"] = "Сохранить"
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Изменения сохранены.")
        return super().form_valid(form)


class PerfumeDeleteView(StaffRequiredMixin, DeleteView):
    model = Perfume
    template_name = "catalog/perfume_confirm_delete.html"
    success_url = reverse_lazy("perfume_list")

    def form_valid(self, form):
        messages.success(self.request, "Парфюм удалён.")
        return super().form_valid(form)


@login_required
@require_POST
def collection_add(request, pk: int):
    perfume = get_object_or_404(Perfume, pk=pk)
    _, created = Collection.objects.get_or_create(user=request.user, perfume=perfume)
    if created:
        messages.success(request, f"«{perfume.name}» добавлен в коллекцию.")
    else:
        messages.info(request, "Уже в коллекции.")
    return HttpResponseRedirect(request.POST.get("next") or f"/perfumes/{pk}/")


@login_required
@require_POST
def collection_remove(request, pk: int):
    perfume = get_object_or_404(Perfume, pk=pk)
    deleted, _ = Collection.objects.filter(user=request.user, perfume=perfume).delete()
    if deleted:
        messages.success(request, f"«{perfume.name}» убран из коллекции.")
    return HttpResponseRedirect(request.POST.get("next") or "/collection/")


@login_required
def collection_list(request):
    items = (
        Collection.objects.filter(user=request.user)
        .select_related("perfume", "perfume__brand")
        .prefetch_related("perfume__families")
    )
    return render(request, "collection/list.html", {"items": items})
