import uuid
import re
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


def _parse_dispositivo(user_agent: str) -> str:
    """Extrai sistema operacional e navegador do User-Agent."""
    ua = user_agent or ""

    if "iPhone" in ua:
        os = "iPhone"
    elif "iPad" in ua:
        os = "iPad"
    elif "Android" in ua:
        os = "Android"
    elif "Windows NT" in ua:
        os = "Windows"
    elif "Macintosh" in ua or "Mac OS X" in ua:
        os = "Mac"
    elif "Linux" in ua:
        os = "Linux"
    else:
        os = "Desconhecido"

    if "Edg/" in ua or "EdgA/" in ua:
        browser = "Edge"
    elif "OPR/" in ua or "Opera" in ua:
        browser = "Opera"
    elif "Chrome/" in ua:
        browser = "Chrome"
    elif "Firefox/" in ua:
        browser = "Firefox"
    elif "Safari/" in ua:
        browser = "Safari"
    else:
        browser = "Outro"

    return f"{browser} / {os}"


class ModuloAvaliacao(models.Model):
    MODULO_CHOICES = [
        # ── Terapia Ocupacional ──────────────────────────────────────────
        ("sensorial",              "Perfil Sensorial"),
        ("vineland",               "Escala Vineland"),
        ("escolar",                "Questionário Sensorial Escolar"),
        ("bebe",                   "Perfil Sensorial Bebê/Criança Pequena"),
        ("spm",                    "SPM — Sensory Processing Measure"),
        ("edm",                    "EDM Figueiredo"),
        ("mabc2",                  "MABC-2"),
        ("beery",                  "Beery VMI"),
        ("pedi",                   "PEDI"),
        ("vineland3",              "Vineland-3"),
        ("portage",                "Guia Portage"),
        # ── Psicologia ───────────────────────────────────────────────────
        ("sdq",                    "SDQ — Capacidades e Dificuldades"),
        ("snap_iv",                "SNAP-IV — Avaliação de TDAH/TOD"),
        ("mchat",                  "M-CHAT-R — Rastreio de Autismo"),
        ("cars",                   "CARS-2 — Escala de Autismo em Crianças"),
        # ── Fonoaudiologia ───────────────────────────────────────────────
        ("linguagem",              "Avaliação de Linguagem"),
        ("alimentacao_seletiva",   "Triagem de Alimentação Seletiva"),
        ("habitos_orais",          "Hábitos Orais Deletérios"),
        ("voz_infantil",           "Triagem de Voz Infantil (pVHI)"),
        ("processamento_auditivo", "Triagem de Processamento Auditivo"),
        ("idv10",                  "IDV-10 — Índice de Desvantagem Vocal"),
        # ── Pediatria / Neuropediatria ───────────────────────────────────
        ("desenvolvimento",        "Marcos de Desenvolvimento Infantil"),
        ("sono_infantil",          "Avaliação de Sono Infantil"),
        # ── ABA / Análise do Comportamento ───────────────────────────────
        ("habilidades_adaptativas", "Habilidades Adaptativas (ABA)"),
        ("comportamento_funcional", "Comportamento Funcional (ABA)"),
        # ── Neuropsicologia ──────────────────────────────────────────────
        ("rastreio_cognitivo",     "Rastreio Cognitivo"),
        # ── Psicopedagogia ───────────────────────────────────────────────
        ("psicopedagogica",        "Avaliação Psicopedagógica"),
    ]
    codigo = models.CharField("Código", max_length=30, unique=True, choices=MODULO_CHOICES)
    nome = models.CharField("Nome", max_length=100)
    descricao = models.CharField("Descrição", max_length=200, blank=True)

    class Meta:
        verbose_name = "Módulo de Avaliação"
        verbose_name_plural = "Módulos de Avaliação"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


# Mapeamento especialidade → módulos padrão sugeridos (usados no admin)
ESPECIALIDADE_CHOICES = [
    ("terapeuta_ocupacional", "Terapia Ocupacional"),
    ("psicologo",             "Psicologia"),
    ("fonoaudiologo",         "Fonoaudiologia"),
    ("neuropsicoplogo",       "Neuropsicologia"),
    ("psicopedagogo",         "Psicopedagogia"),
    ("pediatra",              "Pediatria"),
    ("neuropediatra",         "Neuropediatria"),
    ("analista_aba",          "ABA / Análise do Comportamento"),
]

MODULOS_POR_ESPECIALIDADE = {
    "terapeuta_ocupacional": [
        "sensorial", "vineland", "escolar", "bebe", "spm",
        "edm", "mabc2", "beery", "pedi", "vineland3", "portage",
    ],
    "psicologo": [
        "sdq", "snap_iv", "mchat", "cars",
    ],
    "fonoaudiologo": [
        "linguagem", "alimentacao_seletiva",
        "habitos_orais", "voz_infantil", "processamento_auditivo", "idv10",
    ],
    "neuropsicoplogo": [
        "rastreio_cognitivo", "sdq", "snap_iv", "mchat", "cars",
    ],
    "psicopedagogo": [
        "psicopedagogica", "sdq", "snap_iv",
    ],
    "pediatra": [
        "desenvolvimento", "sono_infantil", "mchat", "snap_iv",
    ],
    "neuropediatra": [
        "desenvolvimento", "sono_infantil", "mchat", "cars",
        "snap_iv", "rastreio_cognitivo", "sensorial",
    ],
    "analista_aba": [
        "habilidades_adaptativas", "comportamento_funcional",
        "mchat", "vineland3",
    ],
}


class Especialidade(models.Model):
    """Especialidade profissional — usada para filtrar módulos no admin."""
    codigo = models.CharField("Código", max_length=30, unique=True, choices=ESPECIALIDADE_CHOICES)
    nome   = models.CharField("Nome",   max_length=100)

    class Meta:
        verbose_name        = "Especialidade"
        verbose_name_plural = "Especialidades"
        ordering            = ["nome"]

    def __str__(self):
        return self.nome


class PerfilMedico(models.Model):
    PLANO_CHOICES = [
        ("trial", "Grátis 7 dias"),
        ("start", "START"),
        ("plus", "PLUS"),
        ("elite", "ELITE"),
    ]

    # Módulos incluídos automaticamente no trial (mesmos do START)
    MODULOS_TRIAL = ["sensorial", "bebe", "escolar", "spm"]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    registro_profissional = models.CharField("Registro Profissional", max_length=30, blank=True)
    especialidades = models.ManyToManyField(
        "Especialidade",
        blank=True,
        verbose_name="Especialidades",
        related_name="profissionais",
    )
    telefone = models.CharField("Telefone", max_length=20, blank=True)
    plano = models.CharField(
        "Plano", max_length=10, choices=PLANO_CHOICES, default="trial"
    )
    trial_inicio    = models.DateTimeField("Início do trial", null=True, blank=True)
    plano_expiracao = models.DateTimeField("Expiração do plano", null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    modulos_liberados = models.ManyToManyField(
        ModuloAvaliacao,
        blank=True,
        verbose_name="Módulos liberados",
        related_name="medicos",
    )
    session_key = models.CharField(
        "Chave de sessão ativa", max_length=40, blank=True, default=""
    )

    class Meta:
        verbose_name = "Perfil do Profissional"
        verbose_name_plural = "Perfis dos Profissionais"

    def __str__(self):
        return f"Dr(a). {self.user.get_full_name() or self.user.username}"

    @property
    def trial_ativo(self):
        if self.plano != "trial" or self.trial_inicio is None:
            return False
        return (timezone.now() - self.trial_inicio).days < 7

    @property
    def trial_dias_restantes(self):
        if self.plano != "trial" or self.trial_inicio is None:
            return 0
        restantes = 7 - (timezone.now() - self.trial_inicio).days
        return max(restantes, 0)

    @property
    def plano_ativo(self):
        """True quando o plano pago (start/plus/elite) ainda está dentro da vigência."""
        if self.plano == "trial":
            return self.trial_ativo
        if self.plano_expiracao is None:
            return True   # sem data = aprovado manualmente sem vencimento
        return timezone.now() < self.plano_expiracao

    @property
    def plano_dias_restantes(self):
        """Dias restantes do plano pago. Retorna None se não houver data de expiração."""
        if self.plano == "trial":
            return self.trial_dias_restantes
        if self.plano_expiracao is None:
            return None
        delta = self.plano_expiracao - timezone.now()
        return max(delta.days, 0)

    def tem_acesso(self, codigo_modulo):
        if self.plano == "trial" and not self.trial_ativo:
            return False
        if self.plano != "trial" and not self.plano_ativo:
            return False
        return self.modulos_liberados.filter(codigo=codigo_modulo).exists()


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
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
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

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
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
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
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
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
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
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
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
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
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
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
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
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
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
    token          = models.CharField(max_length=64, unique=True, blank=True, null=True)
    respostas_json = models.TextField(blank=True, default='{}')
    pagina_atual   = models.IntegerField(default=0)
    observacoes    = models.TextField("Observações clínicas", blank=True, default="")
    criado_em      = models.DateTimeField(auto_now_add=True)

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

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
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


# ── Vineland-3 — Formulário de Pais/Cuidadores dos Níveis de Domínio ─────────

class AvaliacaoVineland3(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente      = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_vineland3")
    token         = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data          = models.DateField("Data da avaliação", default=timezone.now)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual  = models.IntegerField(default=1)

    # Domínios adaptativos (pontuação bruta)
    pont_com   = models.IntegerField("COM — Comunicação", null=True, blank=True)
    pont_avd   = models.IntegerField("AVD — Atividade de Vida Diária", null=True, blank=True)
    pont_soc   = models.IntegerField("SOC — Habilidades Sociais", null=True, blank=True)
    pont_hmot  = models.IntegerField("HMOT — Atividade Física", null=True, blank=True)
    pont_total = models.IntegerField("Composto Adaptativo", null=True, blank=True)

    # Problemas de Comportamento
    pont_pc_a  = models.IntegerField("PC — Seção A", null=True, blank=True)
    pont_pc_b  = models.IntegerField("PC — Seção B", null=True, blank=True)
    pont_pc_c  = models.IntegerField("PC — Seção C", null=True, blank=True)

    observacoes      = models.TextField("Observações clínicas", blank=True, default="")
    email_enviado_em = models.DateTimeField("E-mail enviado em", null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vineland-3"
        ordering = ["-data"]

    def __str__(self):
        return f"Vineland-3 — {self.paciente.nome} — {self.data}"


class RespostaVineland3(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoVineland3, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── Link de Convite para Questionário ─────────────────────────────────────────

class LinkConvite(models.Model):
    TIPO_CHOICES = [
        # ── Terapia Ocupacional ──────────────────────────────────────────
        ("sensorial",               "Perfil Sensorial"),
        ("vineland",                "Escala Vineland"),
        ("escolar",                 "Questionário Sensorial Escolar"),
        ("bebe",                    "Bebê (0–6 meses)"),
        ("crianca_pequena",         "Criança Pequena (7–36 meses)"),
        ("spm_p",                   "SPM-P Casa (2–5 anos)"),
        ("spm_casa",                "SPM Casa (5–12 anos)"),
        ("edm",                     "EDM Figueiredo"),
        ("mabc2",                   "MABC-2"),
        ("beery",                   "Beery VMI"),
        ("pedi",                    "PEDI"),
        ("vineland3",               "Vineland-3"),
        ("portage",                 "Guia Portage"),
        # ── Psicologia ───────────────────────────────────────────────────
        ("sdq",                     "SDQ — Capacidades e Dificuldades"),
        ("snap_iv",                 "SNAP-IV — Avaliação de TDAH/TOD"),
        ("mchat",                   "M-CHAT-R — Rastreio de Autismo"),
        ("cars",                    "CARS-2 — Escala de Autismo em Crianças"),
        # ── Fonoaudiologia ───────────────────────────────────────────────
        ("linguagem",               "Avaliação de Linguagem"),
        ("alimentacao_seletiva",    "Triagem de Alimentação Seletiva"),
        ("habitos_orais",           "Hábitos Orais Deletérios"),
        ("voz_infantil",            "Triagem de Voz Infantil (pVHI)"),
        ("processamento_auditivo",  "Triagem de Processamento Auditivo"),
        ("idv10",                   "IDV-10 — Índice de Desvantagem Vocal"),
        # ── Pediatria / Neuropediatria ───────────────────────────────────
        ("desenvolvimento",         "Marcos de Desenvolvimento Infantil"),
        ("sono_infantil",           "Avaliação de Sono Infantil"),
        # ── ABA / Análise do Comportamento ───────────────────────────────
        ("habilidades_adaptativas", "Habilidades Adaptativas (ABA)"),
        ("comportamento_funcional", "Comportamento Funcional (ABA)"),
        # ── Neuropsicologia ──────────────────────────────────────────────
        ("rastreio_cognitivo",      "Rastreio Cognitivo"),
        # ── Psicopedagogia ───────────────────────────────────────────────
        ("psicopedagogica",         "Avaliação Psicopedagógica"),
    ]
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    medico = models.ForeignKey(User, on_delete=models.CASCADE, related_name="links_convite")
    criado_em = models.DateTimeField(auto_now_add=True)
    usado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Link de Convite"
        verbose_name_plural = "Links de Convite"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.medico.username} — {self.criado_em.date()}"


# ── Guia Portage de Avaliação Pré-Escolar ────────────────────────────────────

class AvaliacaoPortage(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente      = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_portage")
    token         = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data          = models.DateField("Data da avaliação", default=timezone.now)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual  = models.IntegerField(default=1)

    pont_soc  = models.IntegerField("Socialização — SIM", null=True, blank=True)
    pont_cog  = models.IntegerField("Cognição — SIM", null=True, blank=True)
    pont_lin  = models.IntegerField("Linguagem — SIM", null=True, blank=True)
    pont_ac   = models.IntegerField("Auto-Cuidados — SIM", null=True, blank=True)
    pont_mot  = models.IntegerField("Motor — SIM", null=True, blank=True)

    observacoes      = models.TextField("Observações clínicas", blank=True, default="")
    email_enviado_em = models.DateTimeField("E-mail enviado em", null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Guia Portage"
        ordering = ["-data"]

    def __str__(self):
        return f"Portage — {self.paciente.nome} — {self.data}"


class RespostaPortage(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoPortage, on_delete=models.CASCADE, related_name="respostas")
    dominio     = models.CharField(max_length=20)
    numero_item = models.IntegerField()
    valor       = models.IntegerField()   # 2=SIM, 1=SIM COM MEDIAÇÃO, 0=AINDA NÃO

    class Meta:
        unique_together = ("avaliacao", "dominio", "numero_item")
        ordering = ["dominio", "numero_item"]


# ═══════════════════════════════════════════════════════════════════════════════
#  PSICOLOGIA
# ═══════════════════════════════════════════════════════════════════════════════

# ── SDQ — Questionário de Capacidades e Dificuldades ─────────────────────────

class AvaliacaoSDQ(models.Model):
    """SDQ — Strengths and Difficulties Questionnaire (Goodman, 1997).
    25 itens, 5 subescalas de 5 itens. Escala: 0=Não é verdade / 1=Um pouco
    verdade / 2=Muito verdade. Respondentes: pais, professores ou auto-relato.
    """
    RESPONDENTE_CHOICES = [
        ("pais",      "Pais / Cuidadores"),
        ("professor", "Professor"),
        ("auto",      "Auto-relato (≥11 anos)"),
    ]
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente                  = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_sdq")
    token                     = models.CharField(max_length=64, unique=True, blank=True, null=True)
    respondente               = models.CharField(max_length=10, choices=RESPONDENTE_CHOICES, default="pais")
    data                      = models.DateField(default=timezone.now)
    status                    = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual              = models.IntegerField(default=1)

    # Subescalas (soma bruta 0–10 cada)
    pont_emocional            = models.IntegerField("Sintomas Emocionais (0–10)",      null=True, blank=True)
    pont_conduta              = models.IntegerField("Problemas de Conduta (0–10)",     null=True, blank=True)
    pont_hiperatividade       = models.IntegerField("Hiperatividade (0–10)",           null=True, blank=True)
    pont_pares                = models.IntegerField("Problemas com Pares (0–10)",      null=True, blank=True)
    pont_prossocial           = models.IntegerField("Comportamento Prossocial (0–10)", null=True, blank=True)
    pont_total_dificuldades   = models.IntegerField("Total de Dificuldades (0–40)",    null=True, blank=True)

    observacoes               = models.TextField(blank=True, default="")
    email_enviado_em          = models.DateTimeField(null=True, blank=True)
    criado_em                 = models.DateTimeField(auto_now_add=True)
    atualizado_em             = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "SDQ — Capacidades e Dificuldades"
        ordering = ["-data"]

    def __str__(self):
        return f"SDQ — {self.paciente.nome} — {self.data}"


class RespostaSDQ(models.Model):
    avaliacao    = models.ForeignKey(AvaliacaoSDQ, on_delete=models.CASCADE, related_name="respostas")
    numero_item  = models.IntegerField()
    valor        = models.IntegerField()  # 0 / 1 / 2
    observacao   = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── SNAP-IV — Avaliação de TDAH e TOD ────────────────────────────────────────

class AvaliacaoSNAPIV(models.Model):
    """SNAP-IV — Swanson, Nolan and Pelham Rating Scale (Swanson, 1992).
    26 itens; escala 0–3 (Nunca/Pouco/Muito/Demais).
    Itens 1–9: Desatenção | 10–18: Hiperact./Impuls. | 19–26: TOD.
    Ponto de corte: média ≥ 1,5 por subescala é clinicamente significativa.
    """
    RESPONDENTE_CHOICES = [
        ("pais",      "Pais / Cuidadores"),
        ("professor", "Professor"),
    ]
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente                     = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_snap_iv")
    token                        = models.CharField(max_length=64, unique=True, blank=True, null=True)
    respondente                  = models.CharField(max_length=10, choices=RESPONDENTE_CHOICES, default="pais")
    data                         = models.DateField(default=timezone.now)
    status                       = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual                 = models.IntegerField(default=1)

    # Médias por subescala (total da subescala / nº de itens)
    media_desatencao             = models.FloatField("Média Desatenção (itens 1–9)",                null=True, blank=True)
    media_hiperatividade         = models.FloatField("Média Hiperatividade/Impulsividade (10–18)",  null=True, blank=True)
    media_tod                    = models.FloatField("Média TOD (itens 19–26)",                     null=True, blank=True)

    observacoes                  = models.TextField(blank=True, default="")
    email_enviado_em             = models.DateTimeField(null=True, blank=True)
    criado_em                    = models.DateTimeField(auto_now_add=True)
    atualizado_em                = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "SNAP-IV"
        ordering = ["-data"]

    def __str__(self):
        return f"SNAP-IV — {self.paciente.nome} — {self.data}"


class RespostaSNAPIV(models.Model):
    avaliacao    = models.ForeignKey(AvaliacaoSNAPIV, on_delete=models.CASCADE, related_name="respostas")
    numero_item  = models.IntegerField()
    valor        = models.IntegerField()  # 0–3
    observacao   = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── M-CHAT-R — Rastreio de Autismo (16–30 meses) ─────────────────────────────

class AvaliacaoMCHAT(models.Model):
    """M-CHAT-R — Modified Checklist for Autism in Toddlers, Revised (2013).
    20 itens Sim/Não; faixa etária: 16–30 meses.
    Risco: 0–2 baixo | 3–7 médio (requer follow-up) | 8–20 alto.
    """
    CLASSIFICACAO_CHOICES = [
        ("baixo", "Baixo risco (0–2)"),
        ("medio", "Médio risco — indicado M-CHAT-R/F (3–7)"),
        ("alto",  "Alto risco — encaminhar para avaliação (8–20)"),
    ]
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_mchat")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)

    score_total      = models.IntegerField("Score total (0–20)", null=True, blank=True)
    classificacao    = models.CharField(max_length=10, choices=CLASSIFICACAO_CHOICES, blank=True)

    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "M-CHAT-R — Rastreio de Autismo"
        ordering = ["-data"]

    def __str__(self):
        return f"M-CHAT-R — {self.paciente.nome} — {self.data}"


class RespostaMCHAT(models.Model):
    avaliacao    = models.ForeignKey(AvaliacaoMCHAT, on_delete=models.CASCADE, related_name="respostas")
    numero_item  = models.IntegerField()
    valor        = models.BooleanField()  # True=Sim / False=Não

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── CARS-2 — Escala de Classificação de Autismo em Crianças ──────────────────

class AvaliacaoCARS(models.Model):
    """CARS-2 — Childhood Autism Rating Scale, 2ª edição (Schopler, 2010).
    15 itens; escala 1–4 (com meios pontos: 1/1.5/2/2.5/3/3.5/4).
    Score: <30 sem autismo | 30–36,5 leve-moderado | ≥37 grave.
    """
    CLASSIFICACAO_CHOICES = [
        ("sem_autismo",   "Sem Autismo (<30)"),
        ("leve_moderado", "Autismo Leve-Moderado (30–36,5)"),
        ("grave",         "Autismo Grave (≥37)"),
    ]
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_cars")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)

    score_total      = models.FloatField("Score total (15–60)", null=True, blank=True)
    classificacao    = models.CharField(max_length=20, choices=CLASSIFICACAO_CHOICES, blank=True)

    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "CARS-2 — Escala de Autismo"
        ordering = ["-data"]

    def __str__(self):
        return f"CARS-2 — {self.paciente.nome} — {self.data}"


class RespostaCARS(models.Model):
    avaliacao    = models.ForeignKey(AvaliacaoCARS, on_delete=models.CASCADE, related_name="respostas")
    numero_item  = models.IntegerField()
    valor        = models.FloatField()  # 1 / 1.5 / 2 / 2.5 / 3 / 3.5 / 4

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ═══════════════════════════════════════════════════════════════════════════════
#  FONOAUDIOLOGIA
# ═══════════════════════════════════════════════════════════════════════════════

# ── Avaliação de Linguagem ────────────────────────────────────────────────────

class AvaliacaoLinguagem(models.Model):
    """Checklist clínico de avaliação de linguagem — Fonoaudiologia.
    Áreas: Recepção/Compreensão, Expressão Oral, Pragmática,
    Fonologia/Articulação, Fluência, Consciência Fonológica.
    Escala por item: 0=Nunca / 1=Às vezes / 2=Frequentemente / 3=Sempre.
    """
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_linguagem")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)

    pont_recepcao        = models.IntegerField("Recepção/Compreensão",   null=True, blank=True)
    pont_expressao       = models.IntegerField("Expressão Oral",         null=True, blank=True)
    pont_pragmatica      = models.IntegerField("Pragmática",             null=True, blank=True)
    pont_fonologia       = models.IntegerField("Fonologia/Articulação",  null=True, blank=True)
    pont_fluencia        = models.IntegerField("Fluência",               null=True, blank=True)
    pont_consciencia_fono = models.IntegerField("Consciência Fonológica", null=True, blank=True)

    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Avaliação de Linguagem"
        ordering = ["-data"]

    def __str__(self):
        return f"Linguagem — {self.paciente.nome} — {self.data}"


class RespostaLinguagem(models.Model):
    avaliacao    = models.ForeignKey(AvaliacaoLinguagem, on_delete=models.CASCADE, related_name="respostas")
    dominio      = models.CharField(max_length=30)
    numero_item  = models.IntegerField()
    valor        = models.IntegerField()  # 0=ausente / 1=emergente / 2=presente
    observacao   = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "dominio", "numero_item")
        ordering = ["dominio", "numero_item"]


# ── Triagem de Alimentação Seletiva ───────────────────────────────────────────

class AvaliacaoAlimentacao(models.Model):
    """Triagem de seletividade alimentar e disfagia / processamento oral-motor.
    Usada por Fonoaudiólogos e Pediatras.
    Áreas: Variedade Alimentar, Sensibilidade Sensorial, Rituais/Recusa,
    Motricidade Oral, Deglutição.
    """
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente              = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_alimentacao")
    token                 = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data                  = models.DateField(default=timezone.now)
    status                = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual          = models.IntegerField(default=1)

    pont_variedade        = models.IntegerField("Variedade Alimentar",     null=True, blank=True)
    pont_sensibilidade    = models.IntegerField("Tolerância Sensorial",    null=True, blank=True)
    pont_recusa_rituais   = models.IntegerField("Comportamento Refeições", null=True, blank=True)
    pont_interesse        = models.IntegerField("Interesse e Apetite",     null=True, blank=True)
    pont_motricidade_oral = models.IntegerField("Motricidade Orofacial",   null=True, blank=True)
    pont_degluticao       = models.IntegerField("Deglutição e Segurança",  null=True, blank=True)

    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Triagem de Alimentação Seletiva"
        ordering = ["-data"]

    def __str__(self):
        return f"Alimentação — {self.paciente.nome} — {self.data}"


class RespostaAlimentacao(models.Model):
    avaliacao    = models.ForeignKey(AvaliacaoAlimentacao, on_delete=models.CASCADE, related_name="respostas")
    dominio      = models.CharField(max_length=30)
    numero_item  = models.IntegerField()
    valor        = models.IntegerField()
    observacao   = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "dominio", "numero_item")
        ordering = ["dominio", "numero_item"]


# ── Hábitos Orais Deletérios ─────────────────────────────────────────────────

class AvaliacaoHabitosOrais(models.Model):
    """Triagem de hábitos orais deletérios — Fonoaudiologia.
    Áreas: Respiração Nasal, Sucção Não-Nutritiva, Mastigação,
    Padrão de Deglutição, Postura e Bruxismo.
    Escala: 0=Nunca / 1=Às vezes / 2=Frequentemente / 3=Sempre.
    """
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_habitos_orais")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_respiracao  = models.IntegerField("Respiração Nasal",     null=True, blank=True)
    pont_succao      = models.IntegerField("Sucção Não-Nutritiva", null=True, blank=True)
    pont_mastigacao  = models.IntegerField("Mastigação",           null=True, blank=True)
    pont_degluticao  = models.IntegerField("Padrão de Deglutição", null=True, blank=True)
    pont_postura     = models.IntegerField("Postura e Bruxismo",   null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Triagem de Hábitos Orais"
        ordering = ["-data"]

    def __str__(self):
        return f"Hábitos Orais — {self.paciente.nome} — {self.data}"


class RespostaHabitosOrais(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoHabitosOrais, on_delete=models.CASCADE, related_name="respostas")
    dominio     = models.CharField(max_length=30)
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "dominio", "numero_item")
        ordering = ["dominio", "numero_item"]


# ── Triagem de Voz Infantil (pVHI) ───────────────────────────────────────────

class AvaliacaoVozInfantil(models.Model):
    """Triagem de voz infantil — pVHI adaptado — Fonoaudiologia.
    Áreas: Funcional, Físico, Emocional.
    Escala: 0=Nunca / 1=Às vezes / 2=Frequentemente / 3=Sempre.
    """
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_voz_infantil")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_funcional   = models.IntegerField("Funcional",  null=True, blank=True)
    pont_fisico      = models.IntegerField("Físico",     null=True, blank=True)
    pont_emocional   = models.IntegerField("Emocional",  null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Triagem de Voz Infantil"
        ordering = ["-data"]

    def __str__(self):
        return f"Voz Infantil — {self.paciente.nome} — {self.data}"


class RespostaVozInfantil(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoVozInfantil, on_delete=models.CASCADE, related_name="respostas")
    dominio     = models.CharField(max_length=30)
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "dominio", "numero_item")
        ordering = ["dominio", "numero_item"]


# ── Triagem de Processamento Auditivo ────────────────────────────────────────

class AvaliacaoProcessamentoAuditivo(models.Model):
    """Triagem comportamental de processamento auditivo central — Fonoaudiologia.
    Áreas: Atenção/Discriminação, Compreensão, Memória, Figura-Fundo, Impacto.
    Escala: 0=Nunca / 1=Às vezes / 2=Frequentemente / 3=Sempre.
    """
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente           = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_processamento_auditivo")
    token              = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data               = models.DateField(default=timezone.now)
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual       = models.IntegerField(default=1)
    pont_atencao       = models.IntegerField("Atenção e Discriminação", null=True, blank=True)
    pont_compreensao   = models.IntegerField("Compreensão Auditiva",    null=True, blank=True)
    pont_memoria       = models.IntegerField("Memória Auditiva",        null=True, blank=True)
    pont_figura_fundo  = models.IntegerField("Figura-Fundo",            null=True, blank=True)
    pont_impacto       = models.IntegerField("Impacto Funcional",       null=True, blank=True)
    observacoes        = models.TextField(blank=True, default="")
    email_enviado_em   = models.DateTimeField(null=True, blank=True)
    criado_em          = models.DateTimeField(auto_now_add=True)
    atualizado_em      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Triagem de Processamento Auditivo"
        ordering = ["-data"]

    def __str__(self):
        return f"Processamento Auditivo — {self.paciente.nome} — {self.data}"


class RespostaProcessamentoAuditivo(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoProcessamentoAuditivo, on_delete=models.CASCADE, related_name="respostas")
    dominio     = models.CharField(max_length=30)
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "dominio", "numero_item")
        ordering = ["dominio", "numero_item"]


# ── IDV-10 (Índice de Desvantagem Vocal) ─────────────────────────────────────

class AvaliacaoIDV10(models.Model):
    """IDV-10 — Índice de Desvantagem Vocal (VHI-10 adaptado) — Fonoaudiologia.
    Para adolescentes e adultos, auto-relato ou respondido pelo responsável.
    Áreas: Impacto Comunicativo, Aspectos Físicos.
    Escala: 0=Nunca / 1=Às vezes / 2=Frequentemente / 3=Sempre.
    """
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_idv10")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_comunicativo = models.IntegerField("Impacto Comunicativo", null=True, blank=True)
    pont_fisico       = models.IntegerField("Aspectos Físicos",     null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "IDV-10"
        ordering = ["-data"]

    def __str__(self):
        return f"IDV-10 — {self.paciente.nome} — {self.data}"


class RespostaIDV10(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoIDV10, on_delete=models.CASCADE, related_name="respostas")
    dominio     = models.CharField(max_length=30)
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "dominio", "numero_item")
        ordering = ["dominio", "numero_item"]


# ═══════════════════════════════════════════════════════════════════════════════
#  PEDIATRIA / NEUROPEDIATRIA
# ═══════════════════════════════════════════════════════════════════════════════

# ── Marcos de Desenvolvimento Infantil ───────────────────────────────────────

class AvaliacaoDesenvolvimento(models.Model):
    """Checklist de marcos do desenvolvimento infantil.
    Aplicado por Pediatras e Neuropediatras.
    Áreas: Motor Grosso, Motor Fino, Linguagem, Social/Emocional, Cognitivo.
    Escala: 0=Não atingido / 1=Em aquisição / 2=Atingido.
    """
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente           = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_desenvolvimento")
    token              = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data               = models.DateField(default=timezone.now)
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual       = models.IntegerField(default=1)

    pont_motor_grosso  = models.IntegerField("Motor Grosso",      null=True, blank=True)
    pont_motor_fino    = models.IntegerField("Motor Fino",        null=True, blank=True)
    pont_linguagem     = models.IntegerField("Linguagem",         null=True, blank=True)
    pont_social        = models.IntegerField("Social/Emocional",  null=True, blank=True)
    pont_cognitivo     = models.IntegerField("Cognitivo",         null=True, blank=True)

    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Marcos de Desenvolvimento Infantil"
        ordering = ["-data"]

    def __str__(self):
        return f"Desenvolvimento — {self.paciente.nome} — {self.data}"


class RespostaDesenvolvimento(models.Model):
    avaliacao    = models.ForeignKey(AvaliacaoDesenvolvimento, on_delete=models.CASCADE, related_name="respostas")
    dominio      = models.CharField(max_length=30)
    numero_item  = models.IntegerField()
    valor        = models.IntegerField()  # 0=Não atingido / 1=Em aquisição / 2=Atingido
    observacao   = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "dominio", "numero_item")
        ordering = ["dominio", "numero_item"]


# ── Avaliação de Sono Infantil ────────────────────────────────────────────────

class AvaliacaoSono(models.Model):
    """Triagem de distúrbios do sono infantil.
    Baseada em BEARS / CSHQ (adaptação clínica).
    Subescalas: Início do Sono, Manutenção, Sonolência Diurna,
    Resistência, Ansiedade do Sono, Ronco/Apneia.
    """
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente          = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_sono")
    token             = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data              = models.DateField(default=timezone.now)
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual      = models.IntegerField(default=1)

    pont_inicio       = models.IntegerField("Início do sono",      null=True, blank=True)
    pont_manutencao   = models.IntegerField("Manutenção do sono",  null=True, blank=True)
    pont_sonolencia   = models.IntegerField("Sonolência diurna",   null=True, blank=True)
    pont_resistencia  = models.IntegerField("Resistência ao sono", null=True, blank=True)
    pont_ansiedade    = models.IntegerField("Ansiedade do sono",   null=True, blank=True)
    pont_ronco_apneia = models.IntegerField("Ronco/Apneia",        null=True, blank=True)
    pont_total        = models.IntegerField("Score total",         null=True, blank=True)

    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Avaliação de Sono Infantil"
        ordering = ["-data"]

    def __str__(self):
        return f"Sono — {self.paciente.nome} — {self.data}"


class RespostaSono(models.Model):
    avaliacao    = models.ForeignKey(AvaliacaoSono, on_delete=models.CASCADE, related_name="respostas")
    numero_item  = models.IntegerField()
    valor        = models.IntegerField()  # 1=Nunca / 2=Às vezes / 3=Sempre
    observacao   = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ═══════════════════════════════════════════════════════════════════════════════
#  ABA — ANÁLISE DO COMPORTAMENTO APLICADA
# ═══════════════════════════════════════════════════════════════════════════════

# ── Habilidades Adaptativas ───────────────────────────────────────────────────

class AvaliacaoHabilidadesAdaptativas(models.Model):
    """Checklist de habilidades adaptativas para ABA.
    Áreas: Comunicação Funcional, Autocuidado, Socialização,
    Autonomia, Comportamento Adaptativo.
    Escala: 0=Não faz / 1=Ajuda total / 2=Ajuda parcial / 3=Independente.
    """
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente               = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_habilidades_adaptativas")
    token                  = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data                   = models.DateField(default=timezone.now)
    status                 = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual           = models.IntegerField(default=1)

    pont_comunicacao       = models.IntegerField("Comunicação Funcional",    null=True, blank=True)
    pont_autocuidado       = models.IntegerField("Autocuidado",              null=True, blank=True)
    pont_socializacao      = models.IntegerField("Socialização",             null=True, blank=True)
    pont_autonomia         = models.IntegerField("Autonomia",                null=True, blank=True)
    pont_comportamento     = models.IntegerField("Comportamento Adaptativo", null=True, blank=True)

    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Habilidades Adaptativas (ABA)"
        ordering = ["-data"]

    def __str__(self):
        return f"Habilidades Adaptativas — {self.paciente.nome} — {self.data}"


class RespostaHabilidadesAdaptativas(models.Model):
    avaliacao    = models.ForeignKey(AvaliacaoHabilidadesAdaptativas, on_delete=models.CASCADE, related_name="respostas")
    dominio      = models.CharField(max_length=30)
    numero_item  = models.IntegerField()
    valor        = models.IntegerField()  # 0–3
    observacao   = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "dominio", "numero_item")
        ordering = ["dominio", "numero_item"]


# ── Avaliação de Comportamento Funcional ──────────────────────────────────────

class AvaliacaoComportamentoFuncional(models.Model):
    """Rastreio de comportamento funcional — ABA e Neuropediatria.
    Áreas: Iniciação, Manutenção de Tarefa, Flexibilidade/Transições,
    Generalização, Comunicação Funcional, Autocontrole.
    """
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente           = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_comportamento_funcional")
    token              = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data               = models.DateField(default=timezone.now)
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual       = models.IntegerField(default=1)

    pont_iniciacao     = models.IntegerField("Iniciação",                null=True, blank=True)
    pont_manutencao    = models.IntegerField("Manutenção de Tarefa",     null=True, blank=True)
    pont_flexibilidade = models.IntegerField("Flexibilidade/Transições", null=True, blank=True)
    pont_generalizacao = models.IntegerField("Generalização",            null=True, blank=True)
    pont_comunicacao   = models.IntegerField("Comunicação Funcional",    null=True, blank=True)
    pont_autocontrole  = models.IntegerField("Autocontrole",             null=True, blank=True)

    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Comportamento Funcional (ABA)"
        ordering = ["-data"]

    def __str__(self):
        return f"Comportamento Funcional — {self.paciente.nome} — {self.data}"


class RespostaComportamentoFuncional(models.Model):
    avaliacao    = models.ForeignKey(AvaliacaoComportamentoFuncional, on_delete=models.CASCADE, related_name="respostas")
    numero_item  = models.IntegerField()
    valor        = models.IntegerField()
    observacao   = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ═══════════════════════════════════════════════════════════════════════════════
#  NEUROPSICOLOGIA
# ═══════════════════════════════════════════════════════════════════════════════

# ── Rastreio Cognitivo ────────────────────────────────────────────────────────

class AvaliacaoRastreioCognitivo(models.Model):
    """Rastreio neuropsicológico de atenção, memória e funções executivas.
    Usado por Neuropsicólogos e Neuropediatras.
    Áreas: Atenção Sustentada, Atenção Seletiva, Memória de Trabalho,
    Memória Episódica, Funções Executivas, Habilidades Visoespaciais.
    """
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente                  = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_cognitivo")
    token                     = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data                      = models.DateField(default=timezone.now)
    status                    = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual              = models.IntegerField(default=1)

    pont_atencao_sustentada   = models.IntegerField("Atenção Sustentada",        null=True, blank=True)
    pont_atencao_seletiva     = models.IntegerField("Atenção Seletiva",          null=True, blank=True)
    pont_memoria_trabalho     = models.IntegerField("Memória de Trabalho",       null=True, blank=True)
    pont_memoria_episodica    = models.IntegerField("Memória Episódica",         null=True, blank=True)
    pont_funcoes_executivas   = models.IntegerField("Funções Executivas",        null=True, blank=True)
    pont_visoespacial         = models.IntegerField("Habilidades Visoespaciais", null=True, blank=True)

    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rastreio Cognitivo"
        ordering = ["-data"]

    def __str__(self):
        return f"Rastreio Cognitivo — {self.paciente.nome} — {self.data}"


class RespostaRastreioCognitivo(models.Model):
    avaliacao    = models.ForeignKey(AvaliacaoRastreioCognitivo, on_delete=models.CASCADE, related_name="respostas")
    dominio      = models.CharField(max_length=30)
    numero_item  = models.IntegerField()
    valor        = models.IntegerField()
    observacao   = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "dominio", "numero_item")
        ordering = ["dominio", "numero_item"]


# ═══════════════════════════════════════════════════════════════════════════════
#  PSICOPEDAGOGIA
# ═══════════════════════════════════════════════════════════════════════════════

# ── Avaliação Psicopedagógica ─────────────────────────────────────────────────

class AvaliacaoPsicopedagogica(models.Model):
    """Rastreio psicopedagógico de dificuldades de aprendizagem.
    Áreas: Leitura, Escrita, Matemática, Atenção Escolar,
    Comportamento Escolar.
    """
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente             = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_psicopedagogica")
    token                = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data                 = models.DateField(default=timezone.now)
    status               = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual         = models.IntegerField(default=1)

    pont_leitura         = models.IntegerField("Leitura",              null=True, blank=True)
    pont_escrita         = models.IntegerField("Escrita",              null=True, blank=True)
    pont_matematica      = models.IntegerField("Matemática",           null=True, blank=True)
    pont_atencao_escolar = models.IntegerField("Atenção Escolar",      null=True, blank=True)
    pont_comportamento   = models.IntegerField("Comportamento Escolar",null=True, blank=True)

    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Avaliação Psicopedagógica"
        ordering = ["-data"]

    def __str__(self):
        return f"Psicopedagógica — {self.paciente.nome} — {self.data}"


class RespostaPsicopedagogica(models.Model):
    avaliacao    = models.ForeignKey(AvaliacaoPsicopedagogica, on_delete=models.CASCADE, related_name="respostas")
    dominio      = models.CharField(max_length=30)
    numero_item  = models.IntegerField()
    valor        = models.IntegerField()
    observacao   = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "dominio", "numero_item")
        ordering = ["dominio", "numero_item"]


class HistoricoLogin(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name="historico_logins")
    ip          = models.GenericIPAddressField("Endereço IP", null=True, blank=True)
    dispositivo = models.CharField("Dispositivo", max_length=120, blank=True)
    user_agent  = models.TextField("User-Agent completo", blank=True)
    sucesso     = models.BooleanField("Login bem-sucedido", default=True)
    data_hora   = models.DateTimeField("Data/hora", auto_now_add=True)

    class Meta:
        verbose_name        = "Histórico de Login"
        verbose_name_plural = "Histórico de Logins"
        ordering            = ["-data_hora"]

    def __str__(self):
        status = "✓" if self.sucesso else "✗"
        return f"{status} {self.user.username} — {self.ip} — {self.data_hora:%d/%m/%Y %H:%M}"


# ── Solicitação de Upgrade de Plano ───────────────────────────────────────────

# Módulos liberados automaticamente por plano
MODULOS_POR_PLANO = {
    "start": ["sensorial", "bebe", "escolar", "spm"],
    "plus":  ["sensorial", "bebe", "escolar", "spm", "vineland", "pedi", "portage"],
    "elite": [c[0] for c in ModuloAvaliacao.MODULO_CHOICES],
}

PRECO_PLANO = {
    "start": "R$ 39,90/mês",
    "plus":  "R$ 79,90/mês",
    "elite": "R$ 149,90/mês",
}


class SolicitacaoPlano(models.Model):
    STATUS_CHOICES = [
        ("pendente",  "Pendente"),
        ("aprovado",  "Aprovado"),
        ("rejeitado", "Rejeitado"),
    ]
    PLANO_CHOICES = [
        ("start", "START — R$ 39,90/mês"),
        ("plus",  "PLUS — R$ 79,90/mês"),
        ("elite", "ELITE — R$ 149,90/mês"),
    ]

    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name="solicitacoes_plano")
    plano        = models.CharField("Plano solicitado", max_length=10, choices=PLANO_CHOICES)
    status       = models.CharField("Status", max_length=12, choices=STATUS_CHOICES, default="pendente")
    observacoes  = models.TextField("Observações do usuário", blank=True)
    nota_admin   = models.TextField("Nota do admin", blank=True)
    aprovado_por = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="solicitacoes_aprovadas", verbose_name="Aprovado por"
    )
    aprovado_em  = models.DateTimeField("Aprovado/Rejeitado em", null=True, blank=True)
    criado_em    = models.DateTimeField("Solicitado em", auto_now_add=True)

    class Meta:
        verbose_name        = "Solicitação de Plano"
        verbose_name_plural = "Solicitações de Plano"
        ordering            = ["-criado_em"]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} → {self.get_plano_display()} ({self.get_status_display()})"

    @property
    def preco(self):
        return PRECO_PLANO.get(self.plano, "")


# ─────────────────────────────────────────────────────────────────────────────
#  Proxy — aparece no sidebar do admin como "💳 Painel de Pagamentos"
# ─────────────────────────────────────────────────────────────────────────────

class PainelPagamentos(SolicitacaoPlano):
    """Proxy de SolicitacaoPlano — usado apenas para expor o Painel no admin."""

    class Meta:
        proxy        = True
        verbose_name        = "💳 Painel de Pagamentos"
        verbose_name_plural = "💳 Painel de Pagamentos"
