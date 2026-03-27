from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from apps.configuration.models import Currency, Language, StatusCatalog


class Command(BaseCommand):
    help = 'Carga monedas, idiomas y estados por defecto para GESTOR.'

    def handle(self, *args, **options):
        existing_tables = set(connection.introspection.table_names())
        required_tables = {'configuration_currency', 'configuration_language', 'configuration_statuscatalog'}
        if not required_tables.issubset(existing_tables):
            raise CommandError(
                'Faltan tablas de configuración. Ejecuta primero: python manage.py migrate --run-syncdb o python manage.py setup_local --with-demo'
            )

        currencies = [
            ('EUR', 'Euro', '€', 1),
            ('USD', 'Dólar estadounidense', '$', 2),
            ('GBP', 'Libra esterlina', '£', 3),
        ]
        for code, name, symbol, order in currencies:
            Currency.objects.update_or_create(
                code=code,
                defaults={'name': name, 'symbol': symbol, 'sort_order': order, 'is_active': True},
            )

        languages = [
            ('es', 'Español', 1),
            ('en', 'Inglés', 2),
            ('fr', 'Francés', 3),
        ]
        for code, name, order in languages:
            Language.objects.update_or_create(
                code=code,
                defaults={'name': name, 'sort_order': order, 'is_active': True},
            )

        statuses = [
            (StatusCatalog.StatusGroup.TRIP, 'draft', 'Borrador', 1),
            (StatusCatalog.StatusGroup.TRIP, 'open', 'Abierto', 2),
            (StatusCatalog.StatusGroup.TRIP, 'full', 'Completo', 3),
            (StatusCatalog.StatusGroup.TRIP, 'closed', 'Cerrado', 4),
            (StatusCatalog.StatusGroup.TRIP, 'cancelled', 'Cancelado', 5),
            (StatusCatalog.StatusGroup.BOOKING, 'request', 'Solicitud recibida', 1),
            (StatusCatalog.StatusGroup.BOOKING, 'pending_confirmation', 'Pendiente de confirmar', 2),
            (StatusCatalog.StatusGroup.BOOKING, 'prebooking', 'Pre-reserva', 3),
            (StatusCatalog.StatusGroup.BOOKING, 'confirmed', 'Reserva confirmada', 4),
            (StatusCatalog.StatusGroup.BOOKING, 'deposit_pending', 'Señal pendiente', 5),
            (StatusCatalog.StatusGroup.BOOKING, 'deposit_paid', 'Señal pagada', 6),
            (StatusCatalog.StatusGroup.BOOKING, 'partially_paid', 'Pago parcial', 7),
            (StatusCatalog.StatusGroup.BOOKING, 'paid', 'Pagado', 8),
            (StatusCatalog.StatusGroup.BOOKING, 'documentation_pending', 'Documentación pendiente', 9),
            (StatusCatalog.StatusGroup.BOOKING, 'completed', 'Completado', 10),
            (StatusCatalog.StatusGroup.BOOKING, 'cancelled', 'Cancelado', 11),
            (StatusCatalog.StatusGroup.BOOKING, 'waitlist', 'Lista de espera', 12),
            (StatusCatalog.StatusGroup.EXPENSE_PAYMENT, 'pending', 'Pendiente', 1),
            (StatusCatalog.StatusGroup.EXPENSE_PAYMENT, 'partial', 'Pago parcial', 2),
            (StatusCatalog.StatusGroup.EXPENSE_PAYMENT, 'paid', 'Pagado', 3),
            (StatusCatalog.StatusGroup.INVOICE_ISSUED, 'draft', 'Borrador', 1),
            (StatusCatalog.StatusGroup.INVOICE_ISSUED, 'sent', 'Enviada', 2),
            (StatusCatalog.StatusGroup.INVOICE_ISSUED, 'paid', 'Pagada', 3),
            (StatusCatalog.StatusGroup.INVOICE_ISSUED, 'cancelled', 'Cancelada', 4),
            (StatusCatalog.StatusGroup.PAYMENT, 'pending', 'Pendiente', 1),
            (StatusCatalog.StatusGroup.PAYMENT, 'confirmed', 'Confirmado', 2),
            (StatusCatalog.StatusGroup.PAYMENT, 'failed', 'Fallido', 3),
            (StatusCatalog.StatusGroup.PAYMENT, 'refunded', 'Devuelto', 4),

            (StatusCatalog.StatusGroup.TASK, 'pending', 'Pendiente', 1),
            (StatusCatalog.StatusGroup.TASK, 'in_progress', 'En curso', 2),
            (StatusCatalog.StatusGroup.TASK, 'blocked', 'Bloqueada', 3),
            (StatusCatalog.StatusGroup.TASK, 'done', 'Hecha', 4),
            (StatusCatalog.StatusGroup.TASK, 'cancelled', 'Cancelada', 5),
            (StatusCatalog.StatusGroup.LEAD, 'new', 'Nuevo', 1),
            (StatusCatalog.StatusGroup.LEAD, 'contacted', 'Contactado', 2),
            (StatusCatalog.StatusGroup.LEAD, 'proposal', 'Propuesta enviada', 3),
            (StatusCatalog.StatusGroup.LEAD, 'negotiation', 'Negociación', 4),
            (StatusCatalog.StatusGroup.LEAD, 'won', 'Ganado', 5),
            (StatusCatalog.StatusGroup.LEAD, 'lost', 'Perdido', 6),
            (StatusCatalog.StatusGroup.LEAD, 'dormant', 'Dormido', 7),
            (StatusCatalog.StatusGroup.EVENT, 'scheduled', 'Programado', 1),
            (StatusCatalog.StatusGroup.EVENT, 'completed', 'Completado', 2),
            (StatusCatalog.StatusGroup.EVENT, 'cancelled', 'Cancelado', 3),
        ]
        for group, code, label, order in statuses:
            StatusCatalog.objects.update_or_create(
                status_group=group,
                code=code,
                defaults={'label': label, 'sort_order': order, 'is_active': True},
            )

        self.stdout.write(self.style.SUCCESS('Catálogos base cargados correctamente.'))
