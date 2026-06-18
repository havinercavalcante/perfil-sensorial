from datetime import timedelta

from django.shortcuts import render, redirect
from django.utils import timezone

_TRACKED_PAGES = {
    "/":               "landing",
    "/login/":         "login",
    "/registrar/":     "cadastro",
    "/instrumentos/":  "instrumentos",
    "/privacidade/":   "privacidade",
    "/contato/":       "contato",
    "/planos/":        "planos",
}


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


# URLs isentas da verificação de plano (prefixos)
_TRIAL_EXEMPT = (
    "/logout/",
    "/login/",
    "/registrar/",
    "/admin/",
    "/static/",
    "/media/",
    "/privacidade/",
    "/confirmar-email/",
    "/planos/",
)

_GRACE_DAYS = 5


class TrialExpiradoMiddleware:
    """
    Controla acesso baseado no estado do plano do usuário.

    Usuário desativado (is_active=False, não-staff):
      → Redireciona para /planos/

    Trial ou plano pago vencido há mais de 5 dias:
      → Redireciona para /planos/
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
                now = timezone.now()

                # ── Trial vencido há mais de 5 dias ───────────────────────────
                if (
                    perfil.plano == "trial"
                    and perfil.trial_inicio is not None
                    and (now - perfil.trial_inicio).days > 7 + _GRACE_DAYS
                ):
                    return redirect("solicitar_plano")

                # ── Plano pago vencido há mais de 5 dias ──────────────────────
                if (
                    perfil.plano in ("start", "plus", "elite")
                    and perfil.plano_expiracao is not None
                    and now > perfil.plano_expiracao + timedelta(days=_GRACE_DAYS)
                ):
                    return redirect("solicitar_plano")

            except Exception:
                pass

        return self.get_response(request)


class PageVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        pagina_key = _TRACKED_PAGES.get(request.path)
        if pagina_key and request.method == "GET" and response.status_code == 200:
            try:
                from .models import PageVisit
                ip = (
                    request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
                    or request.META.get("REMOTE_ADDR")
                )
                PageVisit.objects.create(
                    pagina=pagina_key,
                    ip=ip or None,
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                    referrer=(request.META.get("HTTP_REFERER") or "")[:500],
                )
            except Exception:
                pass

        return response
