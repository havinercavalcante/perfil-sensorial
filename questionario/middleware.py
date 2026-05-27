from django.shortcuts import render, redirect


class CustomErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404:
            return render(request, "erros/404.html", status=404)
        if response.status_code == 403:
            return render(request, "erros/403.html", status=403)
        return response


# URLs isentas da verificação de trial (prefixos)
_TRIAL_EXEMPT = (
    "/trial-expirado/",
    "/logout/",
    "/login/",
    "/registrar/",
    "/admin/",
    "/static/",
    "/media/",
    "/privacidade/",
    "/confirmar-email/",
    "/pagamentos/",   # solicitar plano, painel admin
)


class TrialExpiradoMiddleware:
    """
    Controla acesso baseado no estado do plano do usuário.

    Usuário desativado (is_active=False, não-staff):
      → Pode fazer login, mas todas as páginas redirecionam para /pagamentos/solicitar/
      → Só consegue acessar /pagamentos/, /logout/, /static/, /admin/

    Trial vencido ou plano pago vencido:
      → Redireciona para /trial-expirado/ (tela de renovação)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and not any(request.path.startswith(p) for p in _TRIAL_EXEMPT)
        ):
            # ── Usuário desativado pelo admin (não pagou) ─────────────────────
            if not request.user.is_active and not request.user.is_staff:
                return redirect("solicitar_plano")

            try:
                perfil = request.user.perfil

                # ── Trial vencido ─────────────────────────────────────────────
                if perfil.plano == "trial" and not perfil.trial_ativo:
                    return redirect("trial_expirado")

                # ── Plano pago vencido ────────────────────────────────────────
                if (
                    perfil.plano in ("start", "plus", "elite")
                    and perfil.plano_expiracao is not None
                    and not perfil.plano_ativo
                ):
                    return redirect("trial_expirado")

            except Exception:
                pass

        return self.get_response(request)
