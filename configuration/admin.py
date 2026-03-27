from django.contrib import admin

from .models import Currency, Language, StatusCatalog


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "symbol", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("code", "name")


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("code", "name")


@admin.register(StatusCatalog)
class StatusCatalogAdmin(admin.ModelAdmin):
    list_display = ("status_group", "code", "label", "is_active", "sort_order")
    list_filter = ("status_group", "is_active")
    search_fields = ("code", "label")
