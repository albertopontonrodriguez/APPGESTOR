from django.contrib.auth.mixins import LoginRequiredMixin

from apps.core.permissions import FinanceManageMixin
from django.db.models import Sum
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from apps.brands.models import Brand
from apps.configuration.models import StatusCatalog
from apps.configuration.utils import get_status_choices
from apps.reports.filters import filter_expenses, filter_suppliers
from apps.trips.models import Trip

from .forms import ExpenseCategoryForm, ExpenseForm, SupplierForm
from .models import Expense, ExpenseCategory, Supplier


class ExpensesHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'expenses/expenses_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'suppliers_count': Supplier.objects.count(),
                'categories_count': ExpenseCategory.objects.count(),
                'expenses_count': Expense.objects.count(),
                'pending_amount': Expense.objects.filter(payment_status=Expense.PaymentStatus.PENDING).aggregate(total=Sum('amount'))['total'] or 0,
                'recent_expenses': Expense.objects.select_related('brand', 'supplier', 'category', 'trip').order_by('-expense_date', '-created_at')[:6],
            }
        )
        return context


class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'expenses/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 20

    def get_queryset(self):
        return filter_suppliers(self.request.GET)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'query': self.request.GET.get('q', '').strip(),
                'selected_brand': self.request.GET.get('brand', '').strip(),
                'selected_supplier_type': self.request.GET.get('supplier_type', '').strip(),
                'country': self.request.GET.get('country', '').strip(),
                'brands': Brand.objects.order_by('name'),
                'supplier_type_choices': Supplier.SupplierType.choices,
            }
        )
        return context


class SupplierCreateView(FinanceManageMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'expenses/supplier_form.html'
    success_url = reverse_lazy('expenses:suppliers_list')


class SupplierDetailView(LoginRequiredMixin, DetailView):
    model = Supplier
    template_name = 'expenses/supplier_detail.html'
    context_object_name = 'supplier'

    def get_queryset(self):
        return Supplier.objects.select_related('brand').prefetch_related('expenses', 'received_invoices')


class SupplierUpdateView(FinanceManageMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'expenses/supplier_form.html'

    def get_success_url(self):
        return reverse_lazy('expenses:suppliers_detail', kwargs={'pk': self.object.pk})


class ExpenseCategoryListView(LoginRequiredMixin, ListView):
    model = ExpenseCategory
    template_name = 'expenses/category_list.html'
    context_object_name = 'categories'


class ExpenseCategoryCreateView(FinanceManageMixin, CreateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = 'expenses/category_form.html'
    success_url = reverse_lazy('expenses:categories_list')


class ExpenseCategoryUpdateView(FinanceManageMixin, UpdateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = 'expenses/category_form.html'
    success_url = reverse_lazy('expenses:categories_list')


class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'expenses/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 25

    def get_queryset(self):
        return filter_expenses(self.request.GET)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtered = filter_expenses(self.request.GET)
        context.update(
            {
                'query': self.request.GET.get('q', '').strip(),
                'selected_brand': self.request.GET.get('brand', '').strip(),
                'selected_trip': self.request.GET.get('trip', '').strip(),
                'selected_supplier': self.request.GET.get('supplier', '').strip(),
                'selected_category': self.request.GET.get('category', '').strip(),
                'selected_payment_status': self.request.GET.get('payment_status', '').strip(),
                'date_from': self.request.GET.get('date_from', '').strip(),
                'date_to': self.request.GET.get('date_to', '').strip(),
                'brands': Brand.objects.order_by('name'),
                'trips': Trip.objects.order_by('start_date', 'name'),
                'suppliers': Supplier.objects.order_by('legal_name'),
                'categories': ExpenseCategory.objects.order_by('name'),
                'payment_status_choices': get_status_choices(StatusCatalog.StatusGroup.EXPENSE_PAYMENT, Expense.PaymentStatus.choices),
                'total_amount': filtered.aggregate(total=Sum('amount'))['total'] or 0,
            }
        )
        return context


class ExpenseCreateView(FinanceManageMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expenses:expenses_list')


class ExpenseDetailView(LoginRequiredMixin, DetailView):
    model = Expense
    template_name = 'expenses/expense_detail.html'
    context_object_name = 'expense'

    def get_queryset(self):
        return Expense.objects.select_related('brand', 'trip', 'supplier', 'category').prefetch_related('received_invoices')


class ExpenseUpdateView(FinanceManageMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'

    def get_success_url(self):
        return reverse_lazy('expenses:expenses_detail', kwargs={'pk': self.object.pk})
