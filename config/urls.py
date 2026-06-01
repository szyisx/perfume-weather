from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path


def home(request):
    return HttpResponse(
        "<h1>PerfumeWeather</h1>"
        "<p>Этап 2 готов. Этапы 3+ — впереди.</p>"
        "<p><a href='/admin/'>Админка</a></p>"
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
