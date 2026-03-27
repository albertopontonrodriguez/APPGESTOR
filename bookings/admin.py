from django.contrib import admin

from .models import Booking, Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('traveler', 'trip', 'booking_date', 'final_price', 'currency', 'status', 'pending_balance')
    search_fields = ('traveler__first_name', 'traveler__last_name', 'trip__name')
    list_filter = ('status', 'currency', 'trip__brand')
    inlines = [PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'payment_date', 'amount', 'currency', 'method', 'status', 'is_reconciled')
    list_filter = ('status', 'method', 'currency', 'is_reconciled')
    search_fields = ('booking__traveler__first_name', 'booking__traveler__last_name', 'reference')
