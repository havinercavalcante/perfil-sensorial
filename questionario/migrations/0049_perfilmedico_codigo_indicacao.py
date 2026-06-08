import uuid

from django.db import migrations, models


def gerar_codigos(apps, schema_editor):
    PerfilMedico = apps.get_model("questionario", "PerfilMedico")
    for perfil in PerfilMedico.objects.all():
        perfil.codigo_indicacao = uuid.uuid4()
        perfil.save(update_fields=["codigo_indicacao"])


class Migration(migrations.Migration):

    dependencies = [
        ("questionario", "0048_indicacao"),
    ]

    operations = [
        migrations.AddField(
            model_name="perfilmedico",
            name="codigo_indicacao",
            field=models.UUIDField(null=True, editable=False, verbose_name="Código de indicação"),
        ),
        migrations.RunPython(gerar_codigos, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="perfilmedico",
            name="codigo_indicacao",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                unique=True,
                verbose_name="Código de indicação",
            ),
        ),
    ]
