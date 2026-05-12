import uuid

from django.core.mail import send_mail
from django.urls import reverse

from .data_spm import (
    SECOES_SPM_P, SECOES_SPM_CASA,
    PERGUNTAS_SPM_P, PERGUNTAS_SPM_CASA,
    SECOES_CONFIG_SPM,
    calcular_pontuacao_spm,
    max_score_spm,
    classificar_spm_pct,
)
from .models import RespostaSPM


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


# ─── Notificações ─────────────────────────────────────────────────────────────

def notificar_terapeuta(paciente, tipo, request):
    terapeuta = paciente.medico
    if not terapeuta.email:
        return
    nome_tipo = "Perfil Sensorial" if tipo == "sensorial" else "Escala Vineland"
    send_mail(
        subject=f"CeciSys — Avaliação concluída: {paciente.nome}",
        message=(
            f"Olá, {terapeuta.get_full_name() or terapeuta.username}!\n\n"
            f"O responsável de {paciente.nome} concluiu o questionário de {nome_tipo}.\n"
            f"Acesse o sistema para visualizar os resultados."
        ),
        from_email=None,
        recipient_list=[terapeuta.email],
        fail_silently=True,
    )


# ─── CSS helpers ──────────────────────────────────────────────────────────────

def classe_css(classificacao):
    return {"Muito menos": "muito-menos", "Menos": "menos", "Típico": "tipico",
            "Mais": "mais", "Muito mais": "muito-mais"}.get(classificacao, "")


# ─── MABC-2 ───────────────────────────────────────────────────────────────────

def mabc2_escore_para_percentil(escore_total):
    tabela = [
        (3, 0), (6, 0), (9, 1), (12, 2), (15, 5), (18, 9),
        (21, 16), (24, 25), (27, 37), (30, 50), (33, 63),
        (36, 75), (39, 84), (42, 91), (45, 95), (48, 98),
        (51, 99), (57, 99),
    ]
    if escore_total is None:
        return None
    for escore, perc in tabela:
        if escore_total <= escore:
            return perc
    return 99


def classificar_mabc2(percentil):
    if percentil is None:
        return "—"
    if percentil <= 5:
        return "Dificuldade significativa"
    elif percentil <= 15:
        return "Risco"
    else:
        return "Típico"


# ─── Beery VMI ────────────────────────────────────────────────────────────────

_BEERY_ESCORE_PERCENTIL = {
    55: 0, 60: 0, 65: 1, 70: 2, 75: 5, 80: 9, 85: 16,
    90: 25, 95: 37, 100: 50, 105: 63, 110: 75, 115: 84,
    120: 91, 125: 95, 130: 98, 135: 99, 140: 99,
}


def beery_escore_para_percentil(escore):
    if escore is None:
        return None
    chaves = sorted(_BEERY_ESCORE_PERCENTIL.keys())
    if escore <= chaves[0]:
        return _BEERY_ESCORE_PERCENTIL[chaves[0]]
    if escore >= chaves[-1]:
        return _BEERY_ESCORE_PERCENTIL[chaves[-1]]
    for i in range(len(chaves) - 1):
        if chaves[i] <= escore < chaves[i + 1]:
            return _BEERY_ESCORE_PERCENTIL[chaves[i]]
    return None


def classificar_beery(escore):
    if escore is None:
        return "—"
    if escore < 70:
        return "Dificuldade significativa"
    elif escore < 85:
        return "Abaixo da média"
    elif escore <= 115:
        return "Médio"
    elif escore <= 130:
        return "Acima da média"
    else:
        return "Superior"


# ─── SPM ──────────────────────────────────────────────────────────────────────

def spm_dados(faixa):
    if faixa == "spm_p":
        return SECOES_SPM_P, PERGUNTAS_SPM_P
    return SECOES_SPM_CASA, PERGUNTAS_SPM_CASA


def spm_salvar_pontuacao(avaliacao):
    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    p = calcular_pontuacao_spm(respostas, avaliacao.faixa)
    avaliacao.pont_soc = p.get("soc", 0)
    avaliacao.pont_vis = p.get("vis", 0)
    avaliacao.pont_hea = p.get("hea", 0)
    avaliacao.pont_tou = p.get("tou", 0)
    avaliacao.pont_sme = p.get("sme", 0)
    avaliacao.pont_bod = p.get("bod", 0)
    avaliacao.pont_bal = p.get("bal", 0)
    avaliacao.pont_pla = p.get("pla", 0)
    avaliacao.pont_tot = p.get("tot", 0)
    return avaliacao


def spm_build_secoes(avaliacao):
    maximos = max_score_spm(avaliacao.faixa)
    campo_map = {
        "soc": avaliacao.pont_soc, "vis": avaliacao.pont_vis,
        "hea": avaliacao.pont_hea, "tou": avaliacao.pont_tou,
        "sme": avaliacao.pont_sme, "bod": avaliacao.pont_bod,
        "bal": avaliacao.pont_bal, "pla": avaliacao.pont_pla,
    }
    secoes = []
    for sec_id, config in SECOES_CONFIG_SPM.items():
        valor = campo_map.get(sec_id) or 0
        maximo = maximos.get(sec_id, 1)
        pct = int(valor / maximo * 100) if maximo else 0
        secoes.append({
            "id": sec_id,
            "nome": config["nome"],
            "sigla": config["sigla"],
            "cor": config["cor"],
            "valor": valor,
            "maximo": maximo,
            "pct": pct,
            "classificacao": classificar_spm_pct(pct),
        })
    return secoes


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
}
