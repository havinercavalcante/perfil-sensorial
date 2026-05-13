from django.db import migrations

MODULOS = [
    ("sensorial", "Perfil Sensorial", "Questionário Perfil Sensorial (9 seções)"),
    ("vineland", "Escala Vineland", "Vineland Adaptive Behavior Scales"),
    ("escolar", "Questionário Sensorial Escolar", "Perfil Sensorial para contexto escolar"),
    ("bebe", "Perfil Sensorial Bebê/Criança Pequena", "Para crianças de 0 a 36 meses"),
    ("spm", "SPM — Sensory Processing Measure", "SPM-P (2–5 anos) e SPM (5–12 anos)"),
    ("edm", "EDM Figueiredo", "Escala de Desenvolvimento Motor"),
    ("mabc2", "MABC-2", "Movement Assessment Battery for Children"),
    ("beery", "Beery VMI", "Beery-Buktenica Developmental Test of VMI"),
    ("pedi", "PEDI", "Pediatric Evaluation of Disability Inventory"),
]


def popular_modulos(apps, schema_editor):
    ModuloAvaliacao = apps.get_model("questionario", "ModuloAvaliacao")
    for codigo, nome, descricao in MODULOS:
        ModuloAvaliacao.objects.get_or_create(
            codigo=codigo,
            defaults={"nome": nome, "descricao": descricao},
        )


def remover_modulos(apps, schema_editor):
    ModuloAvaliacao = apps.get_model("questionario", "ModuloAvaliacao")
    ModuloAvaliacao.objects.filter(codigo__in=[m[0] for m in MODULOS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("questionario", "0011_modulos_avaliacao"),
    ]

    operations = [
        migrations.RunPython(popular_modulos, remover_modulos),
    ]
