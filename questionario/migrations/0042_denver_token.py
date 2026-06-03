from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("questionario", "0041_remove_anamneses"),
    ]

    operations = [
        migrations.AddField(
            model_name="avaliacaodenver",
            name="token",
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="avaliacaodenver",
            name="email_enviado_em",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
