from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("questionario", "0016_avaliacaopedi_token"),
    ]

    operations = [
        migrations.AddField(
            model_name="avaliacaopedi",
            name="respostas_json",
            field=models.TextField(blank=True, default="{}"),
        ),
        migrations.AddField(
            model_name="avaliacaopedi",
            name="pagina_atual",
            field=models.IntegerField(default=0),
        ),
    ]
