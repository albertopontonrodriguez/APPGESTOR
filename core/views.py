from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.views.generic import TemplateView

from apps.billing.models import InvoiceIssued, InvoiceReceived
from apps.bookings.models import Booking, Payment
from apps.brands.models import Brand
from apps.expenses.models import Expense, Supplier
from apps.trips.models import Trip
from apps.travelers.models import Traveler
from apps.notifications.models import Notification
from apps.notifications.services import sync_all_notifications
from apps.planner.models import CalendarEvent, Task
from apps.internal_chat.models import ChatMessage, ChatRoom


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sync_all_notifications()
        payments_total = Payment.objects.filter(status=Payment.Status.CONFIRMED).aggregate(total=Sum('amount'))['total'] or 0
        expenses_total = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
        issued_total = InvoiceIssued.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        received_total = InvoiceReceived.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        context.update(
            {
                'brands_count': Brand.objects.count(),
                'travelers_count': Traveler.objects.count(),
                'trips_count': Trip.objects.count(),
                'bookings_count': Booking.objects.count(),
                'payments_count': Payment.objects.count(),
                'suppliers_count': Supplier.objects.count(),
                'expenses_count': Expense.objects.count(),
                'issued_invoices_count': InvoiceIssued.objects.count(),
                'received_invoices_count': InvoiceReceived.objects.count(),
                'events_count': CalendarEvent.objects.count(),
                'tasks_count': Task.objects.count(),
                'open_tasks_count': Task.objects.exclude(status__in=[Task.Status.DONE, Task.Status.CANCELLED]).count(),
                'payments_total': payments_total,
                'expenses_total': expenses_total,
                'issued_total': issued_total,
                'received_total': received_total,
                'pending_bookings': Booking.objects.filter(status__in=[
                    Booking.Status.PENDING_CONFIRMATION,
                    Booking.Status.DEPOSIT_PENDING,
                    Booking.Status.DOCUMENTATION_PENDING,
                    Booking.Status.PARTIALLY_PAID,
                ]).select_related('traveler', 'trip').order_by('-created_at')[:5],
                'upcoming_trips': Trip.objects.exclude(status=Trip.Status.CANCELLED).select_related('brand').order_by('start_date')[:5],
                'recent_travelers': Traveler.objects.select_related('brand').order_by('-created_at')[:5],
                'top_destinations': Trip.objects.values('destination').annotate(total=Count('id')).order_by('-total', 'destination')[:5],
                'recent_notifications': Notification.objects.filter(user=self.request.user, is_active=True).select_related('booking', 'trip', 'traveler')[:6],
                'unread_notifications': Notification.objects.filter(user=self.request.user, is_active=True, is_read=False).count(),
                'upcoming_events': CalendarEvent.objects.select_related('brand', 'assigned_to').order_by('start_at')[:5],
                'priority_tasks': Task.objects.exclude(status__in=[Task.Status.DONE, Task.Status.CANCELLED]).select_related('assigned_to', 'brand').order_by('due_date', 'priority')[:5],
                'chat_rooms_count': ChatRoom.objects.filter(participants=self.request.user, is_active=True).distinct().count(),
                'recent_chat_messages': ChatMessage.objects.filter(room__participants=self.request.user).select_related('author', 'room').order_by('-created_at')[:5],
            }
        )
        return context
