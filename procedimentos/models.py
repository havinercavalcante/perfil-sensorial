import uuid
from django.db import models
from django.utils import timezone
from questionario.models import Paciente


class ProcedimentoDocumento(models.Model):
    TIPO_CHOICES = [
        # Anamneses
        ("anamnese",          "Anamnese Geral"),
        ("anamnese_adulto",   "Anamnese — Adulto"),
        ("anamnese_infantil", "Anamnese — Infantil / Adolescente"),
        ("anamnese_tea",      "Anamnese — TEA / Autismo"),
        ("anamnese_tdah",     "Anamnese — TDAH"),
        ("anamnese_casal",    "Anamnese — Casal"),
        ("anamnese_seletividade_alimentar", "Anamnese — Seletividade Alimentar"),
        # Prontuário longitudinal
        ("evolucao_semanal",     "Evolução de Atendimento"),
        ("ficha_visita_escolar", "Ficha de Visita Escolar"),
        # Outros procedimentos
        ("ficha_triagem",        "Ficha de Triagem"),
        ("carta_encaminhamento", "Carta de Encaminhamento"),
        ("atestado",             "Atestado"),
        ("relatorio",            "Relatório"),
    ]

    TIPOS_ANAMNESE = [
        "anamnese", "anamnese_adulto", "anamnese_infantil",
        "anamnese_tea", "anamnese_tdah", "anamnese_casal",
    ]

    uuid         = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    paciente     = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="procedimentos")
    tipo         = models.CharField(max_length=40, choices=TIPO_CHOICES)
    titulo       = models.CharField("Título", max_length=200, blank=True)
    conteudo     = models.JSONField(default=dict)
    data         = models.DateField("Data do registro", default=timezone.now)
    token_publico = models.UUIDField(null=True, blank=True, unique=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_em    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Procedimento / Documento"
        verbose_name_plural = "Procedimentos / Documentos"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.paciente.nome} — {self.criado_em:%d/%m/%Y}"

    @property
    def titulo_display(self):
        return self.titulo or self.criado_em.strftime("%d/%m/%Y %H:%M")
