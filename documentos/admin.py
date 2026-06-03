from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import CategoriaDocumento, Documento, DownloadDocumento


@admin.register(CategoriaDocumento)
class CategoriaDocumentoAdmin(admin.ModelAdmin):
    list_display  = ("nome", "codigo", "icone", "ordem", "total_docs")
    list_editable = ("ordem",)
    prepopulated_fields = {"codigo": ("nome",)}

    def total_docs(self, obj):
        return obj.documentos.filter(ativo=True).count()
    total_docs.short_description = "Documentos ativos"


class EspecialidadeFilter(admin.SimpleListFilter):
    title        = "Especialidade"
    parameter_name = "especialidade"

    def lookups(self, request, model_admin):
        from questionario.models import Especialidade
        return [(e.codigo, e.nome) for e in Especialidade.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(especialidades__codigo=self.value())
        return queryset


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display   = ("titulo", "categoria", "plano_minimo", "especialidades_display",
                      "extensao_badge", "ativo", "criado_em", "total_downloads")
    list_filter    = ("ativo", "categoria", "plano_minimo", EspecialidadeFilter)
    search_fields  = ("titulo", "descricao")
    filter_horizontal = ("especialidades",)
    readonly_fields = ("criado_em", "total_downloads")
    list_editable  = ("ativo",)

    fieldsets = (
        (None, {
            "fields": ("titulo", "descricao", "categoria", "arquivo")
        }),
        ("Controle de Acesso", {
            "fields": ("plano_minimo", "especialidades"),
            "description": "Deixe Especialidades vazio para liberar para todos os profissionais."
        }),
        ("Status", {
            "fields": ("ativo", "criado_em", "total_downloads")
        }),
    )

    def especialidades_display(self, obj):
        espec = obj.especialidades.all()
        if not espec.exists():
            return mark_safe('<span style="color:#6b7280;font-size:.8rem">Todas</span>')
        nomes = ", ".join(e.nome for e in espec[:3])
        if espec.count() > 3:
            nomes += f" +{espec.count() - 3}"
        return nomes
    especialidades_display.short_description = "Especialidades"

    def extensao_badge(self, obj):
        ext = obj.extensao.upper()
        cor = "#2563eb" if ext == "PDF" else "#059669"
        return format_html(
            '<span style="background:{};color:#fff;padding:1px 8px;'
            'border-radius:10px;font-size:.75rem;font-weight:700">{}</span>',
            cor, ext or "—"
        )
    extensao_badge.short_description = "Tipo"

    def total_downloads(self, obj):
        return obj.downloads.count()
    total_downloads.short_description = "Downloads"


@admin.register(DownloadDocumento)
class DownloadDocumentoAdmin(admin.ModelAdmin):
    list_display  = ("documento", "user", "baixado_em")
    list_filter   = ("documento__categoria",)
    search_fields = ("documento__titulo", "user__first_name", "user__last_name", "user__email")
    readonly_fields = ("documento", "user", "baixado_em")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
