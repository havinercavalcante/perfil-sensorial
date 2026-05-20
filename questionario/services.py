import uuid

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
    terapeuta = paciente.medico
    if not terapeuta.email:
        return
    link = request.build_absolute_uri(
        reverse("detalhe_paciente", kwargs={"paciente_id": paciente.uuid})
    )
    from .tasks import enviar_email_notificacao
    enviar_email_notificacao.delay(paciente.pk, tipo, link)


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
    "portage":              ("Guia Portage",                       '<i data-lucide="baby" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "linguagem":            ("Avaliação de Linguagem",             '<i data-lucide="message-circle" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "alimentacao_seletiva": ("Triagem de Alimentação Seletiva",    '<i data-lucide="utensils" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "habitos_orais":        ("Hábitos Orais Deletérios",           '<i data-lucide="smile" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "voz_infantil":         ("Triagem de Voz Infantil",            '<i data-lucide="mic" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "processamento_auditivo": ("Triagem de Processamento Auditivo", '<i data-lucide="ear" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "idv10":                ("IDV-10 — Desvantagem Vocal",         '<i data-lucide="volume-2" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "desenvolvimento":           ("Marcos do Desenvolvimento",          '<i data-lucide="trending-up" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "sono_infantil":             ("Sono Infantil",                      '<i data-lucide="moon" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "habilidades_adaptativas":   ("Habilidades Adaptativas",            '<i data-lucide="check-square" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "comportamento_funcional":   ("Comportamento Funcional",            '<i data-lucide="activity" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "rastreio_cognitivo":        ("Rastreio Cognitivo",                 '<i data-lucide="cpu" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "psicopedagogica":           ("Avaliação Psicopedagógica",          '<i data-lucide="book-open" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "sdq":                       ("SDQ",                                '<i data-lucide="clipboard-list" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "snap_iv":                   ("SNAP-IV",                            '<i data-lucide="zap" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "mchat":                     ("M-CHAT-R",                           '<i data-lucide="baby" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "cars":                      ("CARS-2",                             '<i data-lucide="alert-circle" style="width:18px;height:18px;vertical-align:middle;"></i>'),
}
