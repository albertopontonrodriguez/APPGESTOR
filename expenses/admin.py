from django.contrib import admin

from .models import Expense, ExpenseCategory, Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'brand', 'supplier_type', 'email', 'phone', 'default_currency')
    list_filter = ('brand', 'supplier_type', 'default_currency')
    search_fields = ('legal_name', 'trade_name', 'email')


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('category', 'brand', 'trip', 'supplier', 'expense_date', 'amount', 'currency', 'payment_status')
    list_filter = ('brand', 'currency', 'payment_status', 'category')
    search_fields = ('description', 'supplier__legal_name', 'trip__name')
    date_hierarchy = 'expense_date'
