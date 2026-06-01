from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UserRegisterForm


class RegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            from django.shortcuts import redirect

            return redirect("home")
        return super().dispatch(request, *args, **kwargs)


@login_required
def profile_view(request):
    from catalog.models import Collection

    items = (
        Collection.objects.filter(user=request.user)
        .select_related("perfume", "perfume__brand")
        .prefetch_related("perfume__families")
    )
    return render(
        request,
        "accounts/profile.html",
        {"items": items, "items_count": items.count()},
    )
