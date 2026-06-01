from django.contrib import admin

from .models import Brand, Collection, Country, Family, Note, Perfume


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    list_filter = ("country",)
    search_fields = ("name",)


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "slug")
    list_filter = ("type",)
    search_fields = ("name",)


@admin.register(Perfume)
class PerfumeAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "year", "gender", "longevity", "created_at")
    list_filter = ("gender", "longevity", "brand", "families")
    search_fields = ("name", "brand__name")
    filter_horizontal = ("families", "notes")
    autocomplete_fields = ("brand",)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("user", "perfume", "added_at")
    list_filter = ("added_at",)
    search_fields = ("user__username", "perfume__name")
    autocomplete_fields = ("perfume",)
