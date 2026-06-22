import uuid
import re
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

_GRACE_DAYS = 5


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
        # ── Psicologia — Triagem Infantil (Pais/Responsáveis) ────────────
        ("sdq",                    "SDQ — Capacidades e Dificuldades"),
        ("snap_iv",                "SNAP-IV — Avaliação de TDAH/TOD"),
        ("mchat",                  "M-CHAT-R — Rastreio de Autismo"),
        ("cars",                   "CARS-2 — Escala de Autismo em Crianças"),
        ("conners_pais",           "Conners-3 — Avaliação TDAH (Pais)"),
        ("etdah_pais",             "ETDAH — Avaliação TDAH (Pais)"),
        ("auqei",                  "AUQEI — Qualidade de Vida Infantil"),
        ("aq10_child",             "AQ-10 Criança — Rastreio de Autismo"),
        ("scared",                 "SCARED — Ansiedade Infantil (Pais)"),
        ("masc",                   "MASC — Ansiedade Multidimensional"),
        ("scq",                    "SCQ — Comunicação Social"),
        # ── Psicologia — Triagem por Professor ──────────────────────────
        ("conners_prof",           "Conners-3 — Avaliação TDAH (Professor)"),
        ("etdah_prof",             "ETDAH — Avaliação TDAH (Professor)"),
        ("k10", "K-10 — Escala de Kessler"),
        ("ucla", "UCLA — Escala de Solidão"),
        ("msi_bpd", "MSI-BPD — Triagem de Borderline"),
        ("gds15", "GDS-15 — Depressão Geriátrica"),
        ("rosenberg", "Rosenberg — Autoestima"),
        ("audit", "AUDIT — Uso de Álcool"),
        ("bis11", "BIS-11 — Impulsividade de Barratt"),
        ("iar", "IAR — Ansiedade Infantil"),
        ("pas", "PAS — Ansiedade Pré-Escolar"),
        ("cdi", "CDI — Depressão Infantil"),
        ("hama", "HAM-A — Ansiedade de Hamilton"),
        ("lsas", "LSAS — Ansiedade Social de Liebowitz"),
        ("risco_suicidio", "Triagem de Risco de Suicídio"),
        ("agorafobia", "Rastreio de Agorafobia"),
        ("panico", "Rastreio de Pânico"),
        # ── Psicologia — Triagem Geral ───────────────────────────────────
        ("phq9",                   "PHQ-9 — Questionário de Saúde do Paciente"),
        ("gad7",                   "GAD-7 — Transtorno de Ansiedade Generalizada"),
        ("epds",                   "EPDS — Depressão Pós-Parto de Edinburgh"),
        ("pcl5",                   "PCL-5 — Lista de Verificação de PTSD"),
        ("ghq12",                  "GHQ-12 — Questionário de Saúde Geral"),
        # ── Psicologia — Instrumentos para Adultos ───────────────────────
        ("bdi",                    "BDI — Inventário de Depressão de Beck"),
        ("bai",                    "BAI — Inventário de Ansiedade de Beck"),
        ("dass21",                 "DASS-21 — Depressão, Ansiedade e Estresse"),
        ("had",                    "HAD — Ansiedade e Depressão Hospitalar"),
        ("bsl23",                  "BSL-23 — Sintomas Borderline"),
        ("aq10_adulto",            "AQ-10 Adulto — Rastreio de Autismo"),
        ("dep_emocional",          "Questionário de Dependência Emocional"),
        ("bpq",                    "BPQ — Personalidade Borderline"),
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
        ("denver",                 "Checklist Denver II — Desenvolvimento"),
        # ── ABA / Análise do Comportamento ───────────────────────────────
        ("habilidades_adaptativas", "Habilidades Adaptativas (ABA)"),
        ("comportamento_funcional", "Comportamento Funcional (ABA)"),
        # ── Neuropsicologia ──────────────────────────────────────────────
        ("rastreio_cognitivo",     "Rastreio Cognitivo"),
        ("qmpi",                   "QMPI — Memória Prospectiva Infantil"),
        # ── Psicopedagogia ───────────────────────────────────────────────
        ("psicopedagogica",        "Avaliação Psicopedagógica"),
        ("quest_dislexia",         "Questionário de Dislexia (Pais)"),
        ("checklist_dislexia",     "Checklist de Dislexia"),
        ("prot_dislexia_prof",     "Protocolo Dislexia — Avaliação Escolar"),
        ("inventario_dislexia",    "Inventário de Sinais Disléxicos"),
        # ── Nutrição / Terapia Alimentar ─────────────────────────────────────
        ("recordatorio_alimentar",   "Recordatório Alimentar (3 dias)"),
        ("anamnese_alimentar",       "Anamnese Alimentar"),
        # ── Seletividade Alimentar ────────────────────────────────────────
        ("ebai",  "EBAI — Escala Brasileira de Alimentação Infantil"),
        ("seps",  "SEPS — Escala de Problemas Sensoriais na Alimentação"),
        ("eca",   "ECA — Escala de Avaliação do Comportamento Alimentar"),
        ("tod",   "TOD — Escala de Comportamentos Disruptivos"),
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
    ("nutricionista",          "Nutrição"),
]

MODULOS_POR_ESPECIALIDADE = {
    "terapeuta_ocupacional": [
        "sensorial", "vineland", "escolar", "bebe", "spm",
        "edm", "mabc2", "beery", "pedi", "vineland3", "portage",
        "ebai", "seps", "eca", "tod",
    ],
    "psicologo": [
        # triagem geral
        "sdq", "snap_iv", "mchat", "cars",
        # infantil — pais
        "conners_pais", "etdah_pais", "auqei", "aq10_child",
        "scared", "masc", "scq",
        # por professor
        "conners_prof", "etdah_prof",
        # adultos
        "bdi", "bai", "dass21", "had", "bsl23", "aq10_adulto",
        "dep_emocional", "bpq",
        # triagem internacional
        "phq9", "gad7", "epds", "pcl5", "ghq12",
        # novas escalas
        "k10", "ucla", "msi_bpd", "rosenberg", "audit",
        "bis11", "lsas", "hama", "risco_suicidio", "agorafobia", "panico",
        "iar", "pas", "cdi", "gds15",
    ],
    "fonoaudiologo": [
        "linguagem", "alimentacao_seletiva",
        "habitos_orais", "voz_infantil", "processamento_auditivo", "idv10",
        "ebai", "seps", "eca",
    ],
    "neuropsicoplogo": [
        "rastreio_cognitivo", "sdq", "snap_iv", "mchat", "cars",
        "qmpi",
        # infantil — pais
        "conners_pais", "etdah_pais", "aq10_child", "scq",
        # por professor
        "conners_prof", "etdah_prof",
        # adultos
        "bdi", "bai", "dass21", "had", "bsl23", "aq10_adulto",
        "bpq",
        # triagem internacional
        "phq9", "gad7", "pcl5", "ghq12",
        # novas escalas
        "k10", "ucla", "msi_bpd", "bis11", "lsas", "hama",
        "risco_suicidio", "agorafobia", "panico",
        "iar", "pas", "cdi",
    ],
    "psicopedagogo": [
        "psicopedagogica", "sdq", "snap_iv",
        "conners_pais", "conners_prof", "etdah_pais", "etdah_prof",
        "quest_dislexia", "checklist_dislexia",
        "prot_dislexia_prof", "inventario_dislexia",
    ],
    "pediatra": [
        "desenvolvimento", "sono_infantil", "mchat", "snap_iv",
        "denver", "auqei", "epds",
        "iar", "pas", "cdi", "gds15",
    ],
    "neuropediatra": [
        "desenvolvimento", "sono_infantil", "mchat", "cars",
        "snap_iv", "rastreio_cognitivo", "sensorial", "denver",
    ],
    "analista_aba": [
        "habilidades_adaptativas", "comportamento_funcional",
        "mchat", "vineland3",
        "ebai", "seps", "eca", "tod",
    ],
    "nutricionista": [
        "recordatorio_alimentar", "anamnese_alimentar", "alimentacao_seletiva",
        "ebai", "seps", "eca",
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
    TIPO_CONTA_CHOICES = [
        ("profissional", "Profissional autônomo"),
        ("clinica", "Clínica / Equipe"),
    ]
    tipo_conta = models.CharField(
        "Tipo de conta", max_length=15, choices=TIPO_CONTA_CHOICES, default="profissional"
    )
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
    codigo_indicacao = models.UUIDField(
        "Código de indicação", default=uuid.uuid4, editable=False, unique=True
    )
    token_confirmacao = models.UUIDField(
        "Token de confirmação de e-mail", null=True, blank=True, unique=True
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

    @property
    def plano_vencido(self):
        """True quando o plano pago expirou."""
        if self.plano == "trial" or self.plano_expiracao is None:
            return False
        return timezone.now() >= self.plano_expiracao

    @property
    def plano_vencendo_breve(self):
        """True quando o plano pago ativo vence em até 7 dias (inclui o dia de hoje)."""
        dias = self.plano_dias_restantes
        return dias is not None and dias <= 7

    def tem_acesso(self, codigo_modulo):
        now = timezone.now()
        if self.plano == "trial":
            if self.trial_inicio is None:
                return False
            if (now - self.trial_inicio).days > 7 + _GRACE_DAYS:
                return False
        elif (
            self.plano_expiracao is not None
            and now > self.plano_expiracao + timedelta(days=_GRACE_DAYS)
        ):
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

class Indicacao(models.Model):
    """Registra que `indicado` se cadastrou através do link de indicação de `indicador`."""
    RECOMPENSA_DIAS = 30

    indicador = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="indicacoes_feitas",
        verbose_name="Indicado por"
    )
    indicado = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="indicacao_origem",
        verbose_name="Profissional indicado"
    )
    criado_em = models.DateTimeField("Cadastrado em", auto_now_add=True)
    recompensa_aplicada = models.BooleanField("Recompensa aplicada", default=False)
    recompensa_aplicada_em = models.DateTimeField("Recompensa aplicada em", null=True, blank=True)

    class Meta:
        verbose_name = "Indicação"
        verbose_name_plural = "Indicações"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.indicador.username} indicou {self.indicado.username}"


# ── Terapia Alimentar ─────────────────────────────────────────────────────────

class AvaliacaoRecordatorio(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_recordatorio")
    token = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data = models.DateField("Data da avaliação", default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual = models.IntegerField(default=1)
    observacoes = models.TextField("Observações clínicas", blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Recordatório Alimentar"
        verbose_name_plural = "Recordatórios Alimentares"
        ordering = ["-data"]

    def __str__(self):
        return f"Recordatório — {self.paciente.nome} — {self.data}"


REFEICAO_CHOICES = [
    ("cafe", "Café da manhã"),
    ("lanche_manha", "Lanche da manhã"),
    ("almoco", "Almoço"),
    ("lanche_tarde", "Lanche da tarde"),
    ("jantar", "Jantar"),
    ("ceia", "Ceia"),
    ("entre_refeicoes", "Entre refeições"),
]

DIA_CHOICES = [
    ("1", "Dia 1 — semana"),
    ("2", "Dia 2 — semana"),
    ("3", "Dia 3 — fim de semana"),
]


class EntradaRecordatorio(models.Model):
    avaliacao = models.ForeignKey(AvaliacaoRecordatorio, on_delete=models.CASCADE, related_name="entradas")
    dia = models.CharField(max_length=1, choices=DIA_CHOICES)
    refeicao = models.CharField(max_length=20, choices=REFEICAO_CHOICES)
    horario = models.CharField(max_length=20, blank=True, default="")
    o_que_comeu = models.TextField(blank=True, default="")
    onde = models.CharField(max_length=100, blank=True, default="")
    com_quem = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "dia", "refeicao")
        ordering = ["dia", "refeicao"]


TIPO_INVENTARIO_CHOICES = [
    ("recusado", "Deixou de comer"),
    ("familiar", "Cardápio familiar"),
    ("aceito", "Come atualmente"),
]


class InventarioAlimento(models.Model):
    avaliacao = models.ForeignKey(AvaliacaoRecordatorio, on_delete=models.CASCADE, related_name="inventario")
    tipo = models.CharField(max_length=10, choices=TIPO_INVENTARIO_CHOICES)
    ordem = models.IntegerField(default=0)
    alimento = models.CharField(max_length=200, blank=True, default="")
    preparo = models.TextField(blank=True, default="")
    horario = models.CharField(max_length=50, blank=True, default="")
    observacao = models.TextField(blank=True, default="")
    tempo = models.CharField(max_length=100, blank=True, default="")  # only for 'recusado'

    class Meta:
        ordering = ["tipo", "ordem"]


class AvaliacaoAnamnese(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_anamnese")
    data = models.DateField("Data da avaliação", default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual = models.IntegerField(default=1)

    # Parte 1: História
    hist_alergia = models.BooleanField(default=False)
    hist_refluxo = models.BooleanField(default=False)
    hist_prob_gi = models.BooleanField(default=False)
    hist_dif_respiratoria = models.BooleanField(default=False)
    hist_baixo_peso = models.BooleanField(default=False)
    hist_prematuridade = models.BooleanField(default=False)
    hist_tonus = models.BooleanField(default=False)
    hist_explane = models.TextField(blank=True, default="")

    func_amamentacao = models.BooleanField(default=False)
    func_mamadeira = models.BooleanField(default=False)
    func_papinhas = models.BooleanField(default=False)
    func_solidos = models.BooleanField(default=False)
    func_maos = models.BooleanField(default=False)
    func_utensilios = models.BooleanField(default=False)
    func_copo = models.BooleanField(default=False)
    func_explane = models.TextField(blank=True, default="")
    historico_declinio = models.TextField(blank=True, default="")

    # Parte 2: Frequência Sensorial
    # Visual
    sens_visual_forma = models.TextField(blank=True, default="")
    sens_visual_cor = models.TextField(blank=True, default="")
    sens_visual_tamanho = models.TextField(blank=True, default="")
    sens_visual_outros = models.TextField(blank=True, default="")
    # Olfato
    sens_olfato_pouco = models.TextField(blank=True, default="")
    sens_olfato_intenso = models.TextField(blank=True, default="")
    sens_olfato_nao_importa = models.TextField(blank=True, default="")
    sens_olfato_outros = models.TextField(blank=True, default="")
    # Tato
    sens_tato_frio = models.TextField(blank=True, default="")
    sens_tato_quente = models.TextField(blank=True, default="")
    sens_tato_morno = models.TextField(blank=True, default="")
    sens_tato_mole = models.TextField(blank=True, default="")
    sens_tato_dura = models.TextField(blank=True, default="")
    sens_tato_semi_dura = models.TextField(blank=True, default="")
    sens_tato_liso = models.TextField(blank=True, default="")
    sens_tato_rugoso = models.TextField(blank=True, default="")
    sens_tato_aspero = models.TextField(blank=True, default="")
    sens_tato_pegajoso = models.TextField(blank=True, default="")
    sens_tato_seco = models.TextField(blank=True, default="")
    sens_tato_umido = models.TextField(blank=True, default="")
    # Propriocepção
    sens_propr_complexos = models.TextField(blank=True, default="")
    sens_propr_simples = models.TextField(blank=True, default="")
    sens_propr_forca = models.TextField(blank=True, default="")
    sens_propr_resistencia = models.TextField(blank=True, default="")
    # Gosto
    sens_gosto_doce = models.TextField(blank=True, default="")
    sens_gosto_salgado = models.TextField(blank=True, default="")
    sens_gosto_amargo = models.TextField(blank=True, default="")
    sens_gosto_acido = models.TextField(blank=True, default="")
    sens_gosto_umami = models.TextField(blank=True, default="")
    # Auditivo
    sens_audit_barulho = models.TextField(blank=True, default="")
    sens_audit_crocante = models.TextField(blank=True, default="")
    sens_audit_silencioso = models.TextField(blank=True, default="")

    observacoes = models.TextField("Observações clínicas", blank=True, default="")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Anamnese Alimentar"
        verbose_name_plural = "Anamneses Alimentares"
        ordering = ["-data"]

    def __str__(self):
        return f"Anamnese Alimentar — {self.paciente.nome} — {self.data}"


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
        # ── Psicologia — Triagem Infantil (Pais/Responsáveis) ────────────
        ("sdq",                     "SDQ — Capacidades e Dificuldades"),
        ("snap_iv",                 "SNAP-IV — Avaliação de TDAH/TOD"),
        ("mchat",                   "M-CHAT-R — Rastreio de Autismo"),
        ("cars",                    "CARS-2 — Escala de Autismo em Crianças"),
        ("conners_pais",            "Conners-3 — Avaliação TDAH (Pais)"),
        ("etdah_pais",              "ETDAH — Avaliação TDAH (Pais)"),
        ("auqei",                   "AUQEI — Qualidade de Vida Infantil"),
        ("aq10_child",              "AQ-10 Criança — Rastreio de Autismo"),
        ("scared",                  "SCARED — Ansiedade Infantil (Pais)"),
        ("masc",                    "MASC — Ansiedade Multidimensional"),
        ("scq",                     "SCQ — Comunicação Social"),
        # ── Psicologia — Triagem por Professor ──────────────────────────
        ("conners_prof",            "Conners-3 — Avaliação TDAH (Professor)"),
        ("etdah_prof",              "ETDAH — Avaliação TDAH (Professor)"),
        # ── Psicologia — Instrumentos para Adultos ───────────────────────
        ("bdi",                     "BDI — Inventário de Depressão de Beck"),
        ("bai",                     "BAI — Inventário de Ansiedade de Beck"),
        ("dass21",                  "DASS-21 — Depressão, Ansiedade e Estresse"),
        ("had",                     "HAD — Ansiedade e Depressão Hospitalar"),
        ("bsl23",                   "BSL-23 — Sintomas Borderline"),
        ("aq10_adulto",             "AQ-10 Adulto — Rastreio de Autismo"),
        ("dep_emocional",           "Questionário de Dependência Emocional"),
        ("bpq",                     "BPQ — Personalidade Borderline"),
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
        ("denver",                  "Checklist Denver II — Desenvolvimento"),
        # ── ABA / Análise do Comportamento ───────────────────────────────
        ("habilidades_adaptativas", "Habilidades Adaptativas (ABA)"),
        ("comportamento_funcional", "Comportamento Funcional (ABA)"),
        # ── Neuropsicologia ──────────────────────────────────────────────
        ("rastreio_cognitivo",      "Rastreio Cognitivo"),
        ("qmpi",                    "QMPI — Memória Prospectiva Infantil"),
        # ── Psicopedagogia ───────────────────────────────────────────────
        ("psicopedagogica",         "Avaliação Psicopedagógica"),
        ("quest_dislexia",          "Questionário de Dislexia (Pais)"),
        ("checklist_dislexia",      "Checklist de Dislexia"),
        ("prot_dislexia_prof",      "Protocolo Dislexia — Avaliação Escolar"),
        ("inventario_dislexia",     "Inventário de Sinais Disléxicos"),
        # ── Triagem Internacional ────────────────────────────────────────
        ("phq9",                    "PHQ-9 — Questionário de Saúde do Paciente"),
        ("gad7",                    "GAD-7 — Transtorno de Ansiedade Generalizada"),
        ("epds",                    "EPDS — Depressão Pós-Parto de Edinburgh"),
        ("pcl5",                    "PCL-5 — Lista de Verificação de PTSD"),
        ("ghq12",                   "GHQ-12 — Questionário de Saúde Geral"),
        # ── Novas Escalas — Adulto ───────────────────────────────────────
        ("k10",                     "K-10 — Escala de Kessler"),
        ("ucla",                    "UCLA — Escala de Solidão"),
        ("msi_bpd",                 "MSI-BPD — Triagem de Borderline"),
        ("gds15",                   "GDS-15 — Depressão Geriátrica"),
        ("rosenberg",               "Rosenberg — Autoestima"),
        ("audit",                   "AUDIT — Uso de Álcool"),
        ("bis11",                   "BIS-11 — Impulsividade de Barratt"),
        ("hama",                    "HAM-A — Ansiedade de Hamilton"),
        ("lsas",                    "LSAS — Ansiedade Social de Liebowitz"),
        ("risco_suicidio",          "Triagem de Risco de Suicídio"),
        ("agorafobia",              "Rastreio de Agorafobia"),
        ("panico",                  "Rastreio de Pânico"),
        # ── Novas Escalas — Infantil ─────────────────────────────────────
        ("iar",                     "IAR — Ansiedade Infantil"),
        ("pas",                     "PAS — Ansiedade Pré-Escolar"),
        ("cdi",                     "CDI — Depressão Infantil"),
        # ── Nutrição / Terapia Alimentar ─────────────────────────────────────
        ("recordatorio_alimentar",   "Recordatório Alimentar (Pais)"),
        # ── Seletividade Alimentar ────────────────────────────────────────
        ("ebai",  "EBAI — Escala Brasileira de Alimentação Infantil"),
        ("seps",  "SEPS — Escala de Problemas Sensoriais na Alimentação"),
        ("eca",   "ECA — Avaliação do Comportamento Alimentar"),
        ("tod",   "TOD — Escala de Comportamentos Disruptivos"),
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
    observacao  = models.TextField(blank=True, default="")

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


# ── BDI — Inventário de Depressão de Beck ────────────────────────────────────

class AvaliacaoBDI(models.Model):
    """BDI — Beck Depression Inventory (Beck et al., 1961). 21 itens, 0–3 cada.
    Pontuação total 0–63. Pontos de corte: mínimo/leve/moderado/grave."""
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_bdi")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)

    pont_total       = models.IntegerField("Pontuação Total (0–63)", null=True, blank=True)

    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "BDI — Inventário de Depressão de Beck"
        ordering = ["-data"]

    def __str__(self):
        return f"BDI — {self.paciente.nome} — {self.data}"


class RespostaBDI(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoBDI, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── BAI — Inventário de Ansiedade de Beck ────────────────────────────────────

class AvaliacaoBAI(models.Model):
    """BAI — Beck Anxiety Inventory (Beck et al., 1988). 21 itens, 0–3 cada.
    Pontuação total 0–63. Pontos de corte: mínimo/leve/moderado/grave."""
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_bai")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)

    pont_total       = models.IntegerField("Pontuação Total (0–63)", null=True, blank=True)

    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "BAI — Inventário de Ansiedade de Beck"
        ordering = ["-data"]

    def __str__(self):
        return f"BAI — {self.paciente.nome} — {self.data}"


class RespostaBAI(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoBAI, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── DASS-21 — Depressão, Ansiedade e Estresse ────────────────────────────────

class AvaliacaoDASS21(models.Model):
    """DASS-21 — Depression Anxiety Stress Scales (Lovibond & Lovibond, 1995).
    21 itens (7 por subescala), escala 0–3. Multiplica-se por 2 para comparar
    com DASS-42. Pontos de corte por subescala."""
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_dass21")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)

    pont_depressao   = models.IntegerField("Depressão (0–42)", null=True, blank=True)
    pont_ansiedade   = models.IntegerField("Ansiedade (0–42)", null=True, blank=True)
    pont_estresse    = models.IntegerField("Estresse (0–42)", null=True, blank=True)

    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "DASS-21 — Depressão, Ansiedade e Estresse"
        ordering = ["-data"]

    def __str__(self):
        return f"DASS-21 — {self.paciente.nome} — {self.data}"


class RespostaDASS21(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoDASS21, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── HAD — Escala de Ansiedade e Depressão Hospitalar ─────────────────────────

class AvaliacaoHAD(models.Model):
    """HAD — Hospital Anxiety and Depression Scale (Zigmond & Snaith, 1983).
    14 itens (7 ansiedade + 7 depressão), escala 0–3 por item.
    Pontuação 0–21 por subescala. Corte ≥ 8 indica caso provável."""
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid              = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente          = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_had")
    token             = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data              = models.DateField(default=timezone.now)
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual      = models.IntegerField(default=1)

    pont_ansiedade    = models.IntegerField("Ansiedade (0–21)", null=True, blank=True)
    pont_depressao    = models.IntegerField("Depressão (0–21)", null=True, blank=True)

    observacoes       = models.TextField(blank=True, default="")
    email_enviado_em  = models.DateTimeField(null=True, blank=True)
    criado_em         = models.DateTimeField(auto_now_add=True)
    atualizado_em     = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "HAD — Ansiedade e Depressão Hospitalar"
        ordering = ["-data"]

    def __str__(self):
        return f"HAD — {self.paciente.nome} — {self.data}"


class RespostaHAD(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoHAD, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── BSL-23 — Borderline Symptom List ─────────────────────────────────────────

class AvaliacaoBSL23(models.Model):
    """BSL-23 — Borderline Symptom List (Bohus et al., 2009).
    23 itens, escala 0–4. Pontuação: média aritmética dos itens (0–4).
    Cortes: Normal <0,70, Leve 0,70–1,30, Moderado 1,31–2,50, Grave 2,51–3,50, Muito Grave >3,50."""
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_bsl23")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)

    media_total      = models.FloatField("Média Total (0–4)", null=True, blank=True)

    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "BSL-23 — Sintomas Borderline"
        ordering = ["-data"]

    def __str__(self):
        return f"BSL-23 — {self.paciente.nome} — {self.data}"


class RespostaBSL23(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoBSL23, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── AQ-10 Adulto — Rastreio de Autismo ───────────────────────────────────────

class AvaliacaoAQ10Adulto(models.Model):
    """AQ-10 Adulto — Autism Quotient (Allison et al., 2012).
    10 itens, escala 0–1 (pontuação binária). Total 0–10. Corte ≥ 6 indica rastreio positivo."""
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_aq10_adulto")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)

    pont_total       = models.IntegerField("Pontuação Total (0–10)", null=True, blank=True)

    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AQ-10 Adulto — Rastreio de Autismo"
        ordering = ["-data"]

    def __str__(self):
        return f"AQ-10 Adulto — {self.paciente.nome} — {self.data}"


class RespostaAQ10Adulto(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoAQ10Adulto, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── AQ-10 Criança — Rastreio de Autismo ──────────────────────────────────────

class AvaliacaoAQ10Child(models.Model):
    """AQ-10 Criança — Autism Quotient (Allison et al., 2012).
    10 itens, escala 0–1 (pontuação binária). Total 0–10. Corte ≥ 6 indica rastreio positivo."""
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_aq10_child")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)

    pont_total       = models.IntegerField("Pontuação Total (0–10)", null=True, blank=True)

    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AQ-10 Criança — Rastreio de Autismo"
        ordering = ["-data"]

    def __str__(self):
        return f"AQ-10 Criança — {self.paciente.nome} — {self.data}"


class RespostaAQ10Child(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoAQ10Child, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── Dependência Emocional ─────────────────────────────────────────────────────

class AvaliacaoDepEmocional(models.Model):
    """Questionário de Dependência Emocional (Lemos & Londoño, 2006).
    66 itens agrupados em 6 subescalas, escala 1–6. Pontuação por subescala."""
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid                      = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente                  = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_dep_emocional")
    token                     = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data                      = models.DateField(default=timezone.now)
    status                    = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual              = models.IntegerField(default=1)

    pont_ansiedade_separacao  = models.IntegerField("Ansiedade de Separação", null=True, blank=True)
    pont_expressao_afetiva    = models.IntegerField("Expressão Afetiva", null=True, blank=True)
    pont_modificacao_planos   = models.IntegerField("Modificação de Planos", null=True, blank=True)
    pont_miedo_soledad        = models.IntegerField("Medo da Solidão", null=True, blank=True)
    pont_expresion_limite     = models.IntegerField("Expressão Limite", null=True, blank=True)
    pont_busqueda_atencion    = models.IntegerField("Busca de Atenção", null=True, blank=True)

    observacoes               = models.TextField(blank=True, default="")
    email_enviado_em          = models.DateTimeField(null=True, blank=True)
    criado_em                 = models.DateTimeField(auto_now_add=True)
    atualizado_em             = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dependência Emocional"
        ordering = ["-data"]

    def __str__(self):
        return f"Dep. Emocional — {self.paciente.nome} — {self.data}"


class RespostaDepEmocional(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoDepEmocional, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── SCQ — Social Communication Questionnaire ─────────────────────────────────

class AvaliacaoSCQ(models.Model):
    """SCQ — Social Communication Questionnaire (Rutter et al., 2003).
    40 itens Sim/Não. Pontuação total 0–40. Corte ≥ 15 indica rastreio positivo para TEA."""
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_scq")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)

    pont_total       = models.IntegerField("Pontuação Total (0–40)", null=True, blank=True)

    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "SCQ — Comunicação Social"
        ordering = ["-data"]

    def __str__(self):
        return f"SCQ — {self.paciente.nome} — {self.data}"


# ── Conners-3 — Avaliação de TDAH ────────────────────────────────────────────

class AvaliacaoConners(models.Model):
    """Conners-3 (Conners, 2008). 45 itens, escala 0-3. 6 subescalas.
    Versões: Pais e Professor."""
    RESPONDENTE_CHOICES = [
        ("pais",      "Pais / Cuidadores"),
        ("professor", "Professor"),
    ]
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_conners")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    respondente      = models.CharField(max_length=10, choices=RESPONDENTE_CHOICES, default="pais")
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)

    pont_desatencao  = models.IntegerField("Desatenção", null=True, blank=True)
    pont_hiperativ   = models.IntegerField("Hiperatividade/Impulsividade", null=True, blank=True)
    pont_aprend      = models.IntegerField("Problemas de Aprendizagem", null=True, blank=True)
    pont_exec        = models.IntegerField("Funções Executivas", null=True, blank=True)
    pont_pares       = models.IntegerField("Relação com Pares", null=True, blank=True)
    pont_agressiv    = models.IntegerField("Agressividade/TOD", null=True, blank=True)
    pont_total       = models.IntegerField("Total", null=True, blank=True)

    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Conners-3 — Avaliação TDAH"
        ordering = ["-data"]

    def __str__(self):
        return f"Conners-3 ({self.respondente}) — {self.paciente.nome} — {self.data}"


class RespostaConners(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoConners, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── ETDAH — Escala de TDAH ────────────────────────────────────────────────────

class AvaliacaoETDAH(models.Model):
    """ETDAH. 25 itens, escala 0-3. 3 subescalas. Versões: Pais e Professor."""
    RESPONDENTE_CHOICES = [
        ("pais",      "Pais / Cuidadores"),
        ("professor", "Professor"),
    ]
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_etdah")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    respondente      = models.CharField(max_length=10, choices=RESPONDENTE_CHOICES, default="pais")
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)

    pont_desatencao  = models.FloatField("Desatenção (média)", null=True, blank=True)
    pont_hiperativ   = models.FloatField("Hiperatividade/Impulsividade (média)", null=True, blank=True)
    pont_tod         = models.FloatField("TOD (média)", null=True, blank=True)
    pont_total       = models.FloatField("Total (média geral)", null=True, blank=True)

    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ETDAH — Avaliação TDAH"
        ordering = ["-data"]

    def __str__(self):
        return f"ETDAH ({self.respondente}) — {self.paciente.nome} — {self.data}"


class RespostaETDAH(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoETDAH, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── AUQEI — Qualidade de Vida Infantil ────────────────────────────────────────

class AvaliacaoAUQEI(models.Model):
    """AUQEI. 26 itens, escala 1-4. 7 subescalas. Total ≥ 48 = satisfatório."""
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid              = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente          = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_auqei")
    token             = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data              = models.DateField(default=timezone.now)
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual      = models.IntegerField(default=1)

    pont_familia      = models.FloatField("Família", null=True, blank=True)
    pont_lazer        = models.FloatField("Lazer", null=True, blank=True)
    pont_escola       = models.FloatField("Escola", null=True, blank=True)
    pont_autonomia    = models.FloatField("Autonomia", null=True, blank=True)
    pont_funcoes      = models.FloatField("Funções Corporais", null=True, blank=True)
    pont_amigos       = models.FloatField("Amigos", null=True, blank=True)
    pont_independente = models.FloatField("Itens Independentes", null=True, blank=True)
    pont_total        = models.IntegerField("Total (26–104)", null=True, blank=True)

    observacoes       = models.TextField(blank=True, default="")
    email_enviado_em  = models.DateTimeField(null=True, blank=True)
    criado_em         = models.DateTimeField(auto_now_add=True)
    atualizado_em     = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AUQEI — Qualidade de Vida Infantil"
        ordering = ["-data"]

    def __str__(self):
        return f"AUQEI — {self.paciente.nome} — {self.data}"


class RespostaAUQEI(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoAUQEI, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── SCARED — Ansiedade Infantil ───────────────────────────────────────────────

class AvaliacaoSCARED(models.Model):
    """SCARED (Birmaher, 1997). 41 itens, escala 0-2. 5 subescalas. Total ≥ 25 positivo."""
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid               = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente           = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_scared")
    token              = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data               = models.DateField(default=timezone.now)
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual       = models.IntegerField(default=1)

    pont_panico        = models.IntegerField("Pânico / Somático", null=True, blank=True)
    pont_generalizada  = models.IntegerField("Ansiedade Generalizada", null=True, blank=True)
    pont_fobia_social  = models.IntegerField("Fobia Social", null=True, blank=True)
    pont_separacao     = models.IntegerField("Ansiedade de Separação", null=True, blank=True)
    pont_escola        = models.IntegerField("Ansiedade Escolar", null=True, blank=True)
    pont_total         = models.IntegerField("Total (0–82)", null=True, blank=True)

    observacoes        = models.TextField(blank=True, default="")
    email_enviado_em   = models.DateTimeField(null=True, blank=True)
    criado_em          = models.DateTimeField(auto_now_add=True)
    atualizado_em      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "SCARED — Ansiedade Infantil"
        ordering = ["-data"]

    def __str__(self):
        return f"SCARED — {self.paciente.nome} — {self.data}"


class RespostaSCARED(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoSCARED, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── MASC — Ansiedade Multidimensional ─────────────────────────────────────────

class AvaliacaoMASC(models.Model):
    """MASC (March et al., 1997). 39 itens, escala 0-3. 4 subescalas."""
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid               = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente           = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_masc")
    token              = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data               = models.DateField(default=timezone.now)
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual       = models.IntegerField(default=1)

    pont_sint_fisicos  = models.IntegerField("Sintomas Físicos", null=True, blank=True)
    pont_anx_social    = models.IntegerField("Ansiedade Social", null=True, blank=True)
    pont_evit_danos    = models.IntegerField("Evitação de Danos", null=True, blank=True)
    pont_sep_panico    = models.IntegerField("Ansiedade de Separação / Pânico", null=True, blank=True)
    pont_total         = models.IntegerField("Total (0–117)", null=True, blank=True)

    observacoes        = models.TextField(blank=True, default="")
    email_enviado_em   = models.DateTimeField(null=True, blank=True)
    criado_em          = models.DateTimeField(auto_now_add=True)
    atualizado_em      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "MASC — Ansiedade Multidimensional"
        ordering = ["-data"]

    def __str__(self):
        return f"MASC — {self.paciente.nome} — {self.data}"


class RespostaMASC(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoMASC, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── BPQ — Borderline Personality Questionnaire ────────────────────────────────

class AvaliacaoBPQ(models.Model):
    """BPQ (Poreh et al., 2006). 80 itens Verdadeiro/Falso. 9 subescalas."""
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid                 = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente             = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_bpq")
    token                = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data                 = models.DateField(default=timezone.now)
    status               = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual         = models.IntegerField(default=1)

    pont_impulsividade   = models.IntegerField("Impulsividade", null=True, blank=True)
    pont_inst_afetiva    = models.IntegerField("Instabilidade Afetiva", null=True, blank=True)
    pont_identidade      = models.IntegerField("Problemas de Identidade", null=True, blank=True)
    pont_relacoes        = models.IntegerField("Relações Interpessoais", null=True, blank=True)
    pont_automutilacao   = models.IntegerField("Automutilação / Suicídio", null=True, blank=True)
    pont_medo_abandono   = models.IntegerField("Medo de Abandono", null=True, blank=True)
    pont_paranoia        = models.IntegerField("Ideias Paranoides / Dissociação", null=True, blank=True)
    pont_vazio           = models.IntegerField("Sentimento de Vazio", null=True, blank=True)
    pont_raiva           = models.IntegerField("Raiva Intensa", null=True, blank=True)
    pont_total           = models.IntegerField("Total (0–80)", null=True, blank=True)

    observacoes          = models.TextField(blank=True, default="")
    email_enviado_em     = models.DateTimeField(null=True, blank=True)
    criado_em            = models.DateTimeField(auto_now_add=True)
    atualizado_em        = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "BPQ — Personalidade Borderline"
        ordering = ["-data"]

    def __str__(self):
        return f"BPQ — {self.paciente.nome} — {self.data}"


class RespostaBPQ(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoBPQ, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


class RespostaSCQ(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoSCQ, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── Denver II — Checklist de Desenvolvimento ──────────────────────────────────

class AvaliacaoDenver(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid     = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_denver")
    data     = models.DateField(default=timezone.now)
    status   = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")

    pont_pessoal_social  = models.IntegerField(null=True, blank=True)
    pont_motor_fino      = models.IntegerField(null=True, blank=True)
    pont_linguagem       = models.IntegerField(null=True, blank=True)
    pont_motor_grosseiro = models.IntegerField(null=True, blank=True)

    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    email_enviado_em = models.DateTimeField(blank=True, null=True)
    observacoes      = models.TextField(blank=True, default="")
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Avaliação Denver II"
        ordering = ["-data"]

    def __str__(self):
        return f"Denver II — {self.paciente.nome} — {self.data}"


class RespostaDenver(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoDenver, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField(null=True, blank=True)  # 1=Passa, 0=Falha, None=NT
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── QMPI — Morbidade Psiquiátrica Infantil ─────────────────────────────────────

class AvaliacaoQMPI(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid     = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_qmpi")
    data     = models.DateField(default=timezone.now)
    status   = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    token    = models.CharField(max_length=64, blank=True, default="")

    pont_ansiedade = models.IntegerField(null=True, blank=True)
    pont_depressao = models.IntegerField(null=True, blank=True)
    pont_tdah      = models.IntegerField(null=True, blank=True)
    pont_conduta   = models.IntegerField(null=True, blank=True)
    pont_autismo   = models.IntegerField(null=True, blank=True)

    observacoes     = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em       = models.DateTimeField(auto_now_add=True)
    atualizado_em   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Avaliação QMPI"
        ordering = ["-data"]

    def __str__(self):
        return f"QMPI — {self.paciente.nome} — {self.data}"


class RespostaQMPI(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoQMPI, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── Questionário de Dislexia (Pais) ────────────────────────────────────────────

class AvaliacaoQuestDislexia(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid     = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_quest_dislexia")
    data     = models.DateField(default=timezone.now)
    status   = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    token    = models.CharField(max_length=64, blank=True, default="")

    pont_linguagem_oral  = models.IntegerField(null=True, blank=True)
    pont_leitura_escrita = models.IntegerField(null=True, blank=True)
    pont_memoria         = models.IntegerField(null=True, blank=True)
    pont_atencao         = models.IntegerField(null=True, blank=True)
    pont_total           = models.IntegerField(null=True, blank=True)

    observacoes     = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em       = models.DateTimeField(auto_now_add=True)
    atualizado_em   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Questionário de Dislexia (Pais)"
        ordering = ["-data"]

    def __str__(self):
        return f"Quest.Dislexia — {self.paciente.nome} — {self.data}"


class RespostaQuestDislexia(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoQuestDislexia, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── Checklist de Dislexia ──────────────────────────────────────────────────────

class AvaliacaoChecklistDislexia(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid     = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_checklist_dislexia")
    data     = models.DateField(default=timezone.now)
    status   = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    token    = models.CharField(max_length=64, blank=True, default="")

    pont_leitura       = models.IntegerField(null=True, blank=True)
    pont_escrita       = models.IntegerField(null=True, blank=True)
    pont_processamento = models.IntegerField(null=True, blank=True)
    pont_total         = models.IntegerField(null=True, blank=True)

    observacoes     = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em       = models.DateTimeField(auto_now_add=True)
    atualizado_em   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Checklist de Dislexia"
        ordering = ["-data"]

    def __str__(self):
        return f"ChecklistDislexia — {self.paciente.nome} — {self.data}"


class RespostaChecklistDislexia(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoChecklistDislexia, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── Protocolo Dislexia — Avaliação Escolar (Professor) ─────────────────────────

class AvaliacaoProtDislexiaProf(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid     = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_prot_dislexia_prof")
    data     = models.DateField(default=timezone.now)
    status   = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    token    = models.CharField(max_length=64, blank=True, default="")

    pont_leitura    = models.IntegerField(null=True, blank=True)
    pont_escrita    = models.IntegerField(null=True, blank=True)
    pont_matematica = models.IntegerField(null=True, blank=True)
    pont_organizacao = models.IntegerField(null=True, blank=True)

    observacoes     = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em       = models.DateTimeField(auto_now_add=True)
    atualizado_em   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Protocolo Dislexia — Professor"
        ordering = ["-data"]

    def __str__(self):
        return f"ProtDislexiaProf — {self.paciente.nome} — {self.data}"


class RespostaProtDislexiaProf(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoProtDislexiaProf, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── Inventário de Sinais Disléxicos ────────────────────────────────────────────

class AvaliacaoInventarioDislexia(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]

    uuid     = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_inventario_dislexia")
    data     = models.DateField(default=timezone.now)
    status   = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")

    historico_escolar        = models.TextField("Histórico Escolar", blank=True, default="")
    desempenho_leitura       = models.TextField("Desempenho em Leitura", blank=True, default="")
    desempenho_escrita       = models.TextField("Desempenho em Escrita", blank=True, default="")
    processamento_fonologico = models.TextField("Processamento Fonológico", blank=True, default="")
    memoria_trabalho         = models.TextField("Memória de Trabalho", blank=True, default="")
    velocidade_processamento = models.TextField("Velocidade de Processamento", blank=True, default="")
    historico_familiar       = models.TextField("Histórico Familiar", blank=True, default="")
    avaliacoes_anteriores    = models.TextField("Avaliações Anteriores", blank=True, default="")
    observacoes              = models.TextField("Observações Clínicas", blank=True, default="")

    criado_em    = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Inventário de Sinais Disléxicos"
        ordering = ["-data"]

    def __str__(self):
        return f"InventarioDislexia — {self.paciente.nome} — {self.data}"


# ── Solicitação de Upgrade de Plano ───────────────────────────────────────────

# Módulos por plano por especialidade — define o acesso em cada tier
MODULOS_POR_PLANO_POR_ESPECIALIDADE = {
    "terapeuta_ocupacional": {
        "trial": ["sensorial", "bebe", "escolar", "spm"],
        "start": ["sensorial", "bebe", "escolar", "spm",
                  "ebai", "seps", "eca", "tod"],
        "plus":  ["sensorial", "bebe", "escolar", "spm", "vineland", "pedi", "portage",
                  "edm", "mabc2", "beery",
                  "ebai", "seps", "eca", "tod"],
        "elite": ["sensorial", "vineland", "escolar", "bebe", "spm",
                  "edm", "mabc2", "beery", "pedi", "vineland3", "portage",
                  "ebai", "seps", "eca", "tod"],
    },
    "psicologo": {
        "trial": ["phq9", "gad7", "sdq", "mchat"],
        "start": ["phq9", "gad7", "sdq", "mchat",
                  "snap_iv", "epds", "ghq12", "bdi", "bai", "dass21",
                  "auqei", "k10", "rosenberg"],
        "plus":  ["phq9", "gad7", "sdq", "mchat",
                  "snap_iv", "epds", "ghq12", "bdi", "bai", "dass21",
                  "auqei", "k10", "rosenberg",
                  "conners_pais", "etdah_pais", "conners_prof", "etdah_prof",
                  "aq10_child", "scared", "masc", "scq", "cars",
                  "ucla", "msi_bpd", "audit", "bis11", "lsas", "hama",
                  "risco_suicidio", "agorafobia", "panico",
                  "iar", "pas", "cdi", "gds15", "had", "aq10_adulto"],
        "elite": list(dict.fromkeys(MODULOS_POR_ESPECIALIDADE["psicologo"])),
    },
    "fonoaudiologo": {
        "trial": ["linguagem", "alimentacao_seletiva"],
        "start": ["linguagem", "alimentacao_seletiva", "habitos_orais", "voz_infantil",
                  "ebai", "seps", "eca"],
        "plus":  ["linguagem", "alimentacao_seletiva", "habitos_orais", "voz_infantil",
                  "processamento_auditivo", "idv10",
                  "ebai", "seps", "eca"],
        "elite": ["linguagem", "alimentacao_seletiva", "habitos_orais", "voz_infantil",
                  "processamento_auditivo", "idv10",
                  "ebai", "seps", "eca"],
    },
    "neuropsicoplogo": {
        "trial": ["rastreio_cognitivo", "phq9", "gad7", "mchat"],
        "start": ["rastreio_cognitivo", "phq9", "gad7", "mchat",
                  "sdq", "snap_iv", "qmpi", "bdi", "bai", "dass21", "ghq12"],
        "plus":  ["rastreio_cognitivo", "phq9", "gad7", "mchat",
                  "sdq", "snap_iv", "qmpi", "bdi", "bai", "dass21", "ghq12",
                  "conners_pais", "etdah_pais", "conners_prof", "etdah_prof",
                  "aq10_child", "scq", "cars",
                  "k10", "ucla", "msi_bpd", "bis11", "lsas", "hama",
                  "risco_suicidio", "agorafobia", "panico",
                  "iar", "pas", "cdi", "had", "aq10_adulto"],
        "elite": list(dict.fromkeys(MODULOS_POR_ESPECIALIDADE["neuropsicoplogo"])),
    },
    "psicopedagogo": {
        "trial": ["quest_dislexia", "checklist_dislexia", "sdq"],
        "start": ["quest_dislexia", "checklist_dislexia", "sdq",
                  "psicopedagogica", "snap_iv"],
        "plus":  ["quest_dislexia", "checklist_dislexia", "sdq",
                  "psicopedagogica", "snap_iv",
                  "conners_pais", "conners_prof", "etdah_pais", "etdah_prof",
                  "prot_dislexia_prof"],
        "elite": list(dict.fromkeys(MODULOS_POR_ESPECIALIDADE["psicopedagogo"])),
    },
    "pediatra": {
        "trial": ["mchat", "desenvolvimento"],
        "start": ["mchat", "desenvolvimento", "denver", "snap_iv", "epds"],
        "plus":  ["mchat", "desenvolvimento", "denver", "snap_iv", "epds",
                  "sono_infantil", "auqei", "iar", "pas", "cdi"],
        "elite": list(dict.fromkeys(MODULOS_POR_ESPECIALIDADE["pediatra"])),
    },
    "neuropediatra": {
        "trial": ["mchat", "desenvolvimento"],
        "start": ["mchat", "desenvolvimento", "denver", "snap_iv"],
        "plus":  ["mchat", "desenvolvimento", "denver", "snap_iv", "cars", "sensorial"],
        "elite": list(dict.fromkeys(MODULOS_POR_ESPECIALIDADE["neuropediatra"])),
    },
    "analista_aba": {
        "trial": ["mchat", "vineland3"],
        "start": ["mchat", "vineland3", "habilidades_adaptativas",
                  "ebai", "seps", "eca", "tod"],
        "plus":  list(dict.fromkeys(MODULOS_POR_ESPECIALIDADE["analista_aba"])),
        "elite": list(dict.fromkeys(MODULOS_POR_ESPECIALIDADE["analista_aba"])),
    },
    "nutricionista": {
        "trial": ["anamnese_alimentar"],
        "start": ["anamnese_alimentar", "recordatorio_alimentar",
                  "ebai", "seps", "eca"],
        "plus":  ["anamnese_alimentar", "recordatorio_alimentar", "alimentacao_seletiva",
                  "ebai", "seps", "eca"],
        "elite": ["anamnese_alimentar", "recordatorio_alimentar", "alimentacao_seletiva",
                  "ebai", "seps", "eca"],
    },
}


def get_modulos_para_plano(especialidades_codigos, plano):
    """Retorna set de códigos de módulos para o plano e especialidades dados."""
    codigos = set()
    for esp in especialidades_codigos:
        tier = MODULOS_POR_PLANO_POR_ESPECIALIDADE.get(esp, {})
        codigos.update(tier.get(plano, []))
    return codigos


# Mantido para compatibilidade com exibição no admin (baseado em TO)
MODULOS_POR_PLANO = {
    plano: MODULOS_POR_PLANO_POR_ESPECIALIDADE["terapeuta_ocupacional"][plano]
    for plano in ("start", "plus", "elite")
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
#  Proxy — aparece no sidebar do admin como "Painel de Pagamentos"
# ─────────────────────────────────────────────────────────────────────────────

# ── PHQ-9 — Patient Health Questionnaire ─────────────────────────────────────

class AvaliacaoPHQ9(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_phq9")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_total       = models.IntegerField("Pontuação Total (0–27)", null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "PHQ-9 — Questionário de Saúde do Paciente"
        ordering = ["-data"]
    def __str__(self):
        return f"PHQ-9 — {self.paciente.nome} — {self.data}"

class RespostaPHQ9(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoPHQ9, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── GAD-7 — Generalized Anxiety Disorder ─────────────────────────────────────

class AvaliacaoGAD7(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_gad7")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_total       = models.IntegerField("Pontuação Total (0–21)", null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "GAD-7 — Transtorno de Ansiedade Generalizada"
        ordering = ["-data"]
    def __str__(self):
        return f"GAD-7 — {self.paciente.nome} — {self.data}"

class RespostaGAD7(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoGAD7, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── EPDS — Edinburgh Postnatal Depression Scale ───────────────────────────────

class AvaliacaoEPDS(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_epds")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_total       = models.IntegerField("Pontuação Total (0–30)", null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "EPDS — Escala de Depressão Pós-Parto de Edinburgh"
        ordering = ["-data"]
    def __str__(self):
        return f"EPDS — {self.paciente.nome} — {self.data}"

class RespostaEPDS(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoEPDS, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── PCL-5 — PTSD Checklist for DSM-5 ─────────────────────────────────────────

class AvaliacaoPCL5(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid               = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente           = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_pcl5")
    token              = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data               = models.DateField(default=timezone.now)
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual       = models.IntegerField(default=1)
    pont_reexperiencia = models.IntegerField("Reexperiência (0–20)",       null=True, blank=True)
    pont_evitacao      = models.IntegerField("Evitação (0–8)",             null=True, blank=True)
    pont_cognicoes     = models.IntegerField("Cognições/Humor (0–28)",     null=True, blank=True)
    pont_hiperativacao = models.IntegerField("Hiperativação/React. (0–24)",null=True, blank=True)
    pont_total         = models.IntegerField("Pontuação Total (0–80)",     null=True, blank=True)
    observacoes        = models.TextField(blank=True, default="")
    email_enviado_em   = models.DateTimeField(null=True, blank=True)
    criado_em          = models.DateTimeField(auto_now_add=True)
    atualizado_em      = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "PCL-5 — Lista de Verificação de PTSD (DSM-5)"
        ordering = ["-data"]
    def __str__(self):
        return f"PCL-5 — {self.paciente.nome} — {self.data}"

class RespostaPCL5(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoPCL5, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── GHQ-12 — General Health Questionnaire ────────────────────────────────────

class AvaliacaoGHQ12(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_ghq12")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_total       = models.IntegerField("Pontuação Total (0–12)", null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "GHQ-12 — Questionário de Saúde Geral"
        ordering = ["-data"]
    def __str__(self):
        return f"GHQ-12 — {self.paciente.nome} — {self.data}"

class RespostaGHQ12(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoGHQ12, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── K-10 — Escala de Kessler ────────────────────────────────────

class AvaliacaoK10(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_k10")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_total       = models.IntegerField('Pontuação Total (10–50)', null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "K-10 — Escala de Kessler"
        ordering = ["-data"]
    def __str__(self):
        return f"K-10 — Escala de Kessler — {self.paciente.nome} — {self.data}"

class RespostaK10(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoK10, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]

# ── UCLA — Escala de Solidão ────────────────────────────────────

class AvaliacaoUCLA(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_ucla")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_total       = models.IntegerField('Pontuação Total (20–80)', null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "UCLA — Escala de Solidão"
        ordering = ["-data"]
    def __str__(self):
        return f"UCLA — Escala de Solidão — {self.paciente.nome} — {self.data}"

class RespostaUCLA(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoUCLA, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]

# ── MSI-BPD — Triagem Borderline ────────────────────────────────

class AvaliacaoMSI_BPD(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_msi_bpd")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_total       = models.IntegerField('Pontuação Total (0–10)', null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "MSI-BPD — Triagem Borderline"
        ordering = ["-data"]
    def __str__(self):
        return f"MSI-BPD — Triagem Borderline — {self.paciente.nome} — {self.data}"

class RespostaMSI_BPD(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoMSI_BPD, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]

# ── GDS-15 — Depressão Geriátrica ───────────────────────────────

class AvaliacaoGDS15(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_gds15")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_total       = models.IntegerField('Pontuação Total (0–15)', null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "GDS-15 — Depressão Geriátrica"
        ordering = ["-data"]
    def __str__(self):
        return f"GDS-15 — Depressão Geriátrica — {self.paciente.nome} — {self.data}"

class RespostaGDS15(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoGDS15, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]

# ── Rosenberg — Escala de Autoestima ────────────────────────────

class AvaliacaoRosenberg(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_rosenberg")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_total       = models.IntegerField('Pontuação Total (0–30)', null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Rosenberg — Escala de Autoestima"
        ordering = ["-data"]
    def __str__(self):
        return f"Rosenberg — Escala de Autoestima — {self.paciente.nome} — {self.data}"

class RespostaRosenberg(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoRosenberg, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]

# ── AUDIT — Uso de Álcool ───────────────────────────────────────

class AvaliacaoAUDIT(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_audit")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_total       = models.IntegerField('Pontuação Total (0–40)', null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "AUDIT — Uso de Álcool"
        ordering = ["-data"]
    def __str__(self):
        return f"AUDIT — Uso de Álcool — {self.paciente.nome} — {self.data}"

class RespostaAUDIT(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoAUDIT, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]

# ── BIS-11 — Impulsividade de Barratt ───────────────────────────

class AvaliacaoBIS11(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_bis11")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_total       = models.IntegerField('Pontuação Total (30–120)', null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "BIS-11 — Impulsividade de Barratt"
        ordering = ["-data"]
    def __str__(self):
        return f"BIS-11 — Impulsividade de Barratt — {self.paciente.nome} — {self.data}"

class RespostaBIS11(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoBIS11, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]

# ── IAR — Ansiedade Infantil ────────────────────────────────────

class AvaliacaoIAR(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_iar")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_total       = models.IntegerField('Pontuação Total (0–60)', null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "IAR — Ansiedade Infantil"
        ordering = ["-data"]
    def __str__(self):
        return f"IAR — Ansiedade Infantil — {self.paciente.nome} — {self.data}"

class RespostaIAR(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoIAR, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]

# ── PAS — Ansiedade Pré-Escolar ─────────────────────────────────

class AvaliacaoPAS(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_pas")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_total       = models.IntegerField('Pontuação Total (0–112)', null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "PAS — Ansiedade Pré-Escolar"
        ordering = ["-data"]
    def __str__(self):
        return f"PAS — Ansiedade Pré-Escolar — {self.paciente.nome} — {self.data}"

class RespostaPAS(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoPAS, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]

# ── CDI — Depressão Infantil ────────────────────────────────────

class AvaliacaoCDI(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_cdi")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_total       = models.IntegerField('Pontuação Total (0–54)', null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "CDI — Depressão Infantil"
        ordering = ["-data"]
    def __str__(self):
        return f"CDI — Depressão Infantil — {self.paciente.nome} — {self.data}"

class RespostaCDI(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoCDI, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]

# ── HAM-A — Escala de Ansiedade de Hamilton ─────────────────────

class AvaliacaoHAMA(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_hama")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_total       = models.IntegerField('Pontuação Total (0–56)', null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "HAM-A — Escala de Ansiedade de Hamilton"
        ordering = ["-data"]
    def __str__(self):
        return f"HAM-A — Escala de Ansiedade de Hamilton — {self.paciente.nome} — {self.data}"

class RespostaHAMA(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoHAMA, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]

# ── LSAS — Ansiedade Social de Liebowitz ────────────────────────

class AvaliacaoLSAS(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_lsas")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_total       = models.IntegerField('Pontuação Total (0–72)', null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "LSAS — Ansiedade Social de Liebowitz"
        ordering = ["-data"]
    def __str__(self):
        return f"LSAS — Ansiedade Social de Liebowitz — {self.paciente.nome} — {self.data}"

class RespostaLSAS(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoLSAS, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]

# ── Triagem de Risco de Suicídio ────────────────────────────────

class AvaliacaoRiscoSuicidio(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_risco_suicidio")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_total       = models.IntegerField('Pontuação Total (0–10)', null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Triagem de Risco de Suicídio"
        ordering = ["-data"]
    def __str__(self):
        return f"Triagem de Risco de Suicídio — {self.paciente.nome} — {self.data}"

class RespostaRiscoSuicidio(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoRiscoSuicidio, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]

# ── Rastreio de Agorafobia ──────────────────────────────────────

class AvaliacaoAgorafobia(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_agorafobia")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_total       = models.IntegerField('Pontuação Total (0–56)', null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Rastreio de Agorafobia"
        ordering = ["-data"]
    def __str__(self):
        return f"Rastreio de Agorafobia — {self.paciente.nome} — {self.data}"

class RespostaAgorafobia(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoAgorafobia, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]

# ── Rastreio de Transtorno de Pânico ────────────────────────────

class AvaliacaoPanico(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_panico")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_total       = models.IntegerField('Pontuação Total (0–39)', null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Rastreio de Transtorno de Pânico"
        ordering = ["-data"]
    def __str__(self):
        return f"Rastreio de Transtorno de Pânico — {self.paciente.nome} — {self.data}"

class RespostaPanico(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoPanico, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]

# ── EBAI — Escala Brasileira de Alimentação Infantil ─────────────────────────

class AvaliacaoEBAI(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente         = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_ebai")
    token            = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data             = models.DateField(default=timezone.now)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual     = models.IntegerField(default=1)
    pont_bruto       = models.IntegerField("Pontuação Bruta (14–98)", null=True, blank=True)
    escore_t         = models.IntegerField("Escore T", null=True, blank=True)
    observacoes      = models.TextField(blank=True, default="")
    email_enviado_em = models.DateTimeField(null=True, blank=True)
    criado_em        = models.DateTimeField(auto_now_add=True)
    atualizado_em    = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "EBAI — Escala Brasileira de Alimentação Infantil"
        ordering = ["-data"]
    def __str__(self):
        return f"EBAI — {self.paciente.nome} — {self.data}"

class RespostaEBAI(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoEBAI, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── SEPS — Escala de Problemas Sensoriais na Alimentação ──────────────────────

class AvaliacaoSEPS(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid               = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente           = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_seps")
    token              = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data               = models.DateField(default=timezone.now)
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual       = models.IntegerField(default=1)
    pont_aversao_toque = models.IntegerField("Aversão ao toque da comida (0–16)", null=True, blank=True)
    pont_foco_unica    = models.IntegerField("Foco numa única comida (0–16)", null=True, blank=True)
    pont_vomito        = models.IntegerField("Vômito (0–16)", null=True, blank=True)
    pont_sensib_temp   = models.IntegerField("Sensibilidade à temperatura (0–16)", null=True, blank=True)
    pont_expulsao      = models.IntegerField("Expulsão (0–12)", null=True, blank=True)
    pont_encher        = models.IntegerField("Encher demasiado (0–12)", null=True, blank=True)
    observacoes        = models.TextField(blank=True, default="")
    email_enviado_em   = models.DateTimeField(null=True, blank=True)
    criado_em          = models.DateTimeField(auto_now_add=True)
    atualizado_em      = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "SEPS — Escala de Problemas Sensoriais na Alimentação"
        ordering = ["-data"]
    def __str__(self):
        return f"SEPS — {self.paciente.nome} — {self.data}"

class RespostaSEPS(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoSEPS, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── ECA — Escala de Avaliação do Comportamento Alimentar ──────────────────────

class AvaliacaoECA(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid               = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente           = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_eca")
    token              = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data               = models.DateField(default=timezone.now)
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual       = models.IntegerField(default=1)
    pont_mastigacao    = models.IntegerField("Motricidade na Mastigação", null=True, blank=True)
    pont_seletividade  = models.IntegerField("Seletividade Alimentar", null=True, blank=True)
    pont_comportamental= models.IntegerField("Aspectos Comportamentais", null=True, blank=True)
    pont_gi            = models.IntegerField("Sintomas Gastrointestinais", null=True, blank=True)
    pont_sensorial     = models.IntegerField("Sensibilidade Sensorial", null=True, blank=True)
    pont_habilidades   = models.IntegerField("Habilidades nas Refeições", null=True, blank=True)
    observacoes        = models.TextField(blank=True, default="")
    email_enviado_em   = models.DateTimeField(null=True, blank=True)
    criado_em          = models.DateTimeField(auto_now_add=True)
    atualizado_em      = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "ECA — Escala de Avaliação do Comportamento Alimentar"
        ordering = ["-data"]
    def __str__(self):
        return f"ECA — {self.paciente.nome} — {self.data}"

class RespostaECA(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoECA, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ── TOD — Escala de Avaliação de Comportamentos Disruptivos ───────────────────

class AvaliacaoTOD(models.Model):
    STATUS_CHOICES = [("em_andamento", "Em andamento"), ("concluida", "Concluída")]
    uuid                  = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente              = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="avaliacoes_tod")
    token                 = models.CharField(max_length=64, unique=True, blank=True, null=True)
    data                  = models.DateField(default=timezone.now)
    status                = models.CharField(max_length=20, choices=STATUS_CHOICES, default="em_andamento")
    pagina_atual          = models.IntegerField(default=1)
    pont_total            = models.IntegerField("Pontuação Total (0–135)", null=True, blank=True)
    itens_corte_positivos = models.IntegerField("Itens de corte positivos (≥2)", null=True, blank=True)
    observacoes           = models.TextField(blank=True, default="")
    email_enviado_em      = models.DateTimeField(null=True, blank=True)
    criado_em             = models.DateTimeField(auto_now_add=True)
    atualizado_em         = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "TOD — Escala de Avaliação de Comportamentos Disruptivos"
        ordering = ["-data"]
    def __str__(self):
        return f"TOD — {self.paciente.nome} — {self.data}"

class RespostaTOD(models.Model):
    avaliacao   = models.ForeignKey(AvaliacaoTOD, on_delete=models.CASCADE, related_name="respostas")
    numero_item = models.IntegerField()
    valor       = models.IntegerField()
    observacao  = models.TextField(blank=True, default="")
    class Meta:
        unique_together = ("avaliacao", "numero_item")
        ordering = ["numero_item"]


# ─────────────────────────────────────────────────────────────────────────────

class PainelPagamentos(SolicitacaoPlano):
    """Proxy de SolicitacaoPlano — usado apenas para expor o Painel no admin."""

    class Meta:
        proxy        = True
        verbose_name        = "Painel de Pagamentos"
        verbose_name_plural = "Painel de Pagamentos"


class PainelRecebimento(SolicitacaoPlano):
    """Proxy de SolicitacaoPlano — usado apenas para expor o Painel de Recebimento no admin."""

    class Meta:
        proxy               = True
        verbose_name        = "Painel de Recebimento"
        verbose_name_plural = "Painel de Recebimento"


class PageVisit(models.Model):
    PAGINA_CHOICES = [
        ("landing",      "Landing Page (/)"),
        ("login",        "Login (/login/)"),
        ("cadastro",     "Cadastro (/registrar/)"),
        ("instrumentos", "Instrumentos (/instrumentos/)"),
        ("privacidade",  "Privacidade (/privacidade/)"),
        ("contato",      "Contato (/contato/)"),
        ("planos",       "Planos (/planos/)"),
    ]

    pagina      = models.CharField(max_length=20, choices=PAGINA_CHOICES)
    ip          = models.GenericIPAddressField(null=True, blank=True)
    user_agent  = models.TextField(blank=True, default="")
    referrer    = models.URLField(max_length=500, blank=True, default="")
    visitado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering            = ["-visitado_em"]
        verbose_name        = "Visita de Página"
        verbose_name_plural = "Visitas de Páginas"

    def __str__(self):
        return f"{self.get_pagina_display()} — {self.visitado_em:%d/%m/%Y %H:%M}"


class StatusIncident(models.Model):
    IMPACT_CHOICES = [
        ("none",        "Sem Impacto"),
        ("minor",       "Impacto Menor"),
        ("major",       "Impacto Maior"),
        ("critical",    "Crítico"),
        ("maintenance", "Manutenção Programada"),
    ]
    STATUS_CHOICES = [
        ("investigating", "Investigando"),
        ("identified",    "Identificado"),
        ("monitoring",    "Monitorando"),
        ("resolved",      "Resolvido"),
        ("scheduled",     "Agendado"),
        ("in_progress",   "Em Andamento"),
        ("completed",     "Concluído"),
    ]

    titulo      = models.CharField(max_length=200)
    descricao   = models.TextField()
    impacto     = models.CharField(max_length=20, choices=IMPACT_CHOICES, default="minor")
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default="investigating")
    iniciado_em = models.DateTimeField(default=timezone.now)
    resolvido_em = models.DateTimeField(null=True, blank=True)
    criado_em   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering            = ["-iniciado_em"]
        verbose_name        = "Incidente / Manutenção"
        verbose_name_plural = "Incidentes / Manutenções"

    def __str__(self):
        return f"[{self.get_status_display()}] {self.titulo}"

    @property
    def ativo(self):
        return self.status not in ("resolved", "completed")
