from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html, mark_safe
from .models import (
    Paciente, Avaliacao, Resposta, PerfilMedico, ModuloAvaliacao,
    Especialidade, MODULOS_POR_ESPECIALIDADE, HistoricoLogin,
    SolicitacaoPlano, MODULOS_POR_PLANO, PainelPagamentos, PainelRecebimento,
    Indicacao,
)


# ── Helper compartilhado: badge de validade ───────────────────────────────────

def _validade_badge(perfil):
    """Retorna HTML colorido com dias restantes do trial ou plano pago."""
    p = perfil

    # Plano pago com data de expiração
    if p.plano != "trial" and p.plano_expiracao:
        dias = p.plano_dias_restantes
        if dias <= 0:
            return mark_safe(
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
        return mark_safe(
            '<span style="color:#10b981;font-weight:600;font-size:.8rem;">✅ Ativo</span>'
        )

    # Trial
    if p.trial_inicio is None:
        return mark_safe('<span style="color:#aaa;font-size:.8rem;">sem data</span>')
    dias = p.trial_dias_restantes
    if dias <= 0:
        return mark_safe(
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
            return mark_safe('<span style="color:#aaa">—</span>')
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
            return mark_safe('<span style="color:#10b981;font-size:.8rem;">Hoje</span>')
        elif delta.days == 1:
            return mark_safe('<span style="color:#3b82f6;font-size:.8rem;">Ontem</span>')
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
            return mark_safe('<span style="color:#aaa">—</span>')
        return format_html(
            "{}",
            ", ".join(nomes)
        )

    @admin.display(description="Módulos")
    def modulos_count(self, obj):
        total = obj.modulos_liberados.count()
        total_disponivel = ModuloAvaliacao.objects.count()
        return format_html(
            '<span style="font-weight:700;color:#0c3c7b">{}</span>'
            '<span style="color:#aaa;font-size:.78rem"> / {}</span>',
            total, total_disponivel
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
            return mark_safe('<strong style="color:#10b981;">✅ Plano ativo</strong> — sem data de vencimento (aprovado manualmente)')
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
        return mark_safe(tags)

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


@admin.register(Indicacao)
class IndicacaoAdmin(admin.ModelAdmin):
    list_display    = ["indicador", "indicado", "criado_em", "recompensa_status"]
    list_filter     = ["recompensa_aplicada"]
    search_fields   = ["indicador__username", "indicador__first_name", "indicado__username", "indicado__first_name"]
    readonly_fields = ["indicador", "indicado", "criado_em", "recompensa_aplicada", "recompensa_aplicada_em"]
    ordering        = ["-criado_em"]

    def has_add_permission(self, request):
        return False

    def recompensa_status(self, obj):
        if obj.recompensa_aplicada:
            return mark_safe(
                '<span style="background:#f0fdf4;color:#16a34a;padding:2px 7px;'
                'border-radius:4px;font-size:.78rem;font-weight:700;">✓ Aplicada</span>'
            )
        return mark_safe(
            '<span style="background:#fffbeb;color:#d97706;padding:2px 7px;'
            'border-radius:4px;font-size:.78rem;font-weight:700;">⏳ Aguardando conversão</span>'
        )
    recompensa_status.short_description = "Recompensa"


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
    list_display        = ["criado_em_fmt", "usuario_link", "plano_badge", "status_badge", "observacoes_resumo", "aprovado_por", "aprovado_em_fmt"]
    list_filter         = ["status", "plano"]
    search_fields       = ["user__username", "user__first_name", "user__last_name", "user__email"]
    readonly_fields     = ["user", "plano", "observacoes", "criado_em", "aprovado_por", "aprovado_em"]
    ordering            = ["-criado_em"]
    actions             = [_aprovar_solicitacoes]

    def changelist_view(self, request, extra_context=None):
        return redirect("admin:pagamentos_painel")

    def has_module_perms(self, request):
        return False  # oculta do índice — use Painel de Pagamentos

    # ── URLs customizadas ─────────────────────────────────────────────────────

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "painel/",
                self.admin_site.admin_view(self.painel_view),
                name="pagamentos_painel",
            ),
            path(
                "recebimento/",
                self.admin_site.admin_view(self.recebimento_view),
                name="pagamentos_recebimento",
            ),
        ]
        return custom + urls

    def painel_view(self, request):
        """Painel completo de pagamentos dentro do Django admin."""
        from django.contrib import messages as dj_messages
        from .views.pagamentos import _notificar_usuario_aprovado, _notificar_usuario_rejeitado

        if request.method == "POST":
            action  = request.POST.get("action_painel")
            sol_id  = request.POST.get("sol_id")
            nota    = request.POST.get("nota_admin", "").strip()
            agora   = timezone.now()

            # ── Aprovar / Rejeitar solicitação ────────────────────────────────
            if action in ("aprovar", "rejeitar") and sol_id:
                sol = get_object_or_404(SolicitacaoPlano, pk=sol_id)
                if sol.status == "pendente":
                    sol.nota_admin   = nota
                    sol.aprovado_por = request.user
                    sol.aprovado_em  = agora

                    if action == "aprovar":
                        sol.status = "aprovado"
                        sol.save()
                        perfil, _ = PerfilMedico.objects.get_or_create(user=sol.user)
                        perfil.plano = sol.plano
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
                        _notificar_usuario_aprovado(sol, perfil.plano_expiracao)
                        dj_messages.success(
                            request,
                            f"✅ Plano {sol.get_plano_display()} ativado para "
                            f"{sol.user.get_full_name() or sol.user.username} — "
                            f"vence em {perfil.plano_expiracao.strftime('%d/%m/%Y')}."
                        )
                    else:
                        sol.status = "rejeitado"
                        sol.save()
                        _notificar_usuario_rejeitado(sol)
                        dj_messages.warning(
                            request,
                            f"Solicitação de {sol.user.get_full_name() or sol.user.username} rejeitada."
                        )

            # ── Renovar +30 dias (manual, sem SolicitacaoPlano) ───────────────
            elif action == "renovar":
                perfil_id = request.POST.get("perfil_id")
                novo_plano = request.POST.get("novo_plano", "").strip()
                if perfil_id:
                    perfil = get_object_or_404(PerfilMedico, pk=perfil_id)
                    # Atualiza plano se foi enviado
                    if novo_plano in ("start", "plus", "elite"):
                        perfil.plano = novo_plano
                        codigos = MODULOS_POR_PLANO.get(novo_plano, [])
                        perfil.modulos_liberados.set(ModuloAvaliacao.objects.filter(codigo__in=codigos))
                    # Renova vencimento: +30 dias a partir de hoje (ou da expiração atual se ainda vigente)
                    if perfil.plano_expiracao and perfil.plano_expiracao > agora:
                        perfil.plano_expiracao = perfil.plano_expiracao + timezone.timedelta(days=30)
                    else:
                        perfil.plano_expiracao = agora + timezone.timedelta(days=30)
                    if not perfil.user.is_active:
                        perfil.user.is_active = True
                        perfil.user.save(update_fields=["is_active"])
                    perfil.save(update_fields=["plano", "plano_expiracao"])
                    nome = perfil.user.get_full_name() or perfil.user.username
                    dj_messages.success(
                        request,
                        f"✅ {nome} — {perfil.get_plano_display()} renovado até "
                        f"{perfil.plano_expiracao.strftime('%d/%m/%Y')}."
                    )

            # ── Editar dados do profissional ──────────────────────────────────
            elif action == "editar_perfil":
                perfil_id = request.POST.get("perfil_id")
                if perfil_id:
                    perfil = get_object_or_404(PerfilMedico, pk=perfil_id)
                    first_name = request.POST.get("first_name", "").strip()
                    last_name  = request.POST.get("last_name",  "").strip()
                    email      = request.POST.get("email",      "").strip()
                    plano      = request.POST.get("plano",      "").strip()
                    exp_str    = request.POST.get("plano_expiracao", "").strip()

                    perfil.user.first_name = first_name
                    perfil.user.last_name  = last_name
                    if email:
                        perfil.user.email = email
                    perfil.user.save(update_fields=["first_name", "last_name", "email"])

                    if plano in ("trial", "start", "plus", "elite"):
                        perfil.plano = plano
                        if plano != "trial":
                            codigos = MODULOS_POR_PLANO.get(plano, [])
                            perfil.modulos_liberados.set(
                                ModuloAvaliacao.objects.filter(codigo__in=codigos)
                            )

                    if exp_str:
                        from datetime import datetime as _dt
                        try:
                            naive = _dt.strptime(exp_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
                            perfil.plano_expiracao = timezone.make_aware(naive)
                        except ValueError:
                            pass

                    perfil.save(update_fields=["plano", "plano_expiracao"])
                    nome = perfil.user.get_full_name() or perfil.user.username
                    dj_messages.success(request, f"✅ Dados de {nome} atualizados.")

            # ── Desativar usuário (não pagou) ─────────────────────────────────
            elif action == "desativar":
                perfil_id = request.POST.get("perfil_id")
                if perfil_id:
                    perfil = get_object_or_404(PerfilMedico, pk=perfil_id)
                    nome = perfil.user.get_full_name() or perfil.user.username
                    perfil.user.is_active = False
                    perfil.user.save(update_fields=["is_active"])
                    perfil.modulos_liberados.clear()
                    dj_messages.warning(
                        request,
                        f"🚫 {nome} desativado — acesso bloqueado."
                    )

            # ── Reativar usuário ──────────────────────────────────────────────
            elif action == "reativar":
                perfil_id = request.POST.get("perfil_id")
                if perfil_id:
                    perfil = get_object_or_404(PerfilMedico, pk=perfil_id)
                    nome = perfil.user.get_full_name() or perfil.user.username
                    perfil.user.is_active = True
                    perfil.user.save(update_fields=["is_active"])
                    dj_messages.success(
                        request,
                        f"✅ {nome} reativado."
                    )

            return redirect("admin:pagamentos_painel")

        # ── Dados ─────────────────────────────────────────────────────────────
        pendentes  = SolicitacaoPlano.objects.filter(status="pendente").select_related("user").order_by("-criado_em")
        historico  = (
            SolicitacaoPlano.objects
            .exclude(status="pendente")
            .select_related("user", "aprovado_por")
            .order_by("-aprovado_em")[:30]
        )

        # Assinantes com plano pago
        assinantes = (
            PerfilMedico.objects
            .filter(plano__in=("start", "plus", "elite"), user__is_active=True)
            .select_related("user")
            .order_by("plano_expiracao")
        )

        # TODOS os profissionais (para visão geral — inclui trial e planos pagos)
        todos_perfis = (
            PerfilMedico.objects
            .select_related("user")
            .order_by("plano", "user__first_name", "user__last_name")
        )

        # Badges de dias restantes para cada assinante (computed)
        assinantes_info = []
        for p in assinantes:
            dias = p.plano_dias_restantes
            assinantes_info.append({
                "perfil": p,
                "dias": dias,
                "badge": _validade_badge(p),
            })

        # Todos os profissionais com badge
        todos_info = []
        for p in todos_perfis:
            todos_info.append({
                "perfil": p,
                "badge": _validade_badge(p),
            })

        # Stats cards
        total_assinantes  = assinantes.count()
        total_pendentes   = pendentes.count()
        total_profissionais = todos_perfis.count()
        vencendo_3  = sum(1 for x in assinantes_info if x["dias"] is not None and 0 < x["dias"] <= 3)
        vencendo_7  = sum(1 for x in assinantes_info if x["dias"] is not None and 0 < x["dias"] <= 7)
        vencidos    = sum(1 for x in assinantes_info if x["dias"] is not None and x["dias"] <= 0)

        ctx = {
            **self.admin_site.each_context(request),
            "title":               "Painel de Pagamentos",
            "opts":                self.model._meta,
            "pendentes":           pendentes,
            "historico":           historico,
            "assinantes_info":     assinantes_info,
            "todos_info":          todos_info,
            "total_assinantes":    total_assinantes,
            "total_pendentes":     total_pendentes,
            "total_profissionais": total_profissionais,
            "vencendo_3":          vencendo_3,
            "vencendo_7":          vencendo_7,
            "vencidos":            vencidos,
        }
        return render(request, "admin/questionario/solicitacaoplano/painel.html", ctx)

    def recebimento_view(self, request):
        """Painel de recebimento — MRR, ARR, breakdown por plano e histórico mensal."""
        from decimal import Decimal
        from collections import defaultdict, OrderedDict
        from django.db.models.functions import TruncMonth
        from django.db.models import Count

        VALOR_PLANO = {
            "start": Decimal("39.90"),
            "plus":  Decimal("79.90"),
            "elite": Decimal("149.90"),
        }

        def _brl(value):
            s = f"{float(value):,.2f}"
            return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")

        agora  = timezone.now()
        em_30  = agora + timezone.timedelta(days=30)
        em_60  = agora + timezone.timedelta(days=60)

        # ── Assinantes ativos ────────────────────────────────────────────────
        ativos = list(
            PerfilMedico.objects
            .filter(plano__in=("start", "plus", "elite"),
                    user__is_active=True,
                    plano_expiracao__gt=agora)
            .select_related("user")
        )

        por_plano = defaultdict(int)
        for p in ativos:
            por_plano[p.plano] += 1

        mrr = Decimal("0.00")
        breakdown = []
        for plano_key, label, color in [
            ("start", "START", "#3b82f6"),
            ("plus",  "PLUS",  "#8b5cf6"),
            ("elite", "ELITE", "#0c3c7b"),
        ]:
            count    = por_plano.get(plano_key, 0)
            valor    = VALOR_PLANO[plano_key]
            subtotal = valor * count
            mrr     += subtotal
            breakdown.append({
                "plano":    plano_key,
                "label":    label,
                "color":    color,
                "count":    count,
                "valor":    _brl(valor),
                "subtotal": _brl(subtotal),
                "subtotal_raw": float(subtotal),
            })

        total_ativos = len(ativos)
        ticket_medio = mrr / total_ativos if total_ativos else Decimal("0.00")

        # ── Total histórico (todas as ativações aprovadas × valor do plano) ──
        hist_planos = (
            SolicitacaoPlano.objects
            .filter(status="aprovado")
            .values("plano")
            .annotate(total=Count("id"))
        )
        total_historico = sum(
            VALOR_PLANO.get(row["plano"], Decimal("0")) * row["total"]
            for row in hist_planos
        )

        # ── Histórico mensal (últimos 12 meses) ──────────────────────────────
        inicio_hist = agora - timezone.timedelta(days=365)
        hist_raw = (
            SolicitacaoPlano.objects
            .filter(status="aprovado", aprovado_em__gte=inicio_hist)
            .annotate(mes=TruncMonth("aprovado_em"))
            .values("mes", "plano")
            .annotate(total=Count("id"))
            .order_by("mes", "plano")
        )

        meses_dict = OrderedDict()
        for row in hist_raw:
            mk = row["mes"]
            if mk not in meses_dict:
                meses_dict[mk] = {"mes": mk, "start": 0, "plus": 0, "elite": 0}
            if row["plano"] in meses_dict[mk]:
                meses_dict[mk][row["plano"]] = row["total"]

        historico_mensal = []
        for mk in sorted(meses_dict.keys(), reverse=True):
            d = meses_dict[mk]
            rec = (
                d["start"] * VALOR_PLANO["start"] +
                d["plus"]  * VALOR_PLANO["plus"]  +
                d["elite"] * VALOR_PLANO["elite"]
            )
            historico_mensal.append({
                "mes":     mk.strftime("%b/%Y"),
                "start":   d["start"],
                "plus":    d["plus"],
                "elite":   d["elite"],
                "total":   d["start"] + d["plus"] + d["elite"],
                "receita": _brl(rec),
            })

        # ── Próximos vencimentos 30 dias ─────────────────────────────────────
        proximos_30 = list(
            PerfilMedico.objects
            .filter(plano__in=("start", "plus", "elite"),
                    user__is_active=True,
                    plano_expiracao__gt=agora,
                    plano_expiracao__lte=em_30)
            .select_related("user")
            .order_by("plano_expiracao")
        )
        receita_risco_30 = sum(VALOR_PLANO.get(p.plano, Decimal("0")) for p in proximos_30)

        proximos_60 = (
            PerfilMedico.objects
            .filter(plano__in=("start", "plus", "elite"),
                    user__is_active=True,
                    plano_expiracao__gt=em_30,
                    plano_expiracao__lte=em_60)
            .count()
        )

        # MRR máx para porcentagem das barras
        mrr_raw = float(mrr) if mrr else 1

        for item in breakdown:
            item["pct"] = round(item["subtotal_raw"] / mrr_raw * 100) if mrr_raw else 0

        ctx = {
            **self.admin_site.each_context(request),
            "title":            "Painel de Recebimento",
            "opts":             self.model._meta,
            "mrr":              _brl(mrr),
            "total_historico":  _brl(total_historico),
            "ticket_medio":     _brl(ticket_medio),
            "total_ativos":     total_ativos,
            "breakdown":        breakdown,
            "historico_mensal": historico_mensal,
            "proximos_30":      proximos_30,
            "proximos_60_count": proximos_60,
            "receita_risco_30": _brl(receita_risco_30),
        }
        return render(request, "admin/questionario/solicitacaoplano/recebimento.html", ctx)

    # ── list_display ──────────────────────────────────────────────────────────

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


# ── Proxy: entrada direta "Painel de Pagamentos" no sidebar do admin ───────

@admin.register(PainelPagamentos)
class PainelPagamentosAdmin(admin.ModelAdmin):
    """Aparece no índice e sidebar do admin. Redireciona para painel_view."""

    def changelist_view(self, request, extra_context=None):
        return redirect("admin:pagamentos_painel")

    def has_module_perms(self, request):
        return request.user.is_staff

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff


@admin.register(PainelRecebimento)
class PainelRecebimentoAdmin(admin.ModelAdmin):
    """Aparece no índice e sidebar do admin. Redireciona para recebimento_view."""

    def changelist_view(self, request, extra_context=None):
        return redirect("admin:pagamentos_recebimento")

    def has_module_perms(self, request):
        return request.user.is_staff

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff
