from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.utils.html import format_html
from .models import (
    Paciente, Avaliacao, Resposta, PerfilMedico, ModuloAvaliacao,
    Especialidade, MODULOS_POR_ESPECIALIDADE, HistoricoLogin,
    SolicitacaoPlano, MODULOS_POR_PLANO,
)


# ── Helper compartilhado: badge de validade ───────────────────────────────────

def _validade_badge(perfil):
    """Retorna HTML colorido com dias restantes do trial ou plano pago."""
    p = perfil

    # Plano pago com data de expiração
    if p.plano != "trial" and p.plano_expiracao:
        dias = p.plano_dias_restantes
        if dias <= 0:
            return format_html(
                '<span style="background:#fef2f2;color:#dc2626;padding:2px 7px;'
                'border-radius:4px;font-size:.78rem;font-weight:700;">⛔ Vencido</span>'
            )
        elif dias <= 3:
            return format_html(
                '<span style="background:#fef2f2;color:#dc2626;padding:2px 7px;'
                'border-radius:4px;font-size:.78rem;font-weight:700;">'
                '🔴 {} dias<br/><small style="font-weight:400">{}</small></span>',
                dias, p.plano_expiracao.strftime("%d/%m/%Y")
            )
        elif dias <= 7:
            return format_html(
                '<span style="background:#fffbeb;color:#d97706;padding:2px 7px;'
                'border-radius:4px;font-size:.78rem;font-weight:700;">'
                '🟡 {} dias<br/><small style="font-weight:400">{}</small></span>',
                dias, p.plano_expiracao.strftime("%d/%m/%Y")
            )
        else:
            return format_html(
                '<span style="background:#ecfdf5;color:#059669;padding:2px 7px;'
                'border-radius:4px;font-size:.78rem;font-weight:700;">'
                '🟢 {} dias<br/><small style="font-weight:400">{}</small></span>',
                dias, p.plano_expiracao.strftime("%d/%m/%Y")
            )

    # Plano pago sem data de expiração
    if p.plano != "trial" and not p.plano_expiracao:
        return format_html(
            '<span style="color:#10b981;font-weight:600;font-size:.8rem;">✅ Ativo</span>'
        )

    # Trial
    if p.trial_inicio is None:
        return format_html('<span style="color:#aaa;font-size:.8rem;">sem data</span>')
    dias = p.trial_dias_restantes
    if dias <= 0:
        return format_html(
            '<span style="background:#fef2f2;color:#dc2626;padding:2px 7px;'
            'border-radius:4px;font-size:.78rem;font-weight:700;">⛔ Trial expirado</span>'
        )
    elif dias <= 2:
        cor, bg = "#dc2626", "#fef2f2"
    elif dias <= 4:
        cor, bg = "#d97706", "#fffbeb"
    else:
        cor, bg = "#059669", "#ecfdf5"
    return format_html(
        '<span style="background:{};color:{};padding:2px 7px;border-radius:4px;'
        'font-size:.78rem;font-weight:700;">⏳ {} dia{}</span>',
        bg, cor, dias, "s" if dias != 1 else ""
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
    inlines        = [PerfilInline]
    list_display   = ("username", "email", "get_nome_completo", "get_plano_badge", "get_trial_dias", "get_pacientes", "get_ultimo_acesso", "is_active")
    list_filter    = UserAdmin.list_filter + ("perfil__plano",)
    search_fields  = ("username", "email", "first_name", "last_name")
    ordering       = ("-date_joined",)

    @admin.display(description="Nome")
    def get_nome_completo(self, obj):
        return obj.get_full_name() or "—"

    @admin.display(description="Plano", ordering="perfil__plano")
    def get_plano_badge(self, obj):
        try:
            p = obj.perfil
        except Exception:
            return format_html('<span style="color:#aaa">—</span>')
        cores = {
            "trial": "#6366f1",
            "start": "#3b82f6",
            "plus":  "#8b5cf6",
            "elite": "#0c3c7b",
        }
        cor = cores.get(p.plano, "#888")
        label = p.get_plano_display()
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 9px;border-radius:5px;font-size:0.78rem;font-weight:700;">{}</span>',
            cor, label
        )
    get_plano_badge.short_description = "Plano"

    @admin.display(description="Validade")
    def get_trial_dias(self, obj):
        try:
            p = obj.perfil
        except Exception:
            return "—"
        return _validade_badge(p)
    get_trial_dias.short_description = "Validade"

    @admin.display(description="Pacientes")
    def get_pacientes(self, obj):
        total = obj.pacientes.count()
        return format_html('<span style="font-weight:700;color:#0c3c7b">{}</span>', total)

    @admin.display(description="Último acesso", ordering="last_login")
    def get_ultimo_acesso(self, obj):
        if not obj.last_login:
            return "—"
        delta = timezone.now() - obj.last_login
        if delta.days == 0:
            return format_html('<span style="color:#10b981;font-size:.8rem;">Hoje</span>')
        elif delta.days == 1:
            return format_html('<span style="color:#3b82f6;font-size:.8rem;">Ontem</span>')
        elif delta.days <= 7:
            return format_html('<span style="color:#6366f1;font-size:.8rem;">{}d atrás</span>', delta.days)
        else:
            return format_html('<span style="color:#aaa;font-size:.8rem;">{}</span>', obj.last_login.strftime("%d/%m/%Y"))


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
    list_display      = ["usuario_info", "plano_badge", "trial_status", "especialidades_resumo", "modulos_count", "pacientes_count"]
    list_filter       = ["plano", "especialidades"]
    filter_horizontal = ("especialidades", "modulos_liberados",)
    search_fields     = ["user__username", "user__first_name", "user__last_name", "user__email"]
    ordering          = ["-user__date_joined"]
    readonly_fields   = ["trial_info_display", "modulos_do_plano_display"]
    fieldsets = (
        ("Profissional", {
            "fields": ("user", "registro_profissional", "especialidades", "telefone"),
        }),
        ("Plano e Acesso", {
            "fields": ("plano", "trial_inicio", "trial_info_display"),
        }),
        ("Módulos", {
            "fields": ("modulos_do_plano_display", "modulos_liberados"),
            "description": "Os módulos abaixo correspondem ao plano atual. Você pode adicionar módulos extras manualmente.",
        }),
    )

    # ── list_display ──────────────────────────────────────────────────────────

    @admin.display(description="Profissional")
    def usuario_info(self, obj):
        nome  = obj.user.get_full_name() or obj.user.username
        email = obj.user.email
        return format_html(
            '<strong style="color:#0c3c7b">{}</strong><br/>'
            '<small style="color:#6b7280">{}</small>',
            nome, email
        )

    @admin.display(description="Plano", ordering="plano")
    def plano_badge(self, obj):
        cores = {"trial": "#6366f1", "start": "#3b82f6", "plus": "#8b5cf6", "elite": "#0c3c7b"}
        cor   = cores.get(obj.plano, "#888")
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:5px;font-size:.8rem;font-weight:700;">{}</span>',
            cor, obj.get_plano_display()
        )

    @admin.display(description="Validade")
    def trial_status(self, obj):
        return _validade_badge(obj)

    @admin.display(description="Especialidades")
    def especialidades_resumo(self, obj):
        nomes = list(obj.especialidades.values_list("nome", flat=True))
        if not nomes:
            return format_html('<span style="color:#aaa">—</span>')
        return format_html(
            "{}",
            ", ".join(nomes)
        )

    @admin.display(description="Módulos")
    def modulos_count(self, obj):
        total = obj.modulos_liberados.count()
        return format_html(
            '<span style="font-weight:700;color:#0c3c7b">{}</span>'
            '<span style="color:#aaa;font-size:.78rem"> / 27</span>',
            total
        )

    @admin.display(description="Pacientes")
    def pacientes_count(self, obj):
        total = obj.user.pacientes.count()
        return format_html('<span style="font-weight:700;color:#0c3c7b">{}</span>', total)

    # ── readonly fields ───────────────────────────────────────────────────────

    @admin.display(description="Validade do plano")
    def trial_info_display(self, obj):
        # Plano pago com data de expiração
        if obj.plano != "trial" and obj.plano_expiracao:
            dias = obj.plano_dias_restantes
            if dias <= 0:
                return format_html(
                    '<strong style="color:#dc2626">⛔ Plano vencido</strong> em {}',
                    obj.plano_expiracao.strftime("%d/%m/%Y")
                )
            return format_html(
                '<strong style="color:#059669">✅ {} dia{} restante{}</strong> — vence em {}',
                dias, "s" if dias != 1 else "", "s" if dias != 1 else "",
                obj.plano_expiracao.strftime("%d/%m/%Y")
            )
        # Plano pago sem vencimento definido
        if obj.plano != "trial" and not obj.plano_expiracao:
            return format_html('<strong style="color:#10b981;">✅ Plano ativo</strong> — sem data de vencimento (aprovado manualmente)')
        # Trial
        if obj.trial_inicio is None:
            return "—"
        dias = obj.trial_dias_restantes
        expira = obj.trial_inicio + timezone.timedelta(days=7)
        if dias <= 0:
            return format_html(
                '<strong style="color:#dc2626">⛔ Trial expirado</strong> em {}',
                expira.strftime("%d/%m/%Y %H:%M")
            )
        return format_html(
            '<strong style="color:#6366f1">⏳ {} dia{} de trial restante{}</strong> — expira em {}',
            dias, "s" if dias != 1 else "", "s" if dias != 1 else "",
            expira.strftime("%d/%m/%Y")
        )

    @admin.display(description="Módulos do plano atual")
    def modulos_do_plano_display(self, obj):
        codigos = MODULOS_POR_PLANO.get(obj.plano, [])
        if not codigos:
            return "—"
        nomes = list(ModuloAvaliacao.objects.filter(codigo__in=codigos).values_list("nome", flat=True))
        tags = "".join(
            f'<span style="display:inline-block;background:#d5eef5;color:#0c3c7b;'
            f'border:1px solid #85cde2;padding:2px 8px;border-radius:5px;'
            f'font-size:.75rem;font-weight:600;margin:2px;">{n}</span>'
            for n in sorted(nomes)
        )
        return format_html(tags)

    # ── formfield ─────────────────────────────────────────────────────────────

    def formfield_for_manytomany(self, db_field, request, **kwargs):
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


# ── Solicitações de Plano ─────────────────────────────────────────────────────

def _aprovar_solicitacoes(modeladmin, request, queryset):
    """Ação admin: aprovar solicitações selecionadas, ativar plano e definir vencimento."""
    aprovados = 0
    agora = timezone.now()
    for sol in queryset.filter(status="pendente"):
        sol.status       = "aprovado"
        sol.aprovado_por = request.user
        sol.aprovado_em  = agora
        sol.save()

        perfil, _ = PerfilMedico.objects.get_or_create(user=sol.user)
        perfil.plano = sol.plano
        # Renova vencimento: +30 dias
        if perfil.plano_expiracao and perfil.plano_expiracao > agora:
            perfil.plano_expiracao = perfil.plano_expiracao + timezone.timedelta(days=30)
        else:
            perfil.plano_expiracao = agora + timezone.timedelta(days=30)
        if not perfil.user.is_active:
            perfil.user.is_active = True
            perfil.user.save(update_fields=["is_active"])
        perfil.save(update_fields=["plano", "plano_expiracao"])
        codigos = MODULOS_POR_PLANO.get(sol.plano, [])
        perfil.modulos_liberados.set(ModuloAvaliacao.objects.filter(codigo__in=codigos))
        aprovados += 1

    modeladmin.message_user(request, f"{aprovados} plano(s) ativado(s) com vencimento em 30 dias.")

_aprovar_solicitacoes.short_description = "✅ Aprovar e ativar plano"


@admin.register(SolicitacaoPlano)
class SolicitacaoPlanoAdmin(admin.ModelAdmin):
    list_display   = ["criado_em_fmt", "usuario_link", "plano_badge", "status_badge", "observacoes_resumo", "aprovado_por", "aprovado_em_fmt"]
    list_filter    = ["status", "plano"]
    search_fields  = ["user__username", "user__first_name", "user__last_name", "user__email"]
    readonly_fields = ["user", "plano", "observacoes", "criado_em", "aprovado_por", "aprovado_em"]
    ordering       = ["-criado_em"]
    actions        = [_aprovar_solicitacoes]

    @admin.display(description="Solicitado em", ordering="criado_em")
    def criado_em_fmt(self, obj):
        return obj.criado_em.strftime("%d/%m/%Y %H:%M") if obj.criado_em else "—"

    @admin.display(description="Aprovado em", ordering="aprovado_em")
    def aprovado_em_fmt(self, obj):
        return obj.aprovado_em.strftime("%d/%m/%Y %H:%M") if obj.aprovado_em else "—"

    @admin.display(description="Usuário")
    def usuario_link(self, obj):
        nome = obj.user.get_full_name() or obj.user.username
        return format_html('<strong>{}</strong><br/><small style="color:#666">{}</small>', nome, obj.user.email)

    @admin.display(description="Plano")
    def plano_badge(self, obj):
        cores = {"start": "#3b82f6", "plus": "#8b5cf6", "elite": "#0c3c7b"}
        cor = cores.get(obj.plano, "#888")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:0.8rem;font-weight:700;">{}</span>',
            cor, obj.get_plano_display()
        )

    @admin.display(description="Status")
    def status_badge(self, obj):
        cfg = {
            "pendente":  ("#f59e0b", "⏳ Pendente"),
            "aprovado":  ("#10b981", "✅ Aprovado"),
            "rejeitado": ("#ef4444", "❌ Rejeitado"),
        }
        cor, label = cfg.get(obj.status, ("#888", obj.get_status_display()))
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:0.8rem;font-weight:700;">{}</span>',
            cor, label
        )

    @admin.display(description="Observações")
    def observacoes_resumo(self, obj):
        if obj.observacoes:
            return obj.observacoes[:80] + ("…" if len(obj.observacoes) > 80 else "")
        return "—"
