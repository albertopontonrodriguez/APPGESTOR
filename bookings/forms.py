from django import forms

from apps.configuration.models import StatusCatalog
from apps.configuration.utils import get_currency_choices, get_status_choices

from .models import Booking, Payment


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['traveler','trip','final_price','currency','required_deposit','status','due_date','internal_notes']
        labels = {'traveler':'Viajero','trip':'Viaje','final_price':'Precio final','currency':'Moneda','required_deposit':'Señal requerida','status':'Estado','due_date':'Vencimiento','internal_notes':'Notas internas'}
        widgets = {'due_date': forms.DateInput(attrs={'type': 'date'}), 'internal_notes': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].widget = forms.Select(choices=get_currency_choices(['EUR', 'USD']))
        self.fields['status'].choices = get_status_choices(StatusCatalog.StatusGroup.BOOKING, Booking.Status.choices)


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_date', 'amount', 'currency', 'method', 'reference', 'status', 'is_reconciled', 'notes']
        labels = {'payment_date':'Fecha de pago','amount':'Importe','currency':'Moneda','method':'Método','reference':'Referencia','status':'Estado','is_reconciled':'Conciliado','notes':'Notas'}
        widgets = {'payment_date': forms.DateInput(attrs={'type': 'date'}), 'notes': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['currency'].widget = forms.Select(choices=get_currency_choices(['EUR', 'USD']))
        self.fields['status'].choices = get_status_choices(StatusCatalog.StatusGroup.PAYMENT, Payment.Status.choices)
