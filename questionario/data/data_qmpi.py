# QMPI — Questionário de Morbidade Psiquiátrica Infantil
# 5 subescalas, escala 0-3

QMPI_ITENS = [
    {"numero": 1,  "subescala": "ansiedade", "texto": "Tem medos excessivos ou desnecessários"},
    {"numero": 2,  "subescala": "ansiedade", "texto": "Fica muito ansioso(a) em situações novas"},
    {"numero": 3,  "subescala": "ansiedade", "texto": "Queixa-se de dores físicas sem causa médica"},
    {"numero": 4,  "subescala": "ansiedade", "texto": "Tem dificuldade em separar-se dos pais"},
    {"numero": 5,  "subescala": "ansiedade", "texto": "Apresenta pesadelos frequentes"},
    {"numero": 6,  "subescala": "ansiedade", "texto": "Tem dificuldade para dormir sozinho(a)"},
    {"numero": 7,  "subescala": "depressao", "texto": "Apresenta tristeza ou humor deprimido frequente"},
    {"numero": 8,  "subescala": "depressao", "texto": "Chora com muita frequência"},
    {"numero": 9,  "subescala": "depressao", "texto": "Perdeu interesse em atividades que antes gostava"},
    {"numero": 10, "subescala": "depressao", "texto": "Apresenta baixa autoestima ou sentimentos de inutilidade"},
    {"numero": 11, "subescala": "depressao", "texto": "Tem alterações no sono (muita sonolência ou insônia)"},
    {"numero": 12, "subescala": "tdah", "texto": "Tem dificuldade em manter atenção nas atividades"},
    {"numero": 13, "subescala": "tdah", "texto": "É muito agitado(a) ou não consegue ficar quieto(a)"},
    {"numero": 14, "subescala": "tdah", "texto": "Age antes de pensar (impulsivo)"},
    {"numero": 15, "subescala": "tdah", "texto": "Tem dificuldades na escola por falta de atenção"},
    {"numero": 16, "subescala": "tdah", "texto": "Interrompe conversas ou atividades dos outros"},
    {"numero": 17, "subescala": "conduta", "texto": "Tem explosões de raiva ou birras frequentes"},
    {"numero": 18, "subescala": "conduta", "texto": "Desobedece regras consistentemente"},
    {"numero": 19, "subescala": "conduta", "texto": "Agride fisicamente outras crianças ou adultos"},
    {"numero": 20, "subescala": "conduta", "texto": "Destrói objetos intencionalmente"},
    {"numero": 21, "subescala": "conduta", "texto": "Mente ou engana com frequência"},
    {"numero": 22, "subescala": "autismo", "texto": "Tem dificuldade em fazer amigos da mesma idade"},
    {"numero": 23, "subescala": "autismo", "texto": "Apresenta movimentos ou falas repetitivas"},
    {"numero": 24, "subescala": "autismo", "texto": "Tem dificuldade em entender as intenções dos outros"},
    {"numero": 25, "subescala": "autismo", "texto": "Insiste em rotinas e resiste a mudanças"},
]

QMPI_SUBESCALAS = {
    "ansiedade": {"nome": "Ansiedade",        "cor": "#E74C3C", "campo": "pont_ansiedade", "itens": [1, 2, 3, 4, 5, 6]},
    "depressao": {"nome": "Depressão",        "cor": "#9B59B6", "campo": "pont_depressao", "itens": [7, 8, 9, 10, 11]},
    "tdah":      {"nome": "TDAH/Atenção",     "cor": "#3498DB", "campo": "pont_tdah",      "itens": [12, 13, 14, 15, 16]},
    "conduta":   {"nome": "Conduta/Oposição", "cor": "#E67E22", "campo": "pont_conduta",   "itens": [17, 18, 19, 20, 21]},
    "autismo":   {"nome": "Sinais de TEA",    "cor": "#27AE60", "campo": "pont_autismo",   "itens": [22, 23, 24, 25]},
}

QMPI_OPCOES = [
    {"valor": 0, "label": "Nunca"},
    {"valor": 1, "label": "Às vezes"},
    {"valor": 2, "label": "Frequentemente"},
    {"valor": 3, "label": "Sempre"},
]
QMPI_CORTE = 3  # pontuação >= 3 por subescala indica rastreio positivo
