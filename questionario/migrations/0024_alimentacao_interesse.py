from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionario', '0023_linguagem_fluencia_consciencia_fono'),
    ]

    operations = [
        migrations.AddField(
            model_name='avaliacaoalimentacao',
            name='pont_interesse',
            field=models.IntegerField(blank=True, null=True, verbose_name='Interesse e Apetite'),
        ),
    ]
