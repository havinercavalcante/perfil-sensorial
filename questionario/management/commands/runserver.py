import os
import shutil
import socket
import subprocess

from django.core.management import call_command
from django.contrib.staticfiles.management.commands.runserver import Command as RunserverCommand


def _kill_mailpit():
    subprocess.run(["pkill", "-f", "mailpit"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class Command(RunserverCommand):
    def handle(self, *args, **options):
        if not os.environ.get('RUN_MAIN'):
            self.stdout.write("==> Gerando migrações...")
            call_command("makemigrations", verbosity=1)

            self.stdout.write("==> Aplicando migrações...")
            call_command("migrate", verbosity=1)

            mailpit_bin = shutil.which("mailpit")
            if mailpit_bin:
                _kill_mailpit()
                os.makedirs("logs", exist_ok=True)
                subprocess.Popen(
                    [mailpit_bin, "--smtp", "[::]:1025", "--listen", "[::]:8025", "--log-file", "logs/mailpit.log"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                self.stdout.write("==> Mailpit iniciado em http://localhost:8025")
            else:
                self.stdout.write(self.style.WARNING("==> Mailpit não encontrado no PATH, pulando..."))

        super().handle(*args, **options)
