import uuid

from django.core.mail import send_mail
from django.urls import reverse


# ─── Link de avaliações ───────────────────────────────────────────────────────

def build_lista_com_link(queryset, request, publico_url_name):
    result = []
    for av in queryset:
        if not av.token and av.status != "concluida":
            av.token = str(uuid.uuid4())
            av.save(update_fields=["token"])
        link_publico = None
        if av.token and av.status != "concluida":
            path = reverse(publico_url_name, kwargs={"token": av.token, "pagina": 1})
            link_publico = request.build_absolute_uri(path)
        result.append({"obj": av, "link_publico": link_publico})
    return result


def build_lista_sem_pagina(queryset, request, publico_url_name):
    """Like build_lista_com_link but for URLs without a pagina parameter."""
    result = []
    for av in queryset:
        if not av.token and av.status != "concluida":
            av.token = str(uuid.uuid4())
            av.save(update_fields=["token"])
        link_publico = None
        if av.token and av.status != "concluida":
            path = reverse(publico_url_name, kwargs={"token": av.token})
            link_publico = request.build_absolute_uri(path)
        result.append({"obj": av, "link_publico": link_publico})
    return result


# ─── Notificações ─────────────────────────────────────────────────────────────

def notificar_terapeuta(paciente, tipo, request):
    from django.template.loader import render_to_string
    terapeuta = paciente.medico
    if not terapeuta.email:
        return
    _NOMES = {
        "sensorial":       "Perfil Sensorial",
        "vineland":        "Escala Vineland",
        "escolar":         "Sensorial Escolar",
        "bebe":            "Perfil Sensorial Bebê",
        "spm":             "SPM",
        "spm_p":           "SPM-P Casa",
        "spm_casa":        "SPM Casa",
        "pedi":            "PEDI",
        "vineland3":       "Vineland-3",
        "portage":         "Guia Portage",
        "sdq":             "SDQ",
        "snap_iv":         "SNAP-IV",
        "mchat":           "M-CHAT-R",
        "cars":            "CARS-2",
        "linguagem":       "Avaliação de Linguagem",
        "alimentacao":     "Triagem de Alimentação Seletiva",
        "desenvolvimento": "Marcos de Desenvolvimento",
        "sono":            "Avaliação de Sono Infantil",
        "habilidades":     "Habilidades Adaptativas",
        "comportamento":   "Comportamento Funcional",
        "cognitivo":       "Rastreio Cognitivo",
        "psicopedagogica": "Avaliação Psicopedagógica",
    }
    nome_tipo = _NOMES.get(tipo, tipo.replace("_", " ").title())
    nome_terapeuta = terapeuta.get_full_name() or terapeuta.username
    link = request.build_absolute_uri(
        reverse("detalhe_paciente", kwargs={"paciente_id": paciente.uuid})
    )
    html = render_to_string("questionario/email_notificacao_terapeuta.html", {
        "nome_terapeuta": nome_terapeuta,
        "paciente": paciente,
        "nome_tipo": nome_tipo,
        "link": link,
    })
    send_mail(
        subject=f"IntegraMente — Avaliação concluída: {paciente.nome}",
        message=(
            f"Olá, {nome_terapeuta}!\n\n"
            f"O responsável de {paciente.nome} concluiu o questionário de {nome_tipo}.\n"
            f"Acesse o sistema para visualizar os resultados: {link}"
        ),
        from_email=None,
        recipient_list=[terapeuta.email],
        html_message=html,
        fail_silently=True,
    )


# ─── CSS helpers ──────────────────────────────────────────────────────────────

def classe_css(classificacao):
    return {"Muito menos": "muito-menos", "Menos": "menos", "Típico": "tipico",
            "Mais": "mais", "Muito mais": "muito-mais"}.get(classificacao, "")


# ─── Tipos de avaliação (label + ícone) ───────────────────────────────────────

TIPO_INFO = {
    "sensorial":       ("Perfil Sensorial",               '<i data-lucide="brain" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "vineland":        ("Escala Vineland",                 '<i data-lucide="puzzle" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "escolar":         ("Questionário Sensorial Escolar",  '<i data-lucide="school" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "bebe":            ("Bebê (0–6 meses)",                '<i data-lucide="baby" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "crianca_pequena": ("Criança Pequena (7–36 meses)",    '<i data-lucide="user-round" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "spm_p":           ("SPM-P Casa (2–5 anos)",           '<i data-lucide="user-round" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "spm_casa":        ("SPM Casa (5–12 anos)",            '<i data-lucide="house" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "edm":             ("EDM Figueiredo",                  '<i data-lucide="activity" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "mabc2":           ("MABC-2",                          '<i data-lucide="target" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "beery":           ("Beery VMI",                       '<i data-lucide="pencil" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "pedi":            ("PEDI",                            '<i data-lucide="accessibility" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "vineland3":       ("Vineland-3",                      '<i data-lucide="puzzle" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "portage":         ("Guia Portage",                    '<i data-lucide="baby" style="width:18px;height:18px;vertical-align:middle;"></i>'),
}
