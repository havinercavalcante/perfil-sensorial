import os

from django.core.management import call_command
from django.contrib.staticfiles.management.commands.runserver import Command as RunserverCommand


class Command(RunserverCommand):
    def handle(self, *args, **options):
        if not os.environ.get('RUN_MAIN'):
            self.stdout.write("==> Gerando migrações...")
            call_command("makemigrations", verbosity=1)

            self.stdout.write("==> Aplicando migrações...")
            call_command("migrate", verbosity=1)

        super().handle(*args, **options)
