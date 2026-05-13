from django.apps import AppConfig


class QuestionarioConfig(AppConfig):
    name = 'questionario'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(_sincronizar_modulos, sender=self)


def _sincronizar_modulos(sender, **kwargs):
    """
    Garante que todos os módulos definidos em ModuloAvaliacao.MODULO_CHOICES
    existam no banco. Executado automaticamente após cada 'manage.py migrate'.
    Para adicionar um novo módulo: basta incluir em MODULO_CHOICES e rodar migrate.
    """
    try:
        from questionario.models import ModuloAvaliacao
    except Exception:
        return

    for codigo, nome in ModuloAvaliacao.MODULO_CHOICES:
        ModuloAvaliacao.objects.get_or_create(
            codigo=codigo,
            defaults={"nome": nome},
        )
