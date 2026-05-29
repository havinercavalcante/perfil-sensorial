import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionario', '0038_add_psicologia_lote2_models'),
    ]

    operations = [
        # ── Denver II ───────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='AvaliacaoDenver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('data', models.DateField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('em_andamento', 'Em andamento'), ('concluida', 'Concluída')], default='em_andamento', max_length=20)),
                ('pont_pessoal_social', models.IntegerField(blank=True, null=True)),
                ('pont_motor_fino', models.IntegerField(blank=True, null=True)),
                ('pont_linguagem', models.IntegerField(blank=True, null=True)),
                ('pont_motor_grosseiro', models.IntegerField(blank=True, null=True)),
                ('observacoes', models.TextField(blank=True, default='')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='avaliacoes_denver', to='questionario.paciente')),
            ],
            options={'verbose_name': 'Avaliação Denver II', 'ordering': ['-data']},
        ),
        migrations.CreateModel(
            name='RespostaDenver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_item', models.IntegerField()),
                ('valor', models.IntegerField(blank=True, null=True)),
                ('observacao', models.TextField(blank=True, default='')),
                ('avaliacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='respostas', to='questionario.avaliacaodenver')),
            ],
            options={'ordering': ['numero_item'], 'unique_together': {('avaliacao', 'numero_item')}},
        ),
        # ── QMPI ────────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='AvaliacaoQMPI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('data', models.DateField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('em_andamento', 'Em andamento'), ('concluida', 'Concluída')], default='em_andamento', max_length=20)),
                ('token', models.CharField(blank=True, default='', max_length=64)),
                ('pont_ansiedade', models.IntegerField(blank=True, null=True)),
                ('pont_depressao', models.IntegerField(blank=True, null=True)),
                ('pont_tdah', models.IntegerField(blank=True, null=True)),
                ('pont_conduta', models.IntegerField(blank=True, null=True)),
                ('pont_autismo', models.IntegerField(blank=True, null=True)),
                ('observacoes', models.TextField(blank=True, default='')),
                ('email_enviado_em', models.DateTimeField(blank=True, null=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='avaliacoes_qmpi', to='questionario.paciente')),
            ],
            options={'verbose_name': 'Avaliação QMPI', 'ordering': ['-data']},
        ),
        migrations.CreateModel(
            name='RespostaQMPI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_item', models.IntegerField()),
                ('valor', models.IntegerField()),
                ('observacao', models.TextField(blank=True, default='')),
                ('avaliacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='respostas', to='questionario.avaliacaoqmpi')),
            ],
            options={'ordering': ['numero_item'], 'unique_together': {('avaliacao', 'numero_item')}},
        ),
        # ── Questionário de Dislexia (Pais) ─────────────────────────────────────
        migrations.CreateModel(
            name='AvaliacaoQuestDislexia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('data', models.DateField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('em_andamento', 'Em andamento'), ('concluida', 'Concluída')], default='em_andamento', max_length=20)),
                ('token', models.CharField(blank=True, default='', max_length=64)),
                ('pont_linguagem_oral', models.IntegerField(blank=True, null=True)),
                ('pont_leitura_escrita', models.IntegerField(blank=True, null=True)),
                ('pont_memoria', models.IntegerField(blank=True, null=True)),
                ('pont_atencao', models.IntegerField(blank=True, null=True)),
                ('pont_total', models.IntegerField(blank=True, null=True)),
                ('observacoes', models.TextField(blank=True, default='')),
                ('email_enviado_em', models.DateTimeField(blank=True, null=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='avaliacoes_quest_dislexia', to='questionario.paciente')),
            ],
            options={'verbose_name': 'Questionário de Dislexia (Pais)', 'ordering': ['-data']},
        ),
        migrations.CreateModel(
            name='RespostaQuestDislexia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_item', models.IntegerField()),
                ('valor', models.IntegerField()),
                ('observacao', models.TextField(blank=True, default='')),
                ('avaliacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='respostas', to='questionario.avaliacaoquestdislexia')),
            ],
            options={'ordering': ['numero_item'], 'unique_together': {('avaliacao', 'numero_item')}},
        ),
        # ── Checklist de Dislexia ────────────────────────────────────────────────
        migrations.CreateModel(
            name='AvaliacaoChecklistDislexia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('data', models.DateField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('em_andamento', 'Em andamento'), ('concluida', 'Concluída')], default='em_andamento', max_length=20)),
                ('token', models.CharField(blank=True, default='', max_length=64)),
                ('pont_leitura', models.IntegerField(blank=True, null=True)),
                ('pont_escrita', models.IntegerField(blank=True, null=True)),
                ('pont_processamento', models.IntegerField(blank=True, null=True)),
                ('pont_total', models.IntegerField(blank=True, null=True)),
                ('observacoes', models.TextField(blank=True, default='')),
                ('email_enviado_em', models.DateTimeField(blank=True, null=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='avaliacoes_checklist_dislexia', to='questionario.paciente')),
            ],
            options={'verbose_name': 'Checklist de Dislexia', 'ordering': ['-data']},
        ),
        migrations.CreateModel(
            name='RespostaChecklistDislexia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_item', models.IntegerField()),
                ('valor', models.IntegerField()),
                ('observacao', models.TextField(blank=True, default='')),
                ('avaliacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='respostas', to='questionario.avaliacaochecklistdislexia')),
            ],
            options={'ordering': ['numero_item'], 'unique_together': {('avaliacao', 'numero_item')}},
        ),
        # ── Protocolo Dislexia — Professor ───────────────────────────────────────
        migrations.CreateModel(
            name='AvaliacaoProtDislexiaProf',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('data', models.DateField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('em_andamento', 'Em andamento'), ('concluida', 'Concluída')], default='em_andamento', max_length=20)),
                ('token', models.CharField(blank=True, default='', max_length=64)),
                ('pont_leitura', models.IntegerField(blank=True, null=True)),
                ('pont_escrita', models.IntegerField(blank=True, null=True)),
                ('pont_matematica', models.IntegerField(blank=True, null=True)),
                ('pont_organizacao', models.IntegerField(blank=True, null=True)),
                ('observacoes', models.TextField(blank=True, default='')),
                ('email_enviado_em', models.DateTimeField(blank=True, null=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='avaliacoes_prot_dislexia_prof', to='questionario.paciente')),
            ],
            options={'verbose_name': 'Protocolo Dislexia — Professor', 'ordering': ['-data']},
        ),
        migrations.CreateModel(
            name='RespostaProtDislexiaProf',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_item', models.IntegerField()),
                ('valor', models.IntegerField()),
                ('observacao', models.TextField(blank=True, default='')),
                ('avaliacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='respostas', to='questionario.avaliacaoprotdislexiaprof')),
            ],
            options={'ordering': ['numero_item'], 'unique_together': {('avaliacao', 'numero_item')}},
        ),
        # ── Inventário de Sinais Disléxicos ──────────────────────────────────────
        migrations.CreateModel(
            name='AvaliacaoInventarioDislexia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('data', models.DateField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('em_andamento', 'Em andamento'), ('concluida', 'Concluída')], default='em_andamento', max_length=20)),
                ('historico_escolar', models.TextField(blank=True, default='', verbose_name='Histórico Escolar')),
                ('desempenho_leitura', models.TextField(blank=True, default='', verbose_name='Desempenho em Leitura')),
                ('desempenho_escrita', models.TextField(blank=True, default='', verbose_name='Desempenho em Escrita')),
                ('processamento_fonologico', models.TextField(blank=True, default='', verbose_name='Processamento Fonológico')),
                ('memoria_trabalho', models.TextField(blank=True, default='', verbose_name='Memória de Trabalho')),
                ('velocidade_processamento', models.TextField(blank=True, default='', verbose_name='Velocidade de Processamento')),
                ('historico_familiar', models.TextField(blank=True, default='', verbose_name='Histórico Familiar')),
                ('avaliacoes_anteriores', models.TextField(blank=True, default='', verbose_name='Avaliações Anteriores')),
                ('observacoes', models.TextField(blank=True, default='', verbose_name='Observações Clínicas')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='avaliacoes_inventario_dislexia', to='questionario.paciente')),
            ],
            options={'verbose_name': 'Inventário de Sinais Disléxicos', 'ordering': ['-data']},
        ),
    ]
