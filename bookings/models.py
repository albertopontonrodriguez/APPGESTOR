from decimal import Decimal

from django.db import models

from apps.core.models import TimeStampedModel
from apps.trips.models import Trip
from apps.travelers.models import Traveler


class Booking(TimeStampedModel):
    class Status(models.TextChoices):
        REQUEST = 'request', 'Solicitud recibida'
        PENDING_CONFIRMATION = 'pending_confirmation', 'Pendiente de confirmar'
        PREBOOKING = 'prebooking', 'Pre-reserva'
        CONFIRMED = 'confirmed', 'Reserva confirmada'
        DEPOSIT_PENDING = 'deposit_pending', 'Señal pendiente'
        DEPOSIT_PAID = 'deposit_paid', 'Señal pagada'
        PARTIALLY_PAID = 'partially_paid', 'Pago parcial'
        PAID = 'paid', 'Pagado'
        DOCUMENTATION_PENDING = 'documentation_pending', 'Documentación pendiente'
        COMPLETED = 'completed', 'Completado'
        CANCELLED = 'cancelled', 'Cancelado'
        WAITLIST = 'waitlist', 'Lista de espera'

    traveler = models.ForeignKey(Traveler, on_delete=models.PROTECT, related_name='bookings')
    trip = models.ForeignKey(Trip, on_delete=models.PROTECT, related_name='bookings')
    booking_date = models.DateField(auto_now_add=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='EUR')
    required_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    paid_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    pending_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.REQUEST)
    due_date = models.DateField(null=True, blank=True)
    internal_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-created_at']
        unique_together = ('traveler', 'trip')

    def __str__(self) -> str:
        return f'{self.traveler} · {self.trip}'

    @property
    def total_confirmed_paid(self) -> Decimal:
        total = self.payments.filter(status=Payment.Status.CONFIRMED).aggregate(total=models.Sum('amount'))['total']
        return total or Decimal('0.00')

    def refresh_financials(self, save: bool = True) -> None:
        total_paid = self.total_confirmed_paid
        self.paid_deposit = min(self.required_deposit, total_paid)
        self.pending_balance = max(Decimal('0.00'), self.final_price - total_paid)

        if self.status not in {self.Status.CANCELLED, self.Status.WAITLIST, self.Status.COMPLETED}:
            if total_paid <= Decimal('0.00'):
                self.status = self.Status.DEPOSIT_PENDING if self.required_deposit > Decimal('0.00') else self.Status.CONFIRMED
            elif total_paid < self.required_deposit:
                self.status = self.Status.PARTIALLY_PAID
            elif total_paid < self.final_price:
                self.status = self.Status.DEPOSIT_PAID
            else:
                self.status = self.Status.PAID

        if save:
            Booking.objects.filter(pk=self.pk).update(
                paid_deposit=self.paid_deposit,
                pending_balance=self.pending_balance,
                status=self.status,
            )
            self.sync_trip_occupancy()

    def sync_trip_occupancy(self) -> None:
        occupied = self.trip.bookings.exclude(status=self.Status.CANCELLED).count()
        Trip.objects.filter(pk=self.trip_id).update(occupied_slots=occupied)

    def save(self, *args, **kwargs):
        self.pending_balance = max(Decimal('0.00'), self.final_price - self.paid_deposit)
        super().save(*args, **kwargs)
        self.sync_trip_occupancy()

    def delete(self, *args, **kwargs):
        trip = self.trip
        super().delete(*args, **kwargs)
        occupied = trip.bookings.exclude(status=self.Status.CANCELLED).count()
        Trip.objects.filter(pk=trip.pk).update(occupied_slots=occupied)


class Payment(TimeStampedModel):
    class Method(models.TextChoices):
        BANK_TRANSFER = 'bank_transfer', 'Transferencia'
        CARD = 'card', 'Tarjeta'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        CONFIRMED = 'confirmed', 'Confirmado'
        FAILED = 'failed', 'Fallido'
        REFUNDED = 'refunded', 'Devuelto'

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='EUR')
    method = models.CharField(max_length=20, choices=Method.choices)
    reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    is_reconciled = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-payment_date', '-created_at']

    def __str__(self) -> str:
        return f'{self.booking} · {self.amount} {self.currency}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.booking.refresh_financials()

    def delete(self, *args, **kwargs):
        booking = self.booking
        super().delete(*args, **kwargs)
        booking.refresh_financials()
