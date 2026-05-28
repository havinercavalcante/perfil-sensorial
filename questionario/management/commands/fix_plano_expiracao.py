"""
Comando: python manage.py fix_plano_expiracao

Define plano_expiracao para todos os PerfilMedico com plano pago
que ainda não têm data de vencimento.

Lógica:
  - Base: user.date_joined + 30 dias
  - Se esse resultado já passou → hoje + 30 dias (não bloqueia ninguém na hora)
"""
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Define plano_expiracao para usuários com plano pago sem data de vencimento"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Mostra o que seria alterado sem salvar nada",
        )

    def handle(self, *args, **options):
        from questionario.models import PerfilMedico

        dry_run = options["dry_run"]
        agora   = timezone.now()

        perfis = PerfilMedico.objects.filter(
            plano__in=("start", "plus", "elite"),
            plano_expiracao__isnull=True,
        ).select_related("user")

        total = perfis.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS("Nenhum perfil sem data de vencimento. Tudo ok!"))
            return

        self.stdout.write(f"Encontrados {total} perfil(s) sem data de vencimento:\n")

        atualizados = 0
        for perfil in perfis:
            # Calcula: date_joined + 30 dias
            base = perfil.user.date_joined + timezone.timedelta(days=30)
            # Se já passou, dá mais 30 dias a partir de hoje
            expiracao = base if base > agora else agora + timezone.timedelta(days=30)

            nome = perfil.user.get_full_name() or perfil.user.username
            self.stdout.write(
                f"  {nome} ({perfil.get_plano_display()}) "
                f"→ vence em {expiracao.strftime('%d/%m/%Y')}"
                + (" [cadastro recente]" if base > agora else " [prazo renovado desde hoje]")
            )

            if not dry_run:
                perfil.plano_expiracao = expiracao
                perfil.save(update_fields=["plano_expiracao"])
                atualizados += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(f"\n[DRY RUN] Nenhuma alteração salva. Total: {total}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"\n✅ {atualizados} perfil(s) atualizado(s)."))
