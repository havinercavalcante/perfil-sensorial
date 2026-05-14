from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import (
    Paciente, Avaliacao, Resposta, PerfilMedico, ModuloAvaliacao,
)


class PerfilInline(admin.StackedInline):
    model = PerfilMedico
    can_delete = False
    verbose_name_plural = "Perfil e Módulos Liberados"
    filter_horizontal = ("modulos_liberados",)
    fields = ("registro_profissional", "especialidade", "telefone", "modulos_liberados")


class CustomUserAdmin(UserAdmin):
    inlines = [PerfilInline]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ["nome", "medico", "data_nascimento", "responsavel"]
    list_filter = ["medico"]
    search_fields = ["nome", "responsavel", "medico__username"]


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ["paciente", "data", "status", "pont_ex", "pont_ev", "pont_sn", "pont_ob"]
    list_filter = ["status", "paciente__medico"]


@admin.register(ModuloAvaliacao)
class ModuloAvaliacaoAdmin(admin.ModelAdmin):
    list_display = ["codigo", "nome", "descricao", "total_medicos"]
    search_fields = ["codigo", "nome"]
    ordering = ["nome"]

    def total_medicos(self, obj):
        return obj.medicos.count()
    total_medicos.short_description = "Médicos com acesso"


@admin.register(PerfilMedico)
class PerfilMedicoAdmin(admin.ModelAdmin):
    list_display = ["user", "registro_profissional", "especialidade", "modulos_resumo"]
    filter_horizontal = ("modulos_liberados",)
    search_fields = ["user__username", "user__first_name", "user__last_name"]

    def modulos_resumo(self, obj):
        nomes = list(obj.modulos_liberados.values_list("nome", flat=True))
        if not nomes:
            return "— nenhum —"
        return ", ".join(nomes)
    modulos_resumo.short_description = "Módulos liberados"
