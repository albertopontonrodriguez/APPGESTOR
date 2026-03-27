from django.contrib import admin

from .models import InvoiceIssued, InvoiceReceived


@admin.register(InvoiceIssued)
class InvoiceIssuedAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'brand', 'traveler', 'issue_date', 'total_amount', 'currency', 'status')
    list_filter = ('brand', 'currency', 'status')
    search_fields = ('invoice_number', 'traveler__first_name', 'traveler__last_name')
    date_hierarchy = 'issue_date'


@admin.register(InvoiceReceived)
class InvoiceReceivedAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'brand', 'supplier', 'issue_date', 'total_amount', 'currency')
    list_filter = ('brand', 'currency')
    search_fields = ('invoice_number', 'supplier__legal_name', 'supplier__trade_name')
    date_hierarchy = 'issue_date'
