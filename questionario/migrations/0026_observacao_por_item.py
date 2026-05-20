from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionario', '0025_fono_habitos_voz_auditivo_idv10'),
    ]

    operations = [
        migrations.AddField(
            model_name='respostasdq',
            name='observacao',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='respostasnapiv',
            name='observacao',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='respostalinguagem',
            name='observacao',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='respostaalimentacao',
            name='observacao',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='respostahabitosorais',
            name='observacao',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='respostavozinfantil',
            name='observacao',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='respostaprocessamentoauditivo',
            name='observacao',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='respostaidv10',
            name='observacao',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='respostadesenvolvimento',
            name='observacao',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='respostasono',
            name='observacao',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='respostahabilidadesadaptativas',
            name='observacao',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='respostacomportamentofuncional',
            name='observacao',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='respostarastreiocognitivo',
            name='observacao',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='respostapsicopedagogica',
            name='observacao',
            field=models.TextField(blank=True, default=''),
        ),
    ]
