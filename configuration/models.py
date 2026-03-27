from django.db import models
from django.urls import reverse

from apps.core.models import TimeStampedModel


class Currency(TimeStampedModel):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Moneda"
        verbose_name_plural = "Monedas"
        ordering = ["sort_order", "code"]

    def __str__(self) -> str:
        return f"{self.code} · {self.name}"


class Language(TimeStampedModel):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Idioma"
        verbose_name_plural = "Idiomas"
        ordering = ["sort_order", "code"]

    def __str__(self) -> str:
        return f"{self.code} · {self.name}"


class StatusCatalog(TimeStampedModel):
    class StatusGroup(models.TextChoices):
        TRIP = "trip", "Estados de viaje"
        BOOKING = "booking", "Estados de reserva"
        EXPENSE_PAYMENT = "expense_payment", "Estados de pago de gasto"
        INVOICE_ISSUED = "invoice_issued", "Estados de factura emitida"
        PAYMENT = "payment", "Estados de pago"
        TASK = "task", "Estados de tarea"
        LEAD = "lead", "Estados de contacto comercial"
        EVENT = "event", "Estados de evento"

    status_group = models.CharField(max_length=30, choices=StatusGroup.choices)
    code = models.CharField(max_length=50)
    label = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Estado configurable"
        verbose_name_plural = "Estados configurables"
        ordering = ["status_group", "sort_order", "label"]
        unique_together = ("status_group", "code")

    def __str__(self) -> str:
        return f"{self.get_status_group_display()} · {self.label}"


class GoogleSheetsSettings(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True, default='Principal')
    is_enabled = models.BooleanField(default=False)
    auto_sync_enabled = models.BooleanField(default=False)
    spreadsheet_name = models.CharField(max_length=150, default='GESTOR')
    spreadsheet_id = models.CharField(max_length=255, blank=True)
    service_account_json = models.TextField(blank=True)
    default_sheet_prefix = models.CharField(max_length=40, default='GESTOR')
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Google Sheets'
        verbose_name_plural = 'Google Sheets'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

    @property
    def spreadsheet_url(self) -> str:
        if not self.spreadsheet_id:
            return ''
        return f'https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/edit'

    def get_absolute_url(self):
        return reverse('configuration:google_sheets')
