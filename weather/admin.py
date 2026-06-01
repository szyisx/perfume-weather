from django.contrib import admin

from .models import WeatherRule


@admin.register(WeatherRule)
class WeatherRuleAdmin(admin.ModelAdmin):
    list_display = ("condition", "temp_min", "temp_max", "family")
    list_filter = ("condition", "family")
    autocomplete_fields = ("family",)
