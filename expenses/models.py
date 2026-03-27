from django.db import models

from apps.brands.models import Brand
from apps.core.models import TimeStampedModel
from apps.trips.models import Trip


class Supplier(TimeStampedModel):
    class SupplierType(models.TextChoices):
        ACCOMMODATION = 'accommodation', 'Alojamiento'
        INTERNAL_TRANSPORT = 'internal_transport', 'Transporte interno'
        INSURANCE = 'insurance', 'Seguro'
        GUIDE = 'guide', 'Guía local'
        ACTIVITY = 'activity', 'Actividad'
        LOGISTICS = 'logistics', 'Logística'
        OTHER = 'other', 'Otro'

    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='suppliers')
    supplier_type = models.CharField(max_length=30, choices=SupplierType.choices, default=SupplierType.OTHER)
    legal_name = models.CharField(max_length=200)
    trade_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=100, blank=True)
    default_currency = models.CharField(max_length=10, default='EUR')
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['legal_name']

    def __str__(self) -> str:
        return self.trade_name or self.legal_name


class ExpenseCategory(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Categoría de gasto'
        verbose_name_plural = 'Categorías de gasto'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Expense(TimeStampedModel):
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        PAID = 'paid', 'Pagado'
        PARTIAL = 'partial', 'Pago parcial'

    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='expenses')
    trip = models.ForeignKey(Trip, on_delete=models.SET_NULL, related_name='expenses', null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='expenses')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='expenses')
    expense_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='EUR')
    description = models.TextField(blank=True)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)

    class Meta:
        verbose_name = 'Gasto'
        verbose_name_plural = 'Gastos'
        ordering = ['-expense_date', '-created_at']

    def __str__(self) -> str:
        return f'{self.category} · {self.amount} {self.currency}'
