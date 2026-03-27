from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Count, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from apps.accounts.forms import LoginForm, ManagedUserCreateForm, ManagedUserUpdateForm, UserPasswordChangeForm
from apps.accounts.models import User
from apps.billing.models import InvoiceIssued, InvoiceReceived
from apps.bookings.models import Booking
from apps.brands.models import Brand
from apps.configuration.models import Currency, Language, StatusCatalog
from apps.core.permissions import AdminOrCEOMixin
from apps.expenses.models import Expense, Supplier
from apps.notifications.models import Notification
from apps.notifications.services import sync_all_notifications
from apps.travelers.models import Traveler
from apps.trips.models import Trip
from apps.planner.models import CalendarEvent, Task


class ManagementHomeView(AdminOrCEOMixin, TemplateView):
    template_name = 'management_ui/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users_by_role = User.objects.values('role').annotate(total=Count('id')).order_by('role')
        context.update(
            {
                'users_count': User.objects.count(),
                'active_users_count': User.objects.filter(is_active=True).count(),
                'brands_count': Brand.objects.count(),
                'travelers_count': Traveler.objects.count(),
                'trips_count': Trip.objects.count(),
                'bookings_count': Booking.objects.count(),
                'suppliers_count': Supplier.objects.count(),
                'expenses_count': Expense.objects.count(),
                'issued_invoices_count': InvoiceIssued.objects.count(),
                'received_invoices_count': InvoiceReceived.objects.count(),
                'currencies_count': Currency.objects.count(),
                'languages_count': Language.objects.count(),
                'statuses_count': StatusCatalog.objects.count(),
                'events_count': CalendarEvent.objects.count(),
                'tasks_count': Task.objects.count(),
                'users_by_role': users_by_role,
                'recent_users': User.objects.order_by('-date_joined')[:6],
                'unread_notifications_count': Notification.objects.filter(is_read=False, is_active=True).count(),
                'recent_notifications': Notification.objects.filter(is_active=True).select_related('user').order_by('-created_at')[:8],
            }
        )
        return context


class UserListView(AdminOrCEOMixin, ListView):
    model = User
    template_name = 'management_ui/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        queryset = super().get_queryset().order_by('username')
        q = self.request.GET.get('q', '').strip()
        role = self.request.GET.get('role', '').strip()
        active = self.request.GET.get('active', '').strip()

        if q:
            queryset = queryset.filter(Q(username__icontains=q) | Q(display_name__icontains=q) | Q(email__icontains=q))
        if role:
            queryset = queryset.filter(role=role)
        if active == 'yes':
            queryset = queryset.filter(is_active=True)
        elif active == 'no':
            queryset = queryset.filter(is_active=False)
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'query': self.request.GET.get('q', '').strip(),
                'selected_role': self.request.GET.get('role', '').strip(),
                'selected_active': self.request.GET.get('active', '').strip(),
                'role_choices': User.Role.choices,
            }
        )
        return context


class UserCreateView(AdminOrCEOMixin, CreateView):
    model = User
    form_class = ManagedUserCreateForm
    template_name = 'management_ui/user_form.html'
    success_url = reverse_lazy('management_ui:users_list')


class UserDetailView(AdminOrCEOMixin, DetailView):
    model = User
    template_name = 'management_ui/user_detail.html'
    context_object_name = 'managed_user'


class UserUpdateView(AdminOrCEOMixin, UpdateView):
    model = User
    form_class = ManagedUserUpdateForm
    template_name = 'management_ui/user_form.html'

    def get_success_url(self):
        return reverse_lazy('management_ui:users_detail', kwargs={'pk': self.object.pk})


class NotificationSyncView(AdminOrCEOMixin, View):
    def post(self, request, *args, **kwargs):
        sync_all_notifications()
        messages.success(request, 'Avisos internos sincronizados correctamente.')
        return redirect('management_ui:home')


class ProfilePasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = 'management_ui/password_change_form.html'
    success_url = reverse_lazy('management_ui:password_change')

    def form_valid(self, form):
        messages.success(self.request, 'Contraseña actualizada correctamente.')
        return super().form_valid(form)
