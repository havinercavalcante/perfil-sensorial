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
    Redireciona para /trial-expirado/ quando o plano (trial ou pago) está vencido.
    Bloqueia em tempo real — independente de quando o Celery rodar.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and not any(request.path.startswith(p) for p in _TRIAL_EXEMPT)
        ):
            try:
                perfil = request.user.perfil

                # Trial vencido
                if perfil.plano == "trial" and not perfil.trial_ativo:
                    return redirect("trial_expirado")

                # Plano pago vencido (só bloqueia se tiver data definida)
                if (
                    perfil.plano in ("start", "plus", "elite")
                    and perfil.plano_expiracao is not None
                    and not perfil.plano_ativo
                ):
                    return redirect("trial_expirado")

            except Exception:
                pass

        return self.get_response(request)
