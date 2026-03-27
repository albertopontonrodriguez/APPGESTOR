from django import forms

from apps.configuration.models import StatusCatalog
from apps.configuration.utils import get_currency_choices, get_status_choices

from .models import Expense, ExpenseCategory, Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['brand','supplier_type','legal_name','trade_name','email','phone','country','default_currency','notes']
        labels = {'brand':'Marca','supplier_type':'Tipo de proveedor','legal_name':'Nombre legal','trade_name':'Nombre comercial','email':'Email','phone':'Teléfono','country':'País','default_currency':'Moneda por defecto','notes':'Notas'}
        widgets = {'notes': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['default_currency'].widget = forms.Select(choices=get_currency_choices(['EUR', 'USD']))


class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'description', 'is_active']
        labels = {'name':'Nombre', 'description':'Descripción', 'is_active':'Activa'}
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['brand','trip','supplier','category','expense_date','amount','currency','description','payment_status']
        labels = {'brand':'Marca','trip':'Viaje','supplier':'Proveedor','category':'Categoría','expense_date':'Fecha del gasto','amount':'Importe','currency':'Moneda','description':'Descripción','payment_status':'Estado de pago'}
        widgets = {'expense_date': forms.DateInput(attrs={'type': 'date'}), 'description': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].widget = forms.Select(choices=get_currency_choices(['EUR', 'USD']))
        self.fields['payment_status'].choices = get_status_choices(StatusCatalog.StatusGroup.EXPENSE_PAYMENT, Expense.PaymentStatus.choices)
