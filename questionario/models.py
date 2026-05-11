import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class PerfilMedico(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    registro_profissional = models.CharField("Registro Profissional", max_length=30, blank=True)
    especialidade = models.CharField("Especialidade", max_length=100, blank=True)
    telefone = models.CharField("Telefone", max_length=20, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Perfil do Profissional"
        verbose_name_plural = "Perfis dos Profissionais"

    def __str__(self):
        return f"Dr(a). {self.user.get_full_name() or self.user.username}"


class Paciente(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    medico = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pacientes")
    nome = models.CharField("Nome completo", max_length=200)
    data_nascimento = models.DateField("Data de nascimento")
    responsavel = models.CharField("Nome do responsável", max_length=200)
    email_responsavel = models.EmailField("E-mail do responsável", blank=True)
    telefone = models.CharField("Telefone", max_length=20, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ["nome"]

    def __str__(self):
        return self.nome

    @property
    def idade(self):
        hoje = timezone.now().date()
        b = self.data_nascimento
        return hoje.year - b.year - ((hoje.month, hoje.day) < (b.month, b.day))


class Avaliacao(models.Model):
    token = models.CharField(max_length=64, unique=True, blank=True, null=True)
    
    STATUS_CHOICES = [
        ("em_andamento", "Em andamento"),
        ("concluida", "Concluída"),
    ]
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes")
    data = models.DateField("Data da avaliação", default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual = models.IntegerField(default=1)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    pont_auditiva = models.IntegerField(null=True, blank=True)
    pont_visual = models.IntegerField(null=True, blank=True)
    pont_tato = models.IntegerField(null=True, blank=True)
    pont_movimento = models.IntegerField(null=True, blank=True)
    pont_posicao = models.IntegerField(null=True, blank=True)
    pont_oral = models.IntegerField(null=True, blank=True)
    pont_conduta = models.IntegerField(null=True, blank=True)
    pont_socioemocional = models.IntegerField(null=True, blank=True)
    pont_atencao = models.IntegerField(null=True, blank=True)

    pont_ex = models.IntegerField(null=True, blank=True)
    pont_ev = models.IntegerField(null=True, blank=True)
    pont_sn = models.IntegerField(null=True, blank=True)
    pont_ob = models.IntegerField(null=True, blank=True)

    observacoes = models.TextField("Observações clínicas", blank=True, default="")
    email_enviado_em = models.DateTimeField("E-mail enviado em", null=True, blank=True)

    class Meta:
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
        ordering = ["-data"]

    def __str__(self):
        return f"Avaliação de {self.paciente.nome} - {self.data}"


class Resposta(models.Model):
    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField("Número do item")
    valor = models.IntegerField("Pontuação (0-5)")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]

    def __str__(self):
        return f"Item {self.numero_item}: {self.valor}"


class AvaliacaoVineland(models.Model):
    RESPOSTA_CHOICES = [
        ("sim_sempre", "Sim, sempre"),
        ("sim_as_vezes", "Sim, às vezes"),
        ("nao_nunca", "Não, nunca"),
        ("nao_oportunidade", "Não teve oportunidade"),
        ("nao_sei", "Não sei"),
    ]
    STATUS_CHOICES = [
        ("em_andamento", "Em andamento"),
        ("concluida", "Concluída"),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_vineland")
    token = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data = models.DateField("Data da avaliação", default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual = models.IntegerField(default=1)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    # Pontuação total e por categoria
    pont_total = models.FloatField(null=True, blank=True)
    pont_comunicacao = models.FloatField(null=True, blank=True)
    pont_locomocao = models.FloatField(null=True, blank=True)
    pont_ocupacao = models.FloatField(null=True, blank=True)
    pont_socializacao = models.FloatField(null=True, blank=True)
    pont_autogoverno = models.FloatField(null=True, blank=True)
    pont_age = models.FloatField(null=True, blank=True)
    pont_ac = models.FloatField(null=True, blank=True)
    pont_av = models.FloatField(null=True, blank=True)

    # Idade Social (IS) em meses — inserida manualmente pelo profissional
    idade_social_meses = models.IntegerField("Idade Social (meses)", null=True, blank=True)
    quociente_social = models.FloatField("Quociente Social (QS)", null=True, blank=True)

    observacoes = models.TextField("Observações clínicas", blank=True, default="")
    email_enviado_em = models.DateTimeField("E-mail enviado em", null=True, blank=True)

    class Meta:
        verbose_name = "Avaliação Vineland"
        verbose_name_plural = "Avaliações Vineland"
        ordering = ["-data"]

    def __str__(self):
        return f"Vineland — {self.paciente.nome} — {self.data}"


class RespostaVineland(models.Model):
    RESPOSTA_CHOICES = [
        ("sim_sempre", "Sim, sempre"),
        ("sim_as_vezes", "Sim, às vezes"),
        ("nao_nunca", "Não, nunca"),
        ("nao_oportunidade", "Não teve oportunidade"),
        ("nao_sei", "Não sei"),
    ]

    avaliacao = models.ForeignKey(AvaliacaoVineland, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField("Número do item")
    resposta = models.CharField(max_length=20, choices=RESPOSTA_CHOICES)

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]

    def __str__(self):
        return f"Item {self.numero_item}: {self.resposta}"


# ── Questionário Sensorial Escolar ────────────────────────────────────────────

class AvaliacaoEscolar(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_escolar")
    token = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data = models.DateField("Data da avaliação", default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual = models.IntegerField(default=1)
    pont_auditivo = models.IntegerField(null=True, blank=True)
    pont_visual = models.IntegerField(null=True, blank=True)
    pont_tatil = models.IntegerField(null=True, blank=True)
    pont_vestibular = models.IntegerField(null=True, blank=True)
    pont_social = models.IntegerField(null=True, blank=True)
    observacoes = models.TextField("Observações clínicas", blank=True, default="")
    email_enviado_em = models.DateTimeField("E-mail enviado em", null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Questionário Sensorial Escolar"
        ordering = ["-data"]

    def __str__(self):
        return f"Escolar — {self.paciente.nome} — {self.data}"


class RespostaEscolar(models.Model):
    avaliacao = models.ForeignKey(AvaliacaoEscolar, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor = models.IntegerField()

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── Perfil Sensorial Bebê / Criança Pequena ───────────────────────────────────

class AvaliacaoBebe(models.Model):
    FAIXA_CHOICES = [
        ("bebe", "Bebê (0–6 meses)"),
        ("crianca_pequena", "Criança Pequena (7–36 meses)"),
    ]
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_bebe")
    token = models.CharField(max_length=64, unique=True, blank=True, null=True)
    faixa = models.CharField(max_length=20, choices=FAIXA_CHOICES)
    data = models.DateField("Data da avaliação", default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual = models.IntegerField(default=1)
    pont_busca = models.IntegerField(null=True, blank=True)
    pont_evitamento = models.IntegerField(null=True, blank=True)
    pont_sensibilidade = models.IntegerField(null=True, blank=True)
    pont_registro = models.IntegerField(null=True, blank=True)
    observacoes = models.TextField("Observações clínicas", blank=True, default="")
    email_enviado_em = models.DateTimeField("E-mail enviado em", null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil Sensorial Bebê/Criança Pequena"
        ordering = ["-data"]

    def __str__(self):
        return f"Bebê — {self.paciente.nome} — {self.data}"


class RespostaBebe(models.Model):
    avaliacao = models.ForeignKey(AvaliacaoBebe, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor = models.IntegerField()

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── EDM — Escala de Desenvolvimento Motor ─────────────────────────────────────

class AvaliacaoEDM(models.Model):
    LATERALIDADE_CHOICES = [
        ("definida_direita", "Definida Direita"),
        ("definida_esquerda", "Definida Esquerda"),
        ("cruzada", "Cruzada"),
        ("indefinida", "Indefinida"),
    ]
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_edm")
    data = models.DateField("Data da avaliação", default=timezone.now)
    idade_motricidade_fina = models.IntegerField("Motricidade Fina (meses)", null=True, blank=True)
    idade_motricidade_ampla = models.IntegerField("Motricidade Ampla (meses)", null=True, blank=True)
    idade_equilibrio = models.IntegerField("Equilíbrio (meses)", null=True, blank=True)
    idade_esquema_corporal = models.IntegerField("Esquema Corporal (meses)", null=True, blank=True)
    idade_organizacao_espacial = models.IntegerField("Organização Espacial (meses)", null=True, blank=True)
    idade_organizacao_temporal = models.IntegerField("Organização Temporal (meses)", null=True, blank=True)
    lateralidade = models.CharField("Lateralidade", max_length=20, choices=LATERALIDADE_CHOICES, null=True, blank=True)
    idade_motora_geral = models.FloatField("Idade Motora Geral (meses)", null=True, blank=True)
    quociente_motor = models.FloatField("Quociente Motor (QM)", null=True, blank=True)
    observacoes = models.TextField("Observações clínicas", blank=True, default="")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "EDM — Escala de Desenvolvimento Motor"
        ordering = ["-data"]

    def __str__(self):
        return f"EDM — {self.paciente.nome} — {self.data}"


# ── MABC-2 ───────────────────────────────────────────────────────────────────

class AvaliacaoMABC2(models.Model):
    FAIXA_CHOICES = [
        ("3_6", "3–6 anos"),
        ("7_10", "7–10 anos"),
        ("11_16", "11–16 anos"),
    ]
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_mabc2")
    faixa_etaria = models.CharField("Faixa etária", max_length=10, choices=FAIXA_CHOICES)
    data = models.DateField("Data da avaliação", default=timezone.now)
    md1_raw = models.FloatField("Destreza Manual 1 (bruto)", null=True, blank=True)
    md2_raw = models.FloatField("Destreza Manual 2 (bruto)", null=True, blank=True)
    md3_raw = models.FloatField("Destreza Manual 3 (bruto)", null=True, blank=True)
    ac1_raw = models.FloatField("Arremesso/Recepção 1 (bruto)", null=True, blank=True)
    ac2_raw = models.FloatField("Arremesso/Recepção 2 (bruto)", null=True, blank=True)
    eq1_raw = models.FloatField("Equilíbrio 1 (bruto)", null=True, blank=True)
    eq2_raw = models.FloatField("Equilíbrio 2 (bruto)", null=True, blank=True)
    eq3_raw = models.FloatField("Equilíbrio 3 (bruto)", null=True, blank=True)
    md_escore = models.IntegerField("Escore Destreza Manual", null=True, blank=True)
    ac_escore = models.IntegerField("Escore Arremesso/Recepção", null=True, blank=True)
    eq_escore = models.IntegerField("Escore Equilíbrio", null=True, blank=True)
    escore_total = models.IntegerField("Escore Total", null=True, blank=True)
    percentil = models.IntegerField("Percentil", null=True, blank=True)
    observacoes = models.TextField("Observações clínicas", blank=True, default="")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "MABC-2"
        ordering = ["-data"]

    def __str__(self):
        return f"MABC-2 — {self.paciente.nome} — {self.data}"


# ── Beery VMI ─────────────────────────────────────────────────────────────────

class AvaliacaoBeery(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_beery")
    data = models.DateField("Data da avaliação", default=timezone.now)
    idade_anos = models.IntegerField("Idade (anos)", null=True, blank=True)
    idade_meses = models.IntegerField("Idade (meses complementares)", null=True, blank=True)
    vmi_raw = models.IntegerField("VMI — Escore bruto", null=True, blank=True)
    vp_raw = models.IntegerField("Percepção Visual — Escore bruto", null=True, blank=True)
    mc_raw = models.IntegerField("Coordenação Motora — Escore bruto", null=True, blank=True)
    vmi_escore = models.IntegerField("VMI — Escore padrão", null=True, blank=True)
    vp_escore = models.IntegerField("Percepção Visual — Escore padrão", null=True, blank=True)
    mc_escore = models.IntegerField("Coordenação Motora — Escore padrão", null=True, blank=True)
    vmi_percentil = models.IntegerField("VMI — Percentil", null=True, blank=True)
    vp_percentil = models.IntegerField("Percepção Visual — Percentil", null=True, blank=True)
    mc_percentil = models.IntegerField("Coordenação Motora — Percentil", null=True, blank=True)
    observacoes = models.TextField("Observações clínicas", blank=True, default="")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Beery VMI"
        ordering = ["-data"]

    def __str__(self):
        return f"Beery — {self.paciente.nome} — {self.data}"


# ── PEDI ──────────────────────────────────────────────────────────────────────

class AvaliacaoPEDI(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_pedi")
    data = models.DateField("Data da avaliação", default=timezone.now)
    fs_autocuidado = models.IntegerField("FS — Autocuidado (bruto, 0–73)", null=True, blank=True)
    fs_mobilidade = models.IntegerField("FS — Mobilidade (bruto, 0–59)", null=True, blank=True)
    fs_funcao_social = models.IntegerField("FS — Função Social (bruto, 0–65)", null=True, blank=True)
    ca_autocuidado = models.IntegerField("CA — Autocuidado (0–40)", null=True, blank=True)
    ca_mobilidade = models.IntegerField("CA — Mobilidade (0–40)", null=True, blank=True)
    ca_funcao_social = models.IntegerField("CA — Função Social (0–40)", null=True, blank=True)
    fs_autocuidado_escala = models.FloatField("FS — Autocuidado (escala 0–100)", null=True, blank=True)
    fs_mobilidade_escala = models.FloatField("FS — Mobilidade (escala 0–100)", null=True, blank=True)
    fs_funcao_social_escala = models.FloatField("FS — Função Social (escala 0–100)", null=True, blank=True)
    ca_autocuidado_escala = models.FloatField("CA — Autocuidado (escala 0–100)", null=True, blank=True)
    ca_mobilidade_escala = models.FloatField("CA — Mobilidade (escala 0–100)", null=True, blank=True)
    ca_funcao_social_escala = models.FloatField("CA — Função Social (escala 0–100)", null=True, blank=True)
    observacoes = models.TextField("Observações clínicas", blank=True, default="")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "PEDI"
        ordering = ["-data"]

    def __str__(self):
        return f"PEDI — {self.paciente.nome} — {self.data}"


# ── SPM — Sensory Processing Measure ─────────────────────────────────────────

class AvaliacaoSPM(models.Model):
    FAIXA_CHOICES = [
        ("spm_p",    "SPM-P Casa (2–5 anos)"),
        ("spm_casa", "SPM Casa (5–12 anos)"),
    ]
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    paciente      = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_spm")
    token         = models.CharField(max_length=64, unique=True, blank=True, null=True)
    faixa         = models.CharField(max_length=10, choices=FAIXA_CHOICES)
    data          = models.DateField("Data da avaliação", default=timezone.now)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual  = models.IntegerField(default=1)

    pont_soc = models.IntegerField(null=True, blank=True)
    pont_vis = models.IntegerField(null=True, blank=True)
    pont_hea = models.IntegerField(null=True, blank=True)
    pont_tou = models.IntegerField(null=True, blank=True)
    pont_sme = models.IntegerField(null=True, blank=True)
    pont_bod = models.IntegerField(null=True, blank=True)
    pont_bal = models.IntegerField(null=True, blank=True)
    pont_pla = models.IntegerField(null=True, blank=True)
    pont_tot = models.IntegerField(null=True, blank=True)

    observacoes      = models.TextField("Observações clínicas", blank=True, default="")
    email_enviado_em = models.DateTimeField("E-mail enviado em", null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "SPM"
        ordering = ["-data"]

    def __str__(self):
        return f"SPM — {self.paciente.nome} — {self.data}"


class RespostaSPM(models.Model):
    avaliacao    = models.ForeignKey(AvaliacaoSPM, on_delete=models.CASCADE, related_name="respostas")
    numero_item  = models.IntegerField()
    valor        = models.IntegerField()

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── Link de Convite para Questionário ─────────────────────────────────────────

class LinkConvite(models.Model):
    TIPO_CHOICES = [
        ("sensorial", "Perfil Sensorial"),
        ("vineland", "Escala Vineland"),
        ("escolar", "Questionário Sensorial Escolar"),
        ("bebe", "Bebê (0–6 meses)"),
        ("crianca_pequena", "Criança Pequena (7–36 meses)"),
        ("spm_p",    "SPM-P Casa (2–5 anos)"),
        ("spm_casa", "SPM Casa (5–12 anos)"),
        ("edm", "EDM Figueiredo"),
        ("mabc2", "MABC-2"),
        ("beery", "Beery VMI"),
        ("pedi", "PEDI"),
    ]
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    medico = models.ForeignKey(User, on_delete=models.CASCADE, related_name="links_convite")
    criado_em = models.DateTimeField(auto_now_add=True)
    usado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Link de Convite"
        verbose_name_plural = "Links de Convite"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.medico.username} — {self.criado_em.date()}"
