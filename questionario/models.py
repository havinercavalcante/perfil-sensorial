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
