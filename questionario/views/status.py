from django.shortcuts import render
from django.utils import timezone
from django.db import connection


def _check_database():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return "operational"
    except Exception:
        return "outage"


def _check_email():
    from django.conf import settings
    import smtplib

    backend = getattr(settings, "EMAIL_BACKEND", "")
    if "console" in backend or "dummy" in backend or "locmem" in backend:
        return "operational"

    host = getattr(settings, "EMAIL_HOST", "")
    port = getattr(settings, "EMAIL_PORT", 587)
    use_tls = getattr(settings, "EMAIL_USE_TLS", False)

    if not host:
        return "degraded"

    try:
        if use_tls:
            smtp = smtplib.SMTP(host, port, timeout=5)
            smtp.starttls()
        else:
            smtp = smtplib.SMTP_SSL(host, port, timeout=5) if getattr(settings, "EMAIL_USE_SSL", False) else smtplib.SMTP(host, port, timeout=5)
        smtp.quit()
        return "operational"
    except Exception:
        return "degraded"


def _check_celery():
    try:
        from django_celery_results.models import TaskResult
        TaskResult.objects.count()
        return "operational"
    except Exception:
        return "degraded"


def status_view(request):
    from questionario.models import StatusIncident

    db_status     = _check_database()
    email_status  = _check_email()
    celery_status = _check_celery()

    components = [
        {"nome": "Aplicação Web",            "icone": "globe",    "status": "operational"},
        {"nome": "Banco de Dados",           "icone": "database", "status": db_status},
        {"nome": "Tarefas em Segundo Plano", "icone": "zap",      "status": celery_status},
    ]

    all_operational = all(c["status"] == "operational" for c in components)
    any_outage      = any(c["status"] == "outage"      for c in components)

    if any_outage:
        global_status = "outage"
    elif not all_operational:
        global_status = "degraded"
    else:
        global_status = "operational"

    incidents_ativos    = StatusIncident.objects.filter(status__in=["investigating", "identified", "monitoring", "scheduled", "in_progress"])
    incidents_historico = StatusIncident.objects.filter(status__in=["resolved", "completed"])[:10]

    return render(request, "questionario/status.html", {
        "components":          components,
        "global_status":       global_status,
        "incidents_ativos":    incidents_ativos,
        "incidents_historico": incidents_historico,
        "now":                 timezone.now(),
    })
