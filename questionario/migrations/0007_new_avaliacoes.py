import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionario', '0006_observacoes_email_enviado'),
    ]

    operations = [
        # ── AvaliacaoEscolar ──────────────────────────────────────────────────
        migrations.CreateModel(
            name='AvaliacaoEscolar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=django.utils.timezone.now, verbose_name='Data da avaliação')),
                ('status', models.CharField(
                    choices=[('em_andamento', 'Em andamento'), ('concluida', 'Concluída')],
                    default='em_andamento', max_length=20,
                )),
                ('pagina_atual', models.IntegerField(default=1)),
                ('pont_auditivo', models.IntegerField(blank=True, null=True)),
                ('pont_visual', models.IntegerField(blank=True, null=True)),
                ('pont_tatil', models.IntegerField(blank=True, null=True)),
                ('pont_vestibular', models.IntegerField(blank=True, null=True)),
                ('pont_social', models.IntegerField(blank=True, null=True)),
                ('observacoes', models.TextField(blank=True, default='', verbose_name='Observações clínicas')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('paciente', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='avaliacoes_escolar',
                    to='questionario.paciente',
                )),
            ],
            options={
                'verbose_name': 'Questionário Sensorial Escolar',
                'ordering': ['-data'],
            },
        ),
        # ── RespostaEscolar ────────────────────────────────────────────────────
        migrations.CreateModel(
            name='RespostaEscolar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_item', models.IntegerField()),
                ('valor', models.IntegerField()),
                ('avaliacao', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='respostas',
                    to='questionario.avaliacaoescolar',
                )),
            ],
            options={
                'ordering': ['numero_item'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='respostaescolar',
            unique_together={('avaliacao', 'numero_item')},
        ),
        # ── AvaliacaoBebe ─────────────────────────────────────────────────────
        migrations.CreateModel(
            name='AvaliacaoBebe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('faixa', models.CharField(
                    choices=[('bebe', 'Bebê (0–6 meses)'), ('crianca_pequena', 'Criança Pequena (7–36 meses)')],
                    max_length=20,
                )),
                ('data', models.DateField(default=django.utils.timezone.now, verbose_name='Data da avaliação')),
                ('status', models.CharField(
                    choices=[('em_andamento', 'Em andamento'), ('concluida', 'Concluída')],
                    default='em_andamento', max_length=20,
                )),
                ('pagina_atual', models.IntegerField(default=1)),
                ('pont_busca', models.IntegerField(blank=True, null=True)),
                ('pont_evitamento', models.IntegerField(blank=True, null=True)),
                ('pont_sensibilidade', models.IntegerField(blank=True, null=True)),
                ('pont_registro', models.IntegerField(blank=True, null=True)),
                ('observacoes', models.TextField(blank=True, default='', verbose_name='Observações clínicas')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('paciente', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='avaliacoes_bebe',
                    to='questionario.paciente',
                )),
            ],
            options={
                'verbose_name': 'Perfil Sensorial Bebê/Criança Pequena',
                'ordering': ['-data'],
            },
        ),
        # ── RespostaBebe ──────────────────────────────────────────────────────
        migrations.CreateModel(
            name='RespostaBebe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_item', models.IntegerField()),
                ('valor', models.IntegerField()),
                ('avaliacao', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='respostas',
                    to='questionario.avaliacaobebe',
                )),
            ],
            options={
                'ordering': ['numero_item'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='respostabebe',
            unique_together={('avaliacao', 'numero_item')},
        ),
        # ── AvaliacaoEDM ──────────────────────────────────────────────────────
        migrations.CreateModel(
            name='AvaliacaoEDM',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=django.utils.timezone.now, verbose_name='Data da avaliação')),
                ('idade_motricidade_fina', models.IntegerField(blank=True, null=True, verbose_name='Motricidade Fina (meses)')),
                ('idade_motricidade_ampla', models.IntegerField(blank=True, null=True, verbose_name='Motricidade Ampla (meses)')),
                ('idade_equilibrio', models.IntegerField(blank=True, null=True, verbose_name='Equilíbrio (meses)')),
                ('idade_esquema_corporal', models.IntegerField(blank=True, null=True, verbose_name='Esquema Corporal (meses)')),
                ('idade_organizacao_espacial', models.IntegerField(blank=True, null=True, verbose_name='Organização Espacial (meses)')),
                ('idade_organizacao_temporal', models.IntegerField(blank=True, null=True, verbose_name='Organização Temporal (meses)')),
                ('lateralidade', models.CharField(
                    blank=True, max_length=20, null=True,
                    choices=[
                        ('definida_direita', 'Definida Direita'),
                        ('definida_esquerda', 'Definida Esquerda'),
                        ('cruzada', 'Cruzada'),
                        ('indefinida', 'Indefinida'),
                    ],
                    verbose_name='Lateralidade',
                )),
                ('idade_motora_geral', models.FloatField(blank=True, null=True, verbose_name='Idade Motora Geral (meses)')),
                ('quociente_motor', models.FloatField(blank=True, null=True, verbose_name='Quociente Motor (QM)')),
                ('observacoes', models.TextField(blank=True, default='', verbose_name='Observações clínicas')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('paciente', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='avaliacoes_edm',
                    to='questionario.paciente',
                )),
            ],
            options={
                'verbose_name': 'EDM — Escala de Desenvolvimento Motor',
                'ordering': ['-data'],
            },
        ),
        # ── AvaliacaoMABC2 ────────────────────────────────────────────────────
        migrations.CreateModel(
            name='AvaliacaoMABC2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('faixa_etaria', models.CharField(
                    choices=[('3_6', '3–6 anos'), ('7_10', '7–10 anos'), ('11_16', '11–16 anos')],
                    max_length=10, verbose_name='Faixa etária',
                )),
                ('data', models.DateField(default=django.utils.timezone.now, verbose_name='Data da avaliação')),
                ('md1_raw', models.FloatField(blank=True, null=True, verbose_name='Destreza Manual 1 (bruto)')),
                ('md2_raw', models.FloatField(blank=True, null=True, verbose_name='Destreza Manual 2 (bruto)')),
                ('md3_raw', models.FloatField(blank=True, null=True, verbose_name='Destreza Manual 3 (bruto)')),
                ('ac1_raw', models.FloatField(blank=True, null=True, verbose_name='Arremesso/Recepção 1 (bruto)')),
                ('ac2_raw', models.FloatField(blank=True, null=True, verbose_name='Arremesso/Recepção 2 (bruto)')),
                ('eq1_raw', models.FloatField(blank=True, null=True, verbose_name='Equilíbrio 1 (bruto)')),
                ('eq2_raw', models.FloatField(blank=True, null=True, verbose_name='Equilíbrio 2 (bruto)')),
                ('eq3_raw', models.FloatField(blank=True, null=True, verbose_name='Equilíbrio 3 (bruto)')),
                ('md_escore', models.IntegerField(blank=True, null=True, verbose_name='Escore Destreza Manual')),
                ('ac_escore', models.IntegerField(blank=True, null=True, verbose_name='Escore Arremesso/Recepção')),
                ('eq_escore', models.IntegerField(blank=True, null=True, verbose_name='Escore Equilíbrio')),
                ('escore_total', models.IntegerField(blank=True, null=True, verbose_name='Escore Total')),
                ('percentil', models.IntegerField(blank=True, null=True, verbose_name='Percentil')),
                ('observacoes', models.TextField(blank=True, default='', verbose_name='Observações clínicas')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('paciente', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='avaliacoes_mabc2',
                    to='questionario.paciente',
                )),
            ],
            options={
                'verbose_name': 'MABC-2',
                'ordering': ['-data'],
            },
        ),
        # ── AvaliacaoBeery ────────────────────────────────────────────────────
        migrations.CreateModel(
            name='AvaliacaoBeery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=django.utils.timezone.now, verbose_name='Data da avaliação')),
                ('idade_anos', models.IntegerField(blank=True, null=True, verbose_name='Idade (anos)')),
                ('idade_meses', models.IntegerField(blank=True, null=True, verbose_name='Idade (meses complementares)')),
                ('vmi_raw', models.IntegerField(blank=True, null=True, verbose_name='VMI — Escore bruto')),
                ('vp_raw', models.IntegerField(blank=True, null=True, verbose_name='Percepção Visual — Escore bruto')),
                ('mc_raw', models.IntegerField(blank=True, null=True, verbose_name='Coordenação Motora — Escore bruto')),
                ('vmi_escore', models.IntegerField(blank=True, null=True, verbose_name='VMI — Escore padrão')),
                ('vp_escore', models.IntegerField(blank=True, null=True, verbose_name='Percepção Visual — Escore padrão')),
                ('mc_escore', models.IntegerField(blank=True, null=True, verbose_name='Coordenação Motora — Escore padrão')),
                ('vmi_percentil', models.IntegerField(blank=True, null=True, verbose_name='VMI — Percentil')),
                ('vp_percentil', models.IntegerField(blank=True, null=True, verbose_name='Percepção Visual — Percentil')),
                ('mc_percentil', models.IntegerField(blank=True, null=True, verbose_name='Coordenação Motora — Percentil')),
                ('observacoes', models.TextField(blank=True, default='', verbose_name='Observações clínicas')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('paciente', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='avaliacoes_beery',
                    to='questionario.paciente',
                )),
            ],
            options={
                'verbose_name': 'Beery VMI',
                'ordering': ['-data'],
            },
        ),
        # ── AvaliacaoPEDI ─────────────────────────────────────────────────────
        migrations.CreateModel(
            name='AvaliacaoPEDI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=django.utils.timezone.now, verbose_name='Data da avaliação')),
                ('fs_autocuidado', models.IntegerField(blank=True, null=True, verbose_name='FS — Autocuidado (bruto, 0–73)')),
                ('fs_mobilidade', models.IntegerField(blank=True, null=True, verbose_name='FS — Mobilidade (bruto, 0–59)')),
                ('fs_funcao_social', models.IntegerField(blank=True, null=True, verbose_name='FS — Função Social (bruto, 0–65)')),
                ('ca_autocuidado', models.IntegerField(blank=True, null=True, verbose_name='CA — Autocuidado (0–40)')),
                ('ca_mobilidade', models.IntegerField(blank=True, null=True, verbose_name='CA — Mobilidade (0–40)')),
                ('ca_funcao_social', models.IntegerField(blank=True, null=True, verbose_name='CA — Função Social (0–40)')),
                ('fs_autocuidado_escala', models.FloatField(blank=True, null=True, verbose_name='FS — Autocuidado (escala 0–100)')),
                ('fs_mobilidade_escala', models.FloatField(blank=True, null=True, verbose_name='FS — Mobilidade (escala 0–100)')),
                ('fs_funcao_social_escala', models.FloatField(blank=True, null=True, verbose_name='FS — Função Social (escala 0–100)')),
                ('ca_autocuidado_escala', models.FloatField(blank=True, null=True, verbose_name='CA — Autocuidado (escala 0–100)')),
                ('ca_mobilidade_escala', models.FloatField(blank=True, null=True, verbose_name='CA — Mobilidade (escala 0–100)')),
                ('ca_funcao_social_escala', models.FloatField(blank=True, null=True, verbose_name='CA — Função Social (escala 0–100)')),
                ('observacoes', models.TextField(blank=True, default='', verbose_name='Observações clínicas')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('paciente', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='avaliacoes_pedi',
                    to='questionario.paciente',
                )),
            ],
            options={
                'verbose_name': 'PEDI',
                'ordering': ['-data'],
            },
        ),
    ]
