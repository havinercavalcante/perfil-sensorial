from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionario', '0004_paciente_uuid'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='perfilmedico',
            options={'verbose_name': 'Perfil do Profissional', 'verbose_name_plural': 'Perfis dos Profissionais'},
        ),
        migrations.RenameField(
            model_name='perfilmedico',
            old_name='crm',
            new_name='registro_profissional',
        ),
        migrations.AlterField(
            model_name='perfilmedico',
            name='registro_profissional',
            field=models.CharField(blank=True, max_length=30, verbose_name='Registro Profissional'),
        ),
    ]
