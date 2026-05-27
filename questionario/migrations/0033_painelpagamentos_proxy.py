from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("questionario", "0032_plano_expiracao"),
    ]

    operations = [
        migrations.CreateModel(
            name="PainelPagamentos",
            fields=[],
            options={
                "verbose_name": "💳 Painel de Pagamentos",
                "verbose_name_plural": "💳 Painel de Pagamentos",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("questionario.solicitacaoplano",),
        ),
    ]
