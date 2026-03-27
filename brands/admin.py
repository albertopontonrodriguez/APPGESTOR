from django.contrib import admin

from .models import Brand


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'legal_name', 'primary_language', 'primary_currency', 'is_active')
    search_fields = ('name', 'legal_name', 'tax_id', 'email')
    list_filter = ('is_active', 'primary_language', 'primary_currency')
