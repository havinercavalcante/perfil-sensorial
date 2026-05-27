"""
Fix UUID format: strip hyphens from all UUID columns added in migration 0029.
Django's UUIDField stores values as 32-character hex WITHOUT hyphens in SQLite.
Migration 0029 used str(uuid.uuid4()) which produces hyphenated strings, causing
filter() to fail (WHERE uuid = <no hyphens> vs stored <with hyphens>).
"""
from django.db import migrations

MODELS = [
    "avaliacao",
    "avaliacaovineland",
    "avaliacaoescolar",
    "avaliacaobebe",
    "avaliacaoedm",
    "avaliacaomabc2",
    "avaliacaobeery",
    "avaliacaopedi",
    "avaliacaospm",
    "avaliacaovineland3",
    "avaliacaoportage",
    "avaliacaosdq",
    "avaliacaosnapiv",
    "avaliacaomchat",
    "avaliacaocars",
    "avaliacaolinguagem",
    "avaliacaoalimentacao",
    "avaliacaohabitosorais",
    "avaliacaovozinfantil",
    "avaliacaoprocessamentoauditivo",
    "avaliacaoidv10",
    "avaliacaodesenvolvimento",
    "avaliacaosono",
    "avaliacaohabilidadesadaptativas",
    "avaliacaocomportamentofuncional",
    "avaliacaorastreiocognitivo",
    "avaliacaopsicopedagogica",
]


def strip_uuid_hyphens(apps, schema_editor):
    """Remove hyphens from UUID values so Django can look them up correctly."""
    db_alias = schema_editor.connection.alias
    with schema_editor.connection.cursor() as cursor:
        for model_name in MODELS:
            table = f"questionario_{model_name}"
            try:
                cursor.execute(
                    f"UPDATE \"{table}\" SET uuid = REPLACE(uuid, '-', '') "
                    f"WHERE uuid LIKE '%-%'"
                )
                updated = cursor.rowcount
                if updated:
                    print(f"  Fixed {updated} rows in {table}")
            except Exception as e:
                print(f"  Warning: could not fix {table}: {e}")


def restore_uuid_hyphens(apps, schema_editor):
    """Reverse: re-insert hyphens into UUIDs (for rollback)."""
    with schema_editor.connection.cursor() as cursor:
        for model_name in MODELS:
            table = f"questionario_{model_name}"
            try:
                # Convert 32-char hex back to 8-4-4-4-12 format
                cursor.execute(f'SELECT id, uuid FROM "{table}" WHERE LENGTH(uuid) = 32')
                rows = cursor.fetchall()
                for row_id, hex_uuid in rows:
                    hyphenated = f"{hex_uuid[0:8]}-{hex_uuid[8:12]}-{hex_uuid[12:16]}-{hex_uuid[16:20]}-{hex_uuid[20:32]}"
                    cursor.execute(f'UPDATE "{table}" SET uuid = %s WHERE id = %s', [hyphenated, row_id])
            except Exception as e:
                print(f"  Warning: could not restore {table}: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ("questionario", "0029_add_uuid_to_avaliacoes"),
    ]

    operations = [
        migrations.RunPython(strip_uuid_hyphens, restore_uuid_hyphens),
    ]
