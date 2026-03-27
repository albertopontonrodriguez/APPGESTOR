from django.core.management.base import BaseCommand

from apps.accounts.models import User
from apps.brands.models import Brand


class Command(BaseCommand):
    help = 'Crea una instalación base limpia: marca principal y usuarios iniciales, sin datos de ejemplo.'

    def handle(self, *args, **options):
        Brand.objects.get_or_create(
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
            ('admin', 'Administrador', 'admin'),
            ('ainara', 'Ainara', 'ceo'),
            ('maria', 'María', 'ceo'),
        ]
        for username, display_name, role in users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'display_name': display_name,
                    'email': f'{username}@gestor.local',
                    'role': role,
                    'is_active': True,
                },
            )
            user.display_name = display_name
            user.role = role
            user.is_active = True
            if created or not user.has_usable_password():
                user.set_password('gestor')
            user.save()

        self.stdout.write(self.style.SUCCESS('Instalación base limpia creada: usuarios admin, ainara y maria con contraseña gestor.'))
