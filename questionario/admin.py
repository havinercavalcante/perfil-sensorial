from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import (
    Paciente, Avaliacao, Resposta, PerfilMedico, ModuloAvaliacao,
    Especialidade, MODULOS_POR_ESPECIALIDADE, HistoricoLogin,
)


# ── Inline do perfil no User admin ───────────────────────────────────────────

class PerfilInline(admin.StackedInline):
    model = PerfilMedico
    can_delete = False
    verbose_name_plural = "Perfil e Módulos Liberados"
    filter_horizontal = ("especialidades", "modulos_liberados",)
    fields = ("registro_profissional", "especialidades", "telefone", "plano", "trial_inicio", "modulos_liberados")

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "modulos_liberados":
            user_id = request.resolver_match.kwargs.get("object_id")
            if user_id:
                try:
                    perfil = PerfilMedico.objects.get(user_id=user_id)
                    codigos_esp = list(perfil.especialidades.values_list("codigo", flat=True))
                    codigos_modulos = set()
                    for cod in codigos_esp:
                        codigos_modulos.update(MODULOS_POR_ESPECIALIDADE.get(cod, []))
                    if codigos_modulos:
                        kwargs["queryset"] = ModuloAvaliacao.objects.filter(
                            codigo__in=codigos_modulos
                        ).order_by("nome")
                except PerfilMedico.DoesNotExist:
                    pass
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class CustomUserAdmin(UserAdmin):
    inlines = [PerfilInline]
    list_display = UserAdmin.list_display + ("get_plano",)
    list_filter = UserAdmin.list_filter + ("perfil__plano",)

    @admin.display(description="Plano", ordering="perfil__plano")
    def get_plano(self, obj):
        try:
            return obj.perfil.get_plano_display()
        except Exception:
            return "—"


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ── Especialidade ─────────────────────────────────────────────────────────────

@admin.register(Especialidade)
class EspecialidadeAdmin(admin.ModelAdmin):
    list_display = ["codigo", "nome", "total_profissionais"]
    ordering = ["nome"]

    def total_profissionais(self, obj):
        return obj.profissionais.count()
    total_profissionais.short_description = "Profissionais"


# ── Paciente ──────────────────────────────────────────────────────────────────

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ["nome", "medico", "data_nascimento", "responsavel"]
    list_filter = ["medico"]
    search_fields = ["nome", "responsavel", "medico__username"]


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ["paciente", "get_profissional", "data", "status", "pont_ex", "pont_ev", "pont_sn", "pont_ob"]
    list_filter = ["status", "paciente__medico"]
    search_fields = ["paciente__nome", "paciente__medico__username", "paciente__medico__first_name", "paciente__medico__last_name"]

    @admin.display(description="Profissional", ordering="paciente__medico__first_name")
    def get_profissional(self, obj):
        return obj.paciente.medico.get_full_name() or obj.paciente.medico.username


@admin.register(ModuloAvaliacao)
class ModuloAvaliacaoAdmin(admin.ModelAdmin):
    list_display = ["codigo", "nome", "descricao", "total_medicos"]
    search_fields = ["codigo", "nome"]
    ordering = ["nome"]

    def total_medicos(self, obj):
        return obj.medicos.count()
    total_medicos.short_description = "Médicos com acesso"


# ── PerfilMedico ──────────────────────────────────────────────────────────────

@admin.register(PerfilMedico)
class PerfilMedicoAdmin(admin.ModelAdmin):
    list_display  = ["user", "registro_profissional", "especialidades_resumo", "modulos_resumo"]
    filter_horizontal = ("especialidades", "modulos_liberados",)
    search_fields = ["user__username", "user__first_name", "user__last_name"]

    def especialidades_resumo(self, obj):
        nomes = list(obj.especialidades.values_list("nome", flat=True))
        return ", ".join(nomes) if nomes else "—"
    especialidades_resumo.short_description = "Especialidades"

    def modulos_resumo(self, obj):
        nomes = list(obj.modulos_liberados.values_list("nome", flat=True))
        return ", ".join(nomes) if nomes else "— nenhum —"
    modulos_resumo.short_description = "Módulos liberados"

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Filtra modulos_liberados de acordo com as especialidades do profissional."""
        if db_field.name == "modulos_liberados":
            obj_id = request.resolver_match.kwargs.get("object_id")
            if obj_id:
                try:
                    perfil = PerfilMedico.objects.get(pk=obj_id)
                    codigos_esp = list(perfil.especialidades.values_list("codigo", flat=True))
                    codigos_modulos = set()
                    for cod in codigos_esp:
                        codigos_modulos.update(MODULOS_POR_ESPECIALIDADE.get(cod, []))
                    if codigos_modulos:
                        kwargs["queryset"] = ModuloAvaliacao.objects.filter(
                            codigo__in=codigos_modulos
                        ).order_by("nome")
                except PerfilMedico.DoesNotExist:
                    pass
        return super().formfield_for_manytomany(db_field, request, **kwargs)


# ── Histórico de Logins ───────────────────────────────────────────────────────

@admin.register(HistoricoLogin)
class HistoricoLoginAdmin(admin.ModelAdmin):
    list_display  = ["data_hora", "user", "ip", "dispositivo", "status_icon"]
    list_filter   = ["sucesso", "user"]
    search_fields = ["user__username", "user__first_name", "ip", "dispositivo"]
    readonly_fields = ["user", "ip", "dispositivo", "user_agent", "sucesso", "data_hora"]
    ordering      = ["-data_hora"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def status_icon(self, obj):
        return "✓ Sucesso" if obj.sucesso else "✗ Falha"
    status_icon.short_description = "Status"
