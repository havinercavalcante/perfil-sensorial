"""
Migration: adiciona campo uuid (UUIDField único) a todos os modelos Avaliacao*.

Estratégia em 3 passos para SQLite (que não suporta ADD UNIQUE em tabelas existentes):
  1. Adiciona o campo sem unique (nullable)
  2. Data migration: preenche uuid único para cada linha existente
  3. Altera para unique=True e editable=False
"""
import uuid as uuid_lib
from django.db import migrations, models


MODELS = [
    'avaliacao', 'avaliacaoalimentacao', 'avaliacaobebe', 'avaliacaobeery',
    'avaliacaocars', 'avaliacaocomportamentofuncional', 'avaliacaodesenvolvimento',
    'avaliacaoedm', 'avaliacaoescolar', 'avaliacaohabilidadesadaptativas',
    'avaliacaohabitosorais', 'avaliacaoidv10', 'avaliacaolinguagem', 'avaliacaomabc2',
    'avaliacaomchat', 'avaliacaopedi', 'avaliacaoportage', 'avaliacaoprocessamentoauditivo',
    'avaliacaopsicopedagogica', 'avaliacaorastreiocognitivo', 'avaliacaosdq',
    'avaliacaosnapiv', 'avaliacaosono', 'avaliacaospm', 'avaliacaovineland',
    'avaliacaovineland3', 'avaliacaovozinfantil',
]


def populate_uuids(apps, schema_editor):
    """Gera UUID único para cada linha existente em todos os modelos."""
    for model_name in MODELS:
        # Pega a tabela diretamente via SQL para não depender do estado do modelo
        table = f'questionario_{model_name}'
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(f'SELECT id FROM "{table}"')
            rows = cursor.fetchall()
            for (row_id,) in rows:
                cursor.execute(
                    f'UPDATE "{table}" SET uuid = %s WHERE id = %s',
                    [str(uuid_lib.uuid4()), row_id]
                )


class Migration(migrations.Migration):

    dependencies = [
        ('questionario', '0028_trial_perfilmedico'),
    ]

    operations = [
        # ── Passo 1: adiciona campo nullable (sem unique) ──────────────────────
        *[
            migrations.AddField(
                model_name=m,
                name='uuid',
                field=models.UUIDField(null=True, blank=True, editable=False),
            )
            for m in MODELS
        ],

        # ── Passo 2: popula uuid para todas as linhas existentes ───────────────
        migrations.RunPython(populate_uuids, migrations.RunPython.noop),

        # ── Passo 3: torna o campo unique=True e não-nulo ─────────────────────
        *[
            migrations.AlterField(
                model_name=m,
                name='uuid',
                field=models.UUIDField(default=uuid_lib.uuid4, editable=False, unique=True),
            )
            for m in MODELS
        ],
    ]
