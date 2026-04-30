import uuid
from django.db import migrations, models


def populate_uuid(apps, schema_editor):
    Paciente = apps.get_model('questionario', 'Paciente')
    for paciente in Paciente.objects.all():
        paciente.uuid = uuid.uuid4()
        paciente.save(update_fields=['uuid'])


class Migration(migrations.Migration):

    dependencies = [
        ('questionario', '0003_vineland_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='paciente',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.RunPython(populate_uuid, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='paciente',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
