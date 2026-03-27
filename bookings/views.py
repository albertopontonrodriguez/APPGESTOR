from django.contrib.auth.mixins import LoginRequiredMixin

from apps.core.permissions import OperationsManageMixin
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.brands.models import Brand
from apps.configuration.models import StatusCatalog
from apps.configuration.utils import get_status_choices
from apps.reports.filters import filter_bookings
from apps.trips.models import Trip

from .forms import BookingForm, PaymentForm
from .models import Booking


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 20

    def get_queryset(self):
        return filter_bookings(self.request.GET)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtered = filter_bookings(self.request.GET)
        context.update(
            {
                'query': self.request.GET.get('q', '').strip(),
                'selected_brand': self.request.GET.get('brand', '').strip(),
                'selected_trip': self.request.GET.get('trip', '').strip(),
                'selected_status': self.request.GET.get('status', '').strip(),
                'due_from': self.request.GET.get('due_from', '').strip(),
                'due_to': self.request.GET.get('due_to', '').strip(),
                'pending_only': self.request.GET.get('pending_only', '').strip(),
                'brands': Brand.objects.order_by('name'),
                'trips': Trip.objects.order_by('start_date', 'name'),
                'status_choices': get_status_choices(StatusCatalog.StatusGroup.BOOKING, Booking.Status.choices),
                'pending_total': filtered.aggregate(total=Sum('pending_balance'))['total'] or 0,
            }
        )
        return context


class BookingCreateView(OperationsManageMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_form.html'
    success_url = reverse_lazy('bookings:list')


class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'

    def get_queryset(self):
        return Booking.objects.select_related('traveler', 'trip', 'trip__brand').prefetch_related('payments', 'issued_invoices')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment_form'] = PaymentForm(initial={'currency': self.object.currency})
        return context


class BookingUpdateView(OperationsManageMixin, UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_form.html'

    def get_success_url(self):
        return reverse_lazy('bookings:detail', kwargs={'pk': self.object.pk})


class BookingPaymentCreateView(OperationsManageMixin, CreateView):
    form_class = PaymentForm
    template_name = 'bookings/payment_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.booking = get_object_or_404(Booking, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.instance.booking = self.booking
        return form

    def form_valid(self, form):
        payment = form.save(commit=False)
        payment.booking = self.booking
        payment.save()
        return redirect('bookings:detail', pk=self.booking.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['booking'] = self.booking
        return context
