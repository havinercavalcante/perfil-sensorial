"""
Laudos clínicos genéricos — um view e template compartilhados para todos os
instrumentos, com configuração por-instrumento definida aqui.
"""
import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from ..models import (
    AvaliacaoSPM, AvaliacaoVineland, AvaliacaoEscolar, AvaliacaoBebe,
    AvaliacaoEDM, AvaliacaoMABC2, AvaliacaoBeery, AvaliacaoPEDI,
    AvaliacaoVineland3, AvaliacaoPortage, AvaliacaoSDQ, AvaliacaoSNAPIV,
    AvaliacaoMCHAT, AvaliacaoCARS, AvaliacaoLinguagem, AvaliacaoAlimentacao,
    AvaliacaoHabitosOrais, AvaliacaoVozInfantil, AvaliacaoProcessamentoAuditivo,
    AvaliacaoIDV10, AvaliacaoDesenvolvimento, AvaliacaoSono,
    AvaliacaoHabilidadesAdaptativas, AvaliacaoComportamentoFuncional,
    AvaliacaoRastreioCognitivo, AvaliacaoPsicopedagogica,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _idade_str(data_nasc):
    if not data_nasc:
        return "—"
    hoje = datetime.date.today()
    anos = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
    meses = (hoje.month - data_nasc.month - (hoje.day < data_nasc.day)) % 12
    if anos >= 2:
        return f"{anos} anos"
    if anos == 1:
        return f"1 ano e {meses} mês{'es' if meses != 1 else ''}"
    return f"{meses} meses"


def _extrair_secoes(avaliacao, campos):
    """
    campos: lista de (campo, nome_display, maximo_opcional)
    Retorna lista de {nome, valor, maximo}.
    """
    secoes = []
    for item in campos:
        campo = item[0]
        nome  = item[1]
        maximo = item[2] if len(item) > 2 else None
        valor = getattr(avaliacao, campo, None)
        secoes.append({"nome": nome, "valor": valor, "maximo": maximo})
    return secoes


# ─── Configuração por instrumento ─────────────────────────────────────────────

def _config_spm(av):
    nome = "SPM-P Casa (2–5 anos)" if av.faixa == "spm_p" else "SPM Casa (5–12 anos)"
    from ..data.data_spm import tscore_spm, classificar_tscore_spm, SECOES_CONFIG_SPM
    campo_map = {
        "soc": av.pont_soc, "vis": av.pont_vis, "hea": av.pont_hea,
        "tou": av.pont_tou, "sme": av.pont_sme, "bod": av.pont_bod,
        "bal": av.pont_bal, "pla": av.pont_pla,
    }
    secoes = []
    for sec_id, cfg in SECOES_CONFIG_SPM.items():
        raw = campo_map.get(sec_id) or 0
        t = tscore_spm(raw, sec_id, av.faixa)
        secoes.append({
            "nome": cfg["nome"], "valor": raw,
            "extra": f"T={t}" if t else None,
            "classificacao": classificar_tscore_spm(t) if t else None,
            "cor": cfg["cor"],
        })
    return nome, "Sensory Processing Measure (SPM)", secoes


def _config_vineland(av):
    campos = [
        ("pont_comunicacao", "Comunicação"),
        ("pont_locomocao",   "Locomoção"),
        ("pont_ocupacao",    "Ocupação"),
        ("pont_socializacao","Socialização"),
        ("pont_autogoverno", "Autogoverno"),
        ("pont_age",         "Grupo de Pares (AGE)"),
        ("pont_ac",          "Autocuidado (AC)"),
        ("pont_av",          "Autocontrole/Vocabulário (AV)"),
        ("pont_total",       "Maturidade Social Total"),
    ]
    secoes = _extrair_secoes(av, campos)
    return "Escala Vineland de Maturidade Social", "Escala Vineland (Sparrow, Cicchetti & Balla)", secoes


def _config_escolar(av):
    campos = [
        ("pont_ex", "Busca de Sensação"),
        ("pont_ev", "Evitação Sensorial"),
        ("pont_sn", "Sensibilidade Sensorial"),
        ("pont_ob", "Registro Sensorial"),
    ]
    secoes = _extrair_secoes(av, campos)
    return "Questionário Sensorial Escolar", "Perfil Sensorial — versão escolar (Dunn, 2014)", secoes


def _config_bebe(av):
    campos = [
        ("pont_ex", "Busca de Sensação"),
        ("pont_ev", "Evitação Sensorial"),
        ("pont_sn", "Sensibilidade Sensorial"),
        ("pont_ob", "Registro Sensorial"),
    ]
    secoes = _extrair_secoes(av, campos)
    faixa = getattr(av, "faixa", "")
    nome = "Bebê (0–6 meses)" if faixa == "bebe" else "Criança Pequena (7–36 meses)"
    return nome, "Perfil Sensorial — Bebê / Criança Pequena (Dunn, 2014)", secoes


def _config_edm(av):
    campos = [
        ("idade_motricidade_fina",    "Motricidade Fina (meses)"),
        ("idade_motricidade_ampla",   "Motricidade Ampla (meses)"),
        ("idade_equilibrio",          "Equilíbrio (meses)"),
        ("idade_esquema_corporal",    "Esquema Corporal (meses)"),
        ("idade_organizacao_espacial","Organização Espacial (meses)"),
        ("idade_organizacao_temporal","Organização Temporal (meses)"),
        ("idade_motora_geral",        "Idade Motora Geral (meses)"),
        ("quociente_motor",           "Quociente Motor (QM)"),
    ]
    secoes = _extrair_secoes(av, campos)
    return "EDM — Escala de Desenvolvimento Motor", "EDM — Figueiredo (2010)", secoes


def _config_mabc2(av):
    campos = [
        ("md_escore",    "Destreza Manual", 19),
        ("ac_escore",    "Arremesso / Recepção", 19),
        ("eq_escore",    "Equilíbrio", 19),
        ("escore_total", "Escore Total", 57),
        ("percentil",    "Percentil", 100),
    ]
    secoes = _extrair_secoes(av, campos)
    return "MABC-2", "Movement Assessment Battery for Children – 2ª ed.", secoes


def _config_beery(av):
    campos = [
        ("vmi_raw",       "VMI — Escore bruto"),
        ("vmi_escore",    "VMI — Escore padrão"),
        ("vmi_percentil", "VMI — Percentil", 100),
        ("vp_raw",        "Percepção Visual — bruto"),
        ("vp_escore",     "Percepção Visual — padrão"),
        ("vp_percentil",  "Percepção Visual — percentil", 100),
        ("mc_raw",        "Coord. Motora — bruto"),
        ("mc_escore",     "Coord. Motora — padrão"),
        ("mc_percentil",  "Coord. Motora — percentil", 100),
    ]
    secoes = _extrair_secoes(av, campos)
    return "Beery VMI", "Beery-Buktenica Developmental Test of Visual-Motor Integration", secoes


def _config_pedi(av):
    campos = [
        ("fs_autocuidado",        "FS Autocuidado (bruto)", 73),
        ("fs_mobilidade",         "FS Mobilidade (bruto)",  59),
        ("fs_funcao_social",      "FS Função Social (bruto)", 65),
        ("ca_autocuidado",        "CA Autocuidado (0–40)", 40),
        ("ca_mobilidade",         "CA Mobilidade (0–40)",  40),
        ("ca_funcao_social",      "CA Função Social (0–40)", 40),
        ("fs_autocuidado_escala", "FS Autocuidado (escala 0–100)", 100),
        ("fs_mobilidade_escala",  "FS Mobilidade (escala 0–100)",  100),
        ("fs_funcao_social_escala","FS Função Social (escala 0–100)", 100),
    ]
    secoes = _extrair_secoes(av, campos)
    return "PEDI", "Pediatric Evaluation of Disability Inventory", secoes


def _config_vineland3(av):
    campos = [
        ("pont_com",   "Comunicação",                   None),
        ("pont_avd",   "Atividades de Vida Diária",     None),
        ("pont_soc",   "Habilidades Sociais",            None),
        ("pont_hmot",  "Atividade Física",               None),
        ("pont_total", "Composto Adaptativo",            None),
        ("pont_pc_a",  "Problemas de Comportamento — A", None),
        ("pont_pc_b",  "Problemas de Comportamento — B", None),
        ("pont_pc_c",  "Problemas de Comportamento — C", None),
    ]
    secoes = _extrair_secoes(av, campos)
    return "Vineland-3", "Vineland Adaptive Behavior Scales – 3ª edição", secoes


def _config_portage(av):
    campos = [
        ("pont_estimulacao", "Estimulação",      None),
        ("pont_cognitivo",   "Cognitivo",        None),
        ("pont_linguagem",   "Linguagem",        None),
        ("pont_autocuidado", "Autocuidado",      None),
        ("pont_motor",       "Motor",            None),
        ("pont_social",      "Socialização",     None),
        ("pont_total",       "Total",            None),
    ]
    secoes = _extrair_secoes(av, campos)
    return "Guia Portage", "Guia Portage de Educação Pré-Escolar", secoes


def _config_sdq(av):
    campos = [
        ("pont_emocional",          "Sintomas Emocionais",       10),
        ("pont_conduta",            "Problemas de Conduta",      10),
        ("pont_hiperatividade",     "Hiperatividade/Desatenção", 10),
        ("pont_pares",              "Problemas com Colegas",     10),
        ("pont_prossocial",         "Comportamento Prossocial",  10),
        ("pont_total_dificuldades", "Total de Dificuldades",     40),
    ]
    secoes = _extrair_secoes(av, campos)
    respondente = dict(av.RESPONDENTE_CHOICES).get(av.respondente, "")
    return f"SDQ — {respondente}", "Strengths and Difficulties Questionnaire (Goodman, 1997)", secoes


def _config_snap_iv(av):
    campos = [
        ("media_desatencao",     "Desatenção (média 0–3)",                3),
        ("media_hiperatividade", "Hiperatividade / Impulsividade (0–3)",  3),
        ("media_tod",            "TOD (média 0–3)",                       3),
    ]
    secoes = _extrair_secoes(av, campos)
    respondente = dict(av.RESPONDENTE_CHOICES).get(av.respondente, "")
    return f"SNAP-IV — {respondente}", "SNAP-IV (Swanson, Nolan and Pelham Rating Scale)", secoes


def _config_mchat(av):
    class_map = {
        "baixo": "Baixo risco (0–2)",
        "medio": "Médio risco — indicado M-CHAT-R/F (3–7)",
        "alto":  "Alto risco — encaminhar para avaliação (8–20)",
    }
    secoes = [{
        "nome": "Score total (0–20)",
        "valor": av.score_total,
        "maximo": 20,
        "classificacao": class_map.get(av.classificacao, "—"),
    }]
    return "M-CHAT-R", "Modified Checklist for Autism in Toddlers, Revised (2013)", secoes


def _config_cars(av):
    class_map = {
        "sem_autismo":   "Sem Autismo (<30)",
        "leve_moderado": "Autismo Leve-Moderado (30–36,5)",
        "grave":         "Autismo Grave (≥37)",
    }
    secoes = [{
        "nome": "Score total",
        "valor": av.score_total,
        "maximo": 60,
        "classificacao": class_map.get(av.classificacao, "—"),
    }]
    return "CARS-2", "Childhood Autism Rating Scale – 2ª edição (Schopler, 2010)", secoes


def _config_linguagem(av):
    campos = [
        ("pont_recepcao",       "Recepção / Compreensão"),
        ("pont_expressao",      "Expressão Oral"),
        ("pont_pragmatica",     "Pragmática"),
        ("pont_fonologia",      "Fonologia / Articulação"),
        ("pont_fluencia",       "Fluência"),
        ("pont_consciencia_fono","Consciência Fonológica"),
    ]
    secoes = _extrair_secoes(av, campos)
    return "Avaliação de Linguagem", "Checklist clínico de linguagem — Fonoaudiologia", secoes


def _config_alimentacao(av):
    campos = [
        ("pont_variedade",        "Variedade Alimentar"),
        ("pont_sensibilidade",    "Tolerância Sensorial"),
        ("pont_recusa_rituais",   "Comportamento nas Refeições"),
        ("pont_interesse",        "Interesse e Apetite"),
        ("pont_motricidade_oral", "Motricidade Orofacial"),
        ("pont_degluticao",       "Deglutição e Segurança"),
    ]
    secoes = _extrair_secoes(av, campos)
    return "Triagem de Alimentação Seletiva", "Checklist de seletividade alimentar — Fonoaudiologia", secoes


def _config_habitos_orais(av):
    campos = [
        ("pont_respiracao",  "Respiração Nasal"),
        ("pont_succao",      "Sucção Não-Nutritiva"),
        ("pont_mastigacao",  "Mastigação"),
        ("pont_degluticao",  "Padrão de Deglutição"),
        ("pont_postura",     "Postura e Bruxismo"),
    ]
    secoes = _extrair_secoes(av, campos)
    return "Hábitos Orais Deletérios", "Triagem de hábitos orais — Fonoaudiologia", secoes


def _config_voz(av):
    campos = [
        ("pont_funcional", "Funcional"),
        ("pont_fisico",    "Físico"),
        ("pont_emocional", "Emocional"),
    ]
    secoes = _extrair_secoes(av, campos)
    return "Triagem de Voz Infantil", "pVHI adaptado — Fonoaudiologia", secoes


def _config_auditivo(av):
    campos = [
        ("pont_atencao",      "Atenção e Discriminação"),
        ("pont_compreensao",  "Compreensão Auditiva"),
        ("pont_memoria",      "Memória Auditiva"),
        ("pont_figura_fundo", "Figura-Fundo"),
        ("pont_impacto",      "Impacto Funcional"),
    ]
    secoes = _extrair_secoes(av, campos)
    return "Triagem de Processamento Auditivo", "Triagem comportamental de processamento auditivo central", secoes


def _config_idv10(av):
    campos = [
        ("pont_comunicativo", "Impacto Comunicativo"),
        ("pont_fisico",       "Aspectos Físicos"),
    ]
    secoes = _extrair_secoes(av, campos)
    return "IDV-10 — Desvantagem Vocal", "Índice de Desvantagem Vocal – VHI-10 adaptado", secoes


def _config_desenvolvimento(av):
    campos = [
        ("pont_motor_grosso",  "Motor Grosso"),
        ("pont_motor_fino",    "Motor Fino"),
        ("pont_linguagem",     "Linguagem"),
        ("pont_social",        "Social / Emocional"),
        ("pont_cognitivo",     "Cognitivo"),
    ]
    secoes = _extrair_secoes(av, campos)
    return "Marcos do Desenvolvimento Infantil", "Checklist de marcos — Pediatria / Neuropediatria", secoes


def _config_sono(av):
    campos = [
        ("pont_inicio",       "Início do Sono"),
        ("pont_manutencao",   "Manutenção do Sono"),
        ("pont_sonolencia",   "Sonolência Diurna"),
        ("pont_resistencia",  "Resistência ao Sono"),
        ("pont_ansiedade",    "Ansiedade do Sono"),
        ("pont_ronco_apneia", "Ronco / Apneia"),
        ("pont_total",        "Score Total"),
    ]
    secoes = _extrair_secoes(av, campos)
    return "Avaliação do Sono Infantil", "Triagem baseada em BEARS / CSHQ — Pediatria", secoes


def _config_habilidades(av):
    campos = [
        ("pont_comunicacao",   "Comunicação Funcional"),
        ("pont_autocuidado",   "Autocuidado"),
        ("pont_socializacao",  "Socialização"),
        ("pont_autonomia",     "Autonomia"),
        ("pont_comportamento", "Comportamento Adaptativo"),
    ]
    secoes = _extrair_secoes(av, campos)
    return "Habilidades Adaptativas", "Checklist de habilidades adaptativas — ABA", secoes


def _config_comportamento(av):
    campos = [
        ("pont_iniciacao",     "Iniciação"),
        ("pont_manutencao",    "Manutenção de Tarefa"),
        ("pont_flexibilidade", "Flexibilidade / Transições"),
        ("pont_generalizacao", "Generalização"),
        ("pont_comunicacao",   "Comunicação Funcional"),
        ("pont_autocontrole",  "Autocontrole"),
    ]
    secoes = _extrair_secoes(av, campos)
    return "Avaliação de Comportamento Funcional", "Rastreio de comportamento funcional — ABA", secoes


def _config_cognitivo(av):
    campos = [
        ("pont_atencao_sustentada", "Atenção Sustentada"),
        ("pont_atencao_seletiva",   "Atenção Seletiva"),
        ("pont_memoria_trabalho",   "Memória de Trabalho"),
        ("pont_memoria_episodica",  "Memória Episódica"),
        ("pont_funcoes_executivas", "Funções Executivas"),
        ("pont_visoespacial",       "Habilidades Visoespaciais"),
    ]
    secoes = _extrair_secoes(av, campos)
    return "Rastreio Cognitivo", "Rastreio neuropsicológico — Neuropsicologia", secoes


def _config_psicopedagogica(av):
    campos = [
        ("pont_leitura",    "Leitura"),
        ("pont_escrita",    "Escrita"),
        ("pont_matematica", "Matemática"),
        ("pont_atencao",    "Atenção Escolar"),
        ("pont_comportamento_escolar", "Comportamento Escolar"),
    ]
    secoes = _extrair_secoes(av, campos)
    return "Avaliação Psicopedagógica", "Rastreio psicopedagógico — Psicopedagogia", secoes


# ─── Mapeamento tipo → (Model, config_fn, url_voltar) ─────────────────────────

LAUDO_MAP = {
    "spm":          (AvaliacaoSPM,                    _config_spm,            "spm_resultado"),
    "vineland":     (AvaliacaoVineland,               _config_vineland,       "vineland_resultado"),
    "escolar":      (AvaliacaoEscolar,                _config_escolar,        "escolar_resultado"),
    "bebe":         (AvaliacaoBebe,                   _config_bebe,           "bebe_resultado"),
    "edm":          (AvaliacaoEDM,                    _config_edm,            "edm_resultado"),
    "mabc2":        (AvaliacaoMABC2,                  _config_mabc2,          "mabc2_resultado"),
    "beery":        (AvaliacaoBeery,                  _config_beery,          "beery_resultado"),
    "pedi":         (AvaliacaoPEDI,                   _config_pedi,           "pedi_resultado"),
    "vineland3":    (AvaliacaoVineland3,              _config_vineland3,      "vineland3_resultado"),
    "portage":      (AvaliacaoPortage,                _config_portage,        "portage_resultado"),
    "sdq":          (AvaliacaoSDQ,                    _config_sdq,            "sdq_resultado"),
    "snap_iv":      (AvaliacaoSNAPIV,                 _config_snap_iv,        "snap_iv_resultado"),
    "mchat":        (AvaliacaoMCHAT,                  _config_mchat,          "mchat_resultado"),
    "cars":         (AvaliacaoCARS,                   _config_cars,           "cars_resultado"),
    "linguagem":    (AvaliacaoLinguagem,              _config_linguagem,      "linguagem_resultado"),
    "alimentacao":  (AvaliacaoAlimentacao,            _config_alimentacao,    "alimentacao_resultado"),
    "habitos":      (AvaliacaoHabitosOrais,           _config_habitos_orais,  "habitos_resultado"),
    "voz":          (AvaliacaoVozInfantil,            _config_voz,            "voz_resultado"),
    "auditivo":     (AvaliacaoProcessamentoAuditivo,  _config_auditivo,       "auditivo_resultado"),
    "idv":          (AvaliacaoIDV10,                  _config_idv10,          "idv_resultado"),
    "desenvolvimento": (AvaliacaoDesenvolvimento,     _config_desenvolvimento,"desenvolvimento_resultado"),
    "sono":         (AvaliacaoSono,                   _config_sono,           "sono_resultado"),
    "habilidades":  (AvaliacaoHabilidadesAdaptativas, _config_habilidades,    "habilidades_resultado"),
    "comportamento":(AvaliacaoComportamentoFuncional, _config_comportamento,  "comportamento_resultado"),
    "cognitivo":    (AvaliacaoRastreioCognitivo,      _config_cognitivo,      "cognitivo_resultado"),
    "psicopedagogica":(AvaliacaoPsicopedagogica,      _config_psicopedagogica,"psicopedagogica_resultado"),
}


# ─── View genérica ────────────────────────────────────────────────────────────

@login_required
def laudo_generico(request, tipo, avaliacao_id):
    Model, config_fn, url_resultado_name = LAUDO_MAP[tipo]
    avaliacao = get_object_or_404(Model, uuid=avaliacao_id, paciente__medico=request.user)
    paciente  = avaliacao.paciente

    nome_instrumento, referencia, secoes = config_fn(avaliacao)

    return render(request, "questionario/avaliacoes/laudo_generico.html", {
        "avaliacao":        avaliacao,
        "paciente":         paciente,
        "nome_instrumento": nome_instrumento,
        "referencia":       referencia,
        "secoes":           secoes,
        "idade_str":        _idade_str(paciente.data_nascimento),
        "data_hoje":        datetime.date.today().strftime("%d/%m/%Y"),
        "url_resultado":    url_resultado_name,
        "tipo":             tipo,
    })
