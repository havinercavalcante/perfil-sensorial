import uuid
from django.db import migrations, models


def gerar_tokens(apps, schema_editor):
    Documento = apps.get_model("documentos", "Documento")
    for doc in Documento.objects.all():
        doc.token = uuid.uuid4()
        doc.save(update_fields=["token"])


class Migration(migrations.Migration):

    dependencies = [
        ("documentos", "0002_alter_documento_arquivo"),
    ]

    operations = [
        migrations.AddField(
            model_name="documento",
            name="token",
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True, verbose_name="Token"),
        ),
        migrations.RunPython(gerar_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="documento",
            name="token",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Token"),
        ),
    ]
