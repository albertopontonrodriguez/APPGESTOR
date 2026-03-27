from decimal import Decimal

from django import forms

from apps.configuration.models import StatusCatalog
from apps.configuration.utils import get_currency_choices, get_status_choices

from .models import InvoiceIssued, InvoiceIssuedAttachment, InvoiceReceived, InvoiceReceivedAttachment


class InvoiceIssuedForm(forms.ModelForm):
    class Meta:
        model = InvoiceIssued
        fields = ['brand', 'traveler', 'booking', 'invoice_number', 'issue_date', 'taxable_base', 'vat_amount', 'total_amount', 'currency', 'status', 'notes']
        labels = {'brand':'Marca','traveler':'Viajero','booking':'Reserva','invoice_number':'Número de factura','issue_date':'Fecha de emisión','taxable_base':'Base imponible','vat_amount':'IVA','total_amount':'Total','currency':'Moneda','status':'Estado','notes':'Notas'}
        widgets = {'issue_date': forms.DateInput(attrs={'type': 'date'}), 'notes': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['total_amount'].required = False
        self.fields['currency'].widget = forms.Select(choices=get_currency_choices(['EUR', 'USD']))
        self.fields['status'].choices = get_status_choices(StatusCatalog.StatusGroup.INVOICE_ISSUED, InvoiceIssued.Status.choices)

    def clean(self):
        cleaned_data = super().clean()
        taxable_base = cleaned_data.get('taxable_base') or Decimal('0.00')
        vat_amount = cleaned_data.get('vat_amount') or Decimal('0.00')
        total_amount = cleaned_data.get('total_amount')
        if total_amount in (None, ''):
            cleaned_data['total_amount'] = taxable_base + vat_amount
        return cleaned_data


class InvoiceReceivedForm(forms.ModelForm):
    class Meta:
        model = InvoiceReceived
        fields = ['brand', 'supplier', 'expense', 'invoice_number', 'issue_date', 'taxable_base', 'vat_amount', 'total_amount', 'currency', 'notes']
        labels = {'brand':'Marca','supplier':'Proveedor','expense':'Gasto vinculado','invoice_number':'Número de factura','issue_date':'Fecha de emisión','taxable_base':'Base imponible','vat_amount':'IVA','total_amount':'Total','currency':'Moneda','notes':'Notas'}
        widgets = {'issue_date': forms.DateInput(attrs={'type': 'date'}), 'notes': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['total_amount'].required = False
        self.fields['currency'].widget = forms.Select(choices=get_currency_choices(['EUR', 'USD']))

    def clean(self):
        cleaned_data = super().clean()
        taxable_base = cleaned_data.get('taxable_base') or Decimal('0.00')
        vat_amount = cleaned_data.get('vat_amount') or Decimal('0.00')
        total_amount = cleaned_data.get('total_amount')
        if total_amount in (None, ''):
            cleaned_data['total_amount'] = taxable_base + vat_amount
        return cleaned_data


class InvoiceIssuedAttachmentForm(forms.ModelForm):
    class Meta:
        model = InvoiceIssuedAttachment
        fields = ['title', 'file', 'notes']
        labels = {'title':'Título','file':'Archivo','notes':'Notas'}
        widgets = {'notes': forms.Textarea(attrs={'rows': 3})}


class InvoiceReceivedAttachmentForm(forms.ModelForm):
    class Meta:
        model = InvoiceReceivedAttachment
        fields = ['title', 'file', 'notes']
        labels = {'title':'Título','file':'Archivo','notes':'Notas'}
        widgets = {'notes': forms.Textarea(attrs={'rows': 3})}
