from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = 'Prepara una instalación local limpia y, opcionalmente, añade datos demo.'

    def add_arguments(self, parser):
        parser.add_argument('--with-demo', action='store_true', help='Cargar también datos demo y usuarios de prueba.')

    def handle(self, *args, **options):
        self.stdout.write('Aplicando estructura de base de datos...')
        call_command('makemigrations', interactive=False)
        call_command('migrate', run_syncdb=True, interactive=False)

        self.stdout.write('Cargando catálogos base...')
        call_command('seed_catalogs')

        self.stdout.write('Creando usuarios iniciales y configuración base...')
        call_command('bootstrap_basic')

        if options.get('with_demo'):
            self.stdout.write('Cargando datos demo...')
            call_command('bootstrap_demo')

        self.stdout.write(self.style.SUCCESS('Instalación local completada correctamente.'))
