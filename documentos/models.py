from django.db import models
from django.contrib.auth.models import User
from questionario.models import Especialidade

PLANO_ORDEM = {"trial": 0, "start": 1, "plus": 2, "elite": 3}


class CategoriaDocumento(models.Model):
    nome   = models.CharField("Nome", max_length=80)
    codigo = models.SlugField("Código", max_length=40, unique=True)
    icone  = models.CharField("Ícone Lucide", max_length=40, default="file-text",
                              help_text="Nome do ícone Lucide (ex: file-text, clipboard, file-check)")
    ordem  = models.PositiveSmallIntegerField("Ordem", default=0)

    class Meta:
        verbose_name        = "Categoria de Documento"
        verbose_name_plural = "Categorias de Documentos"
        ordering            = ["ordem", "nome"]

    def __str__(self):
        return self.nome


class Documento(models.Model):
    PLANO_CHOICES = [
        ("start", "START"),
        ("plus",  "PLUS"),
        ("elite", "ELITE"),
    ]

    titulo        = models.CharField("Título", max_length=200)
    descricao     = models.TextField("Descrição", blank=True)
    categoria     = models.ForeignKey(
        CategoriaDocumento, on_delete=models.PROTECT,
        verbose_name="Categoria", related_name="documentos"
    )
    arquivo       = models.FileField(
        "Arquivo", upload_to="documentos/", max_length=500,
        help_text="Formatos aceitos: PDF, DOCX, DOC"
    )
    especialidades = models.ManyToManyField(
        Especialidade, blank=True,
        verbose_name="Especialidades",
        help_text="Deixe vazio para disponibilizar para TODAS as especialidades"
    )
    plano_minimo  = models.CharField(
        "Plano mínimo", max_length=10, choices=PLANO_CHOICES, default="start"
    )
    ativo         = models.BooleanField("Ativo", default=True)
    criado_em     = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        verbose_name        = "Documento"
        verbose_name_plural = "Documentos"
        ordering            = ["categoria__ordem", "titulo"]

    def __str__(self):
        return self.titulo

    @property
    def extensao(self):
        nome = self.arquivo.name or ""
        return nome.rsplit(".", 1)[-1].lower() if "." in nome else ""

    @property
    def eh_pdf(self):
        return self.extensao == "pdf"

    def usuario_tem_acesso(self, perfil):
        """Retorna True se o perfil do profissional tem acesso a este documento."""
        if not perfil.plano_ativo:
            return False
        ordem_usuario = PLANO_ORDEM.get(perfil.plano, 0)
        ordem_doc     = PLANO_ORDEM.get(self.plano_minimo, 1)
        if ordem_usuario < ordem_doc:
            return False
        # Verifica especialidade: se doc não tem restrição, libera para todos
        if self.especialidades.exists():
            especialidades_usuario = perfil.especialidades.values_list("codigo", flat=True)
            especialidades_doc     = self.especialidades.values_list("codigo", flat=True)
            if not set(especialidades_usuario) & set(especialidades_doc):
                return False
        return True


class DownloadDocumento(models.Model):
    documento  = models.ForeignKey(Documento, on_delete=models.CASCADE,
                                   verbose_name="Documento", related_name="downloads")
    user       = models.ForeignKey(User, on_delete=models.CASCADE,
                                   verbose_name="Profissional", related_name="downloads_doc")
    baixado_em = models.DateTimeField("Baixado em", auto_now_add=True)

    class Meta:
        verbose_name        = "Download de Documento"
        verbose_name_plural = "Downloads de Documentos"
        ordering            = ["-baixado_em"]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} — {self.documento.titulo}"
