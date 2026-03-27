from datetime import date, timedelta

from django.utils import timezone
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from apps.accounts.models import User
from apps.billing.models import InvoiceIssued, InvoiceReceived
from apps.bookings.models import Booking, Payment
from apps.brands.models import Brand
from apps.configuration.models import Currency, GoogleSheetsSettings, Language, StatusCatalog
from apps.expenses.models import Expense, ExpenseCategory, Supplier
from apps.notifications.services import sync_all_notifications
from apps.travelers.models import Traveler
from apps.trips.models import Trip
from apps.crm.models import EmailTemplate, Lead, LeadActivity
from apps.planner.models import CalendarEvent, Task
from apps.internal_chat.models import ChatMessage, ChatRoom


class Command(BaseCommand):
    help = 'Carga datos mínimos de demostración para poder entrar y revisar GESTOR rápidamente.'

    def handle(self, *args, **options):
        existing_tables = set(connection.introspection.table_names())
        required_tables = {
            'configuration_currency', 'configuration_language', 'configuration_statuscatalog',
            'accounts_user', 'brands_brand', 'travelers_traveler', 'trips_trip', 'bookings_booking',
        }
        if not required_tables.issubset(existing_tables):
            raise CommandError(
                'La base de datos todavía no está preparada. Ejecuta primero: python manage.py migrate --run-syncdb o python manage.py setup_local --with-demo'
            )

        self._seed_catalogs()
        brand, _ = Brand.objects.get_or_create(
            name='55º',
            defaults={
                'legal_name': '55 Grados Norte',
                'website': 'https://www.55gradosnorte.com/',
                'email': 'info@55gradosnorte.com',
                'primary_language': 'es',
                'primary_currency': 'EUR',
                'accent_color': '#5B7F3A',
            },
        )

        users = [
            ('admin', 'Administrador', 'admin', 'Gestor2026!'),
            ('ainara', 'Ainara', 'ceo', 'Gestor2026!'),
            ('maria', 'María', 'ceo', 'Gestor2026!'),
        ]
        for username, display_name, role, password in users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'display_name': display_name,
                    'email': f'{username}@gestor.local',
                    'role': role,
                    'is_active': True,
                },
            )
            if created or not user.has_usable_password():
                user.set_password(password)
                user.role = role
                user.display_name = display_name
                user.is_active = True
                user.save()

        manager = User.objects.filter(username='ainara').first()

        traveler, _ = Traveler.objects.get_or_create(
            brand=brand,
            first_name='Lucía',
            last_name='Navarro',
            defaults={
                'email': 'lucia@example.com',
                'phone': '+34 600 000 001',
                'preferred_language': 'es',
                'dni': '00000000A',
                'photo_authorization': True,
            },
        )

        trip, _ = Trip.objects.get_or_create(
            brand=brand,
            name='Svalbard en moto de nieve',
            defaults={
                'destination': 'Svalbard',
                'trip_type': 'Expedición',
                'description': 'Viaje de demostración para revisar el panel.',
                'start_date': date.today() + timedelta(days=45),
                'end_date': date.today() + timedelta(days=52),
                'total_slots': 10,
                'base_price': Decimal('3490.00'),
                'currency': 'EUR',
                'status': 'open',
                'manager': manager,
            },
        )

        booking, _ = Booking.objects.get_or_create(
            traveler=traveler,
            trip=trip,
            defaults={
                'final_price': Decimal('3490.00'),
                'currency': 'EUR',
                'required_deposit': Decimal('900.00'),
                'status': 'deposit_pending',
                'due_date': date.today() + timedelta(days=10),
                'internal_notes': 'Reserva de demostración cargada automáticamente.',
            },
        )

        Payment.objects.get_or_create(
            booking=booking,
            amount=Decimal('900.00'),
            payment_date=date.today(),
            method='bank_transfer',
            defaults={
                'currency': 'EUR',
                'reference': 'DEMO-DEP-001',
                'status': 'confirmed',
                'is_reconciled': True,
            },
        )
        booking.refresh_financials()

        category, _ = ExpenseCategory.objects.get_or_create(name='Alojamiento', defaults={'is_active': True})
        supplier, _ = Supplier.objects.get_or_create(
            brand=brand,
            legal_name='Arctic Lodge AS',
            defaults={
                'trade_name': 'Arctic Lodge',
                'supplier_type': 'accommodation',
                'country': 'Noruega',
                'default_currency': 'EUR',
            },
        )
        expense, _ = Expense.objects.get_or_create(
            brand=brand,
            trip=trip,
            supplier=supplier,
            category=category,
            expense_date=date.today(),
            amount=Decimal('1200.00'),
            defaults={
                'currency': 'EUR',
                'description': 'Reserva de alojamiento para la expedición de prueba.',
                'payment_status': 'pending',
            },
        )

        InvoiceIssued.objects.get_or_create(
            brand=brand,
            traveler=traveler,
            booking=booking,
            invoice_number='EMI-2026-0001',
            defaults={
                'issue_date': date.today(),
                'taxable_base': Decimal('2884.30'),
                'vat_amount': Decimal('605.70'),
                'total_amount': Decimal('3490.00'),
                'currency': 'EUR',
                'status': 'sent',
                'notes': 'Factura de demostración.',
            },
        )

        InvoiceReceived.objects.get_or_create(
            brand=brand,
            supplier=supplier,
            expense=expense,
            invoice_number='PROV-2026-001',
            defaults={
                'issue_date': date.today(),
                'taxable_base': Decimal('991.74'),
                'vat_amount': Decimal('208.26'),
                'total_amount': Decimal('1200.00'),
                'currency': 'EUR',
                'notes': 'Factura recibida de demostración.',
            },
        )

        lead, _ = Lead.objects.get_or_create(
            brand=brand,
            full_name='Carlos Vega',
            defaults={
                'email': 'carlos.vega@example.com',
                'phone': '+34 600 000 020',
                'source': 'web',
                'stage': 'proposal',
                'owner': manager,
                'preferred_language': 'es',
                'destination_interest': 'Svalbard y auroras',
                'trip_interest': trip,
                'estimated_value': Decimal('3490.00'),
                'currency': 'EUR',
                'next_follow_up': date.today() + timedelta(days=1),
                'notes': 'Lead de ejemplo para revisar el CRM comercial.',
            },
        )
        LeadActivity.objects.get_or_create(
            lead=lead,
            summary='Llamada inicial realizada',
            defaults={
                'activity_type': 'call',
                'notes': 'Interés alto. Solicita propuesta y condiciones.',
                'created_by': manager,
            },
        )

        EmailTemplate.objects.get_or_create(
            brand=brand,
            name='Primer seguimiento comercial',
            language='es',
            defaults={
                'stage_hint': 'contacted',
                'subject_template': 'Seguimiento de {brand_name} para {destination}',
                'body_template': 'Hola {lead_first_name},\n\nGracias por tu interés en {brand_name}. Te escribo para continuar con la propuesta sobre {destination}.\n\nSi te viene bien, podemos avanzar con el viaje {trip_name} y dejar una llamada de seguimiento para el {follow_up_date}.\n\nUn saludo,\n{owner_name}',
                'is_active': True,
                'notes': 'Plantilla base para leads con primer contacto realizado.',
            },
        )
        EmailTemplate.objects.get_or_create(
            brand=brand,
            name='Propuesta enviada',
            language='es',
            defaults={
                'stage_hint': 'proposal',
                'subject_template': 'Tu propuesta para {trip_name}',
                'body_template': 'Hola {lead_first_name},\n\nTe envío el resumen de la propuesta para {trip_name}. El valor estimado es de {estimated_value} {currency}.\n\nQuedo pendiente para resolver dudas y confirmar siguientes pasos.\n\nGracias,\n{owner_name}',
                'is_active': True,
                'notes': 'Plantilla orientada a leads con propuesta ya enviada.',
            },
        )

        Task.objects.get_or_create(
            brand=brand,
            title='Revisar documentación de Lucía Navarro',
            defaults={
                'task_type': 'documentation',
                'description': 'Comprobar pasaporte y autorización de fotografías antes de salida.',
                'due_date': date.today() + timedelta(days=2),
                'status': 'pending',
                'priority': 'high',
                'assigned_to': manager,
                'created_by': manager,
                'traveler': traveler,
                'trip': trip,
                'booking': booking,
            },
        )
        CalendarEvent.objects.get_or_create(
            brand=brand,
            title='Seguimiento comercial Carlos Vega',
            defaults={
                'event_type': 'follow_up',
                'start_at': timezone.now() + timedelta(days=1),
                'end_at': timezone.now() + timedelta(days=1, hours=1),
                'status': 'scheduled',
                'priority': 'high',
                'assigned_to': manager,
                'lead': lead,
                'location': 'Llamada / online',
                'notes': 'Confirmar interés y enviar propuesta definitiva.',
            },
        )

        GoogleSheetsSettings.objects.get_or_create(
            name='Principal',
            defaults={'is_enabled': False, 'auto_sync_enabled': False, 'spreadsheet_name': 'GESTOR 55º', 'default_sheet_prefix': 'GESTOR'},
        )

        sala, _ = ChatRoom.objects.get_or_create(
            name='Equipo general',
            defaults={'description': 'Sala interna principal del equipo.', 'created_by': manager, 'is_active': True},
        )
        sala.participants.add(*User.objects.filter(username__in=['admin', 'ainara', 'maria']))
        if not sala.messages.exists():
            ChatMessage.objects.create(room=sala, author=manager, body='Bienvenidas a GESTOR. Este chat interno ya está preparado para coordinar el trabajo diario.')

        sync_all_notifications()
        self.stdout.write(self.style.SUCCESS('Datos de demostración cargados.'))
        self.stdout.write('Accesos creados: admin / ainara / maria')
        self.stdout.write('Contraseña para todos: Gestor2026!')

    def _seed_catalogs(self):
        currencies = [
            ('EUR', 'Euro', '€', 1),
            ('USD', 'Dólar estadounidense', '$', 2),
            ('NOK', 'Corona noruega', 'kr', 3),
        ]
        languages = [
            ('es', 'Español', 1),
            ('en', 'Inglés', 2),
        ]
        for code, name, symbol, order in currencies:
            Currency.objects.get_or_create(code=code, defaults={'name': name, 'symbol': symbol, 'is_active': True, 'sort_order': order})
        for code, name, order in languages:
            Language.objects.get_or_create(code=code, defaults={'name': name, 'is_active': True, 'sort_order': order})

        status_payload = [
            ('trip', 'draft', 'Borrador', 1),
            ('trip', 'open', 'Abierto', 2),
            ('trip', 'full', 'Completo', 3),
            ('trip', 'closed', 'Cerrado', 4),
            ('trip', 'cancelled', 'Cancelado', 5),
            ('booking', 'pending_confirmation', 'Pendiente de confirmar', 1),
            ('booking', 'deposit_pending', 'Señal pendiente', 2),
            ('booking', 'deposit_paid', 'Señal pagada', 3),
            ('booking', 'paid', 'Pagado', 4),
            ('booking', 'cancelled', 'Cancelado', 5),
            ('expense_payment', 'pending', 'Pendiente', 1),
            ('expense_payment', 'partial', 'Pago parcial', 2),
            ('expense_payment', 'paid', 'Pagado', 3),
            ('invoice_issued', 'draft', 'Borrador', 1),
            ('invoice_issued', 'sent', 'Enviada', 2),
            ('invoice_issued', 'paid', 'Pagada', 3),
            ('payment', 'pending', 'Pendiente', 1),
            ('payment', 'confirmed', 'Confirmado', 2),
        ]
        for group, code, label, order in status_payload:
            StatusCatalog.objects.get_or_create(
                status_group=group,
                code=code,
                defaults={'label': label, 'is_active': True, 'sort_order': order},
            )
