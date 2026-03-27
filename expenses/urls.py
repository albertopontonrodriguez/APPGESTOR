from django.urls import path

from .views import (
    ExpenseCategoryCreateView,
    ExpenseCategoryListView,
    ExpenseCategoryUpdateView,
    ExpenseCreateView,
    ExpenseDetailView,
    ExpenseListView,
    ExpenseUpdateView,
    ExpensesHomeView,
    SupplierCreateView,
    SupplierDetailView,
    SupplierListView,
    SupplierUpdateView,
)

app_name = 'expenses'

urlpatterns = [
    path('', ExpensesHomeView.as_view(), name='home'),
    path('proveedores/', SupplierListView.as_view(), name='suppliers_list'),
    path('proveedores/nuevo/', SupplierCreateView.as_view(), name='suppliers_create'),
    path('proveedores/<int:pk>/', SupplierDetailView.as_view(), name='suppliers_detail'),
    path('proveedores/<int:pk>/editar/', SupplierUpdateView.as_view(), name='suppliers_update'),
    path('categorias/', ExpenseCategoryListView.as_view(), name='categories_list'),
    path('categorias/nueva/', ExpenseCategoryCreateView.as_view(), name='categories_create'),
    path('categorias/<int:pk>/editar/', ExpenseCategoryUpdateView.as_view(), name='categories_update'),
    path('listado/', ExpenseListView.as_view(), name='expenses_list'),
    path('nuevo/', ExpenseCreateView.as_view(), name='expenses_create'),
    path('<int:pk>/', ExpenseDetailView.as_view(), name='expenses_detail'),
    path('<int:pk>/editar/', ExpenseUpdateView.as_view(), name='expenses_update'),
]
