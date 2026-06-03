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
    # ── Psicologia infantil — pais ────────────────────────────────────
    "conners_pais":              ("Conners-3 (Pais)",                   '<i data-lucide="clipboard-check" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "etdah_pais":                ("ETDAH (Pais)",                       '<i data-lucide="zap" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "auqei":                     ("AUQEI — Qualidade de Vida",          '<i data-lucide="heart" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "aq10_child":                ("AQ-10 Criança",                      '<i data-lucide="search" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "scared":                    ("SCARED — Ansiedade (Pais)",          '<i data-lucide="alert-triangle" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "masc":                      ("MASC — Ansiedade",                   '<i data-lucide="alert-triangle" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "scq":                       ("SCQ — Comunicação Social",           '<i data-lucide="message-circle" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "anamnese_tea_inf":          ("Anamnese TEA Infantil",              '<i data-lucide="file-text" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "anamnese_tdah_inf":         ("Anamnese TDAH Infantil",             '<i data-lucide="file-text" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    # ── Psicologia — professor ────────────────────────────────────────
    "conners_prof":              ("Conners-3 (Professor)",              '<i data-lucide="clipboard-check" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "etdah_prof":                ("ETDAH (Professor)",                  '<i data-lucide="zap" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    # ── Psicologia adulto ─────────────────────────────────────────────
    "bdi":                       ("BDI — Depressão de Beck",            '<i data-lucide="cloud-rain" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "bai":                       ("BAI — Ansiedade de Beck",            '<i data-lucide="alert-triangle" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "dass21":                    ("DASS-21",                            '<i data-lucide="thermometer" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "had":                       ("HAD — Ansiedade e Depressão",        '<i data-lucide="thermometer" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "bsl23":                     ("BSL-23 — Borderline",                '<i data-lucide="shield-alert" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "aq10_adulto":               ("AQ-10 Adulto",                       '<i data-lucide="search" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "dep_emocional":             ("Dependência Emocional",              '<i data-lucide="heart-crack" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "bpq":                       ("BPQ — Borderline",                   '<i data-lucide="shield-alert" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "anamnese_adulto":           ("Anamnese Adulto",                    '<i data-lucide="file-text" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "anamnese_tdah_adulto":      ("Anamnese TDAH Adulto",               '<i data-lucide="file-text" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    # ── Pediatria / Neuropediatria ────────────────────────────────────
    "denver":                    ("Checklist Denver II",                '<i data-lucide="trending-up" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    # ── Neuropsicologia ───────────────────────────────────────────────
    "qmpi":                      ("QMPI — Memória Prospectiva",         '<i data-lucide="cpu" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    # ── Psicopedagogia ────────────────────────────────────────────────
    "quest_dislexia":            ("Quest. Dislexia (Pais)",             '<i data-lucide="book-open" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "checklist_dislexia":        ("Checklist Dislexia",                 '<i data-lucide="check-square" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "prot_dislexia_prof":        ("Protocolo Dislexia (Professor)",     '<i data-lucide="book-open" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "inventario_dislexia":       ("Inventário Sinais Disléxicos",       '<i data-lucide="list" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    # ── Triagem Internacional ─────────────────────────────────────────
    "phq9":              ("PHQ-9",                            '<i data-lucide="clipboard-list" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "gad7":              ("GAD-7",                            '<i data-lucide="alert-triangle" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "epds":              ("EPDS — Depressão Pós-Parto",       '<i data-lucide="heart" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "pcl5":              ("PCL-5 — PTSD",                     '<i data-lucide="shield-alert" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "ghq12":             ("GHQ-12",                           '<i data-lucide="activity" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    # ── Novas Escalas — Adulto ────────────────────────────────────────
    "k10":               ("K-10 — Kessler",                   '<i data-lucide="thermometer" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "ucla":              ("UCLA — Solidão",                    '<i data-lucide="users" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "msi_bpd":           ("MSI-BPD",                          '<i data-lucide="shield-alert" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "gds15":             ("GDS-15",                           '<i data-lucide="cloud-rain" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "rosenberg":         ("Rosenberg — Autoestima",           '<i data-lucide="star" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "audit":             ("AUDIT",                            '<i data-lucide="wine" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "bis11":             ("BIS-11",                           '<i data-lucide="zap" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "hama":              ("HAM-A",                            '<i data-lucide="alert-triangle" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "lsas":              ("LSAS",                             '<i data-lucide="users" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "risco_suicidio":    ("Triagem de Risco de Suicídio",     '<i data-lucide="alert-octagon" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "agorafobia":        ("Agorafobia",                       '<i data-lucide="compass" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "panico":            ("Pânico",                           '<i data-lucide="wind" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    # ── Novas Escalas — Infantil ──────────────────────────────────────
    "iar":               ("IAR — Ansiedade Infantil",          '<i data-lucide="alert-triangle" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "pas":               ("PAS — Ansiedade Pré-Escolar",       '<i data-lucide="baby" style="width:18px;height:18px;vertical-align:middle;"></i>'),
    "cdi":               ("CDI — Depressão Infantil",          '<i data-lucide="cloud-rain" style="width:18px;height:18px;vertical-align:middle;"></i>'),
}
