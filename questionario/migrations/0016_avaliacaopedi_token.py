from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("questionario", "0015_portage_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="avaliacaopedi",
            name="token",
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
    ]
