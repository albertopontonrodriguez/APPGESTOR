from django.db import models

from apps.bookings.models import Booking
from apps.brands.models import Brand
from apps.core.models import TimeStampedModel
from apps.expenses.models import Expense, Supplier
from apps.travelers.models import Traveler


class InvoiceIssued(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Borrador'
        SENT = 'sent', 'Enviada'
        PAID = 'paid', 'Pagada'
        CANCELLED = 'cancelled', 'Cancelada'

    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='issued_invoices')
    traveler = models.ForeignKey(Traveler, on_delete=models.PROTECT, related_name='issued_invoices')
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, related_name='issued_invoices', null=True, blank=True)
    invoice_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField()
    taxable_base = models.DecimalField(max_digits=10, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='EUR')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Factura emitida'
        verbose_name_plural = 'Facturas emitidas'
        ordering = ['-issue_date', '-created_at']

    def __str__(self) -> str:
        return self.invoice_number


class InvoiceReceived(TimeStampedModel):
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='received_invoices')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='received_invoices')
    expense = models.ForeignKey(Expense, on_delete=models.SET_NULL, related_name='received_invoices', null=True, blank=True)
    invoice_number = models.CharField(max_length=50)
    issue_date = models.DateField()
    taxable_base = models.DecimalField(max_digits=10, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='EUR')
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Factura recibida'
        verbose_name_plural = 'Facturas recibidas'
        ordering = ['-issue_date', '-created_at']
        unique_together = ('supplier', 'invoice_number')

    def __str__(self) -> str:
        return self.invoice_number


class InvoiceIssuedAttachment(TimeStampedModel):
    invoice = models.ForeignKey(InvoiceIssued, on_delete=models.CASCADE, related_name='attachments')
    title = models.CharField(max_length=120)
    file = models.FileField(upload_to='billing/issued/%Y/%m/')
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Adjunto de factura emitida'
        verbose_name_plural = 'Adjuntos de facturas emitidas'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.invoice.invoice_number} · {self.title}'


class InvoiceReceivedAttachment(TimeStampedModel):
    invoice = models.ForeignKey(InvoiceReceived, on_delete=models.CASCADE, related_name='attachments')
    title = models.CharField(max_length=120)
    file = models.FileField(upload_to='billing/received/%Y/%m/')
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Adjunto de factura recibida'
        verbose_name_plural = 'Adjuntos de facturas recibidas'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.invoice.invoice_number} · {self.title}'
