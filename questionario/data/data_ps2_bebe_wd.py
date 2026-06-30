# Perfil Sensorial 2 — Bebê (0–6 meses) — Winnie Dunn
# Escala: 5=Quase sempre, 4=Frequentemente, 3=Metade do tempo,
#         2=Ocasionalmente, 1=Quase nunca, 0=Não se aplica (excluído)

SECOES_PS2_BEBE = [
    {"id": "geral",      "nome": "Processamento GERAL",            "itens": list(range(1, 9))},
    {"id": "auditivo",   "nome": "Processamento AUDITIVO",          "itens": list(range(9, 13))},
    {"id": "visual",     "nome": "Processamento VISUAL",            "itens": list(range(13, 17))},
    {"id": "tato",       "nome": "Processamento do TATO",           "itens": list(range(17, 20))},
    {"id": "movimentos", "nome": "Processamento de MOVIMENTOS",     "itens": list(range(20, 24))},
    {"id": "oral",       "nome": "Processamento de SENSIBILIDADE ORAL", "itens": [24, 25]},
]

PERGUNTAS_PS2_BEBE = {
    # GERAL
    1:  "permanece quieto(a) e calmo(a) em um ambiente ativo, em comparação com outros bebês.",
    2:  "não percebe se as pessoas estão entrando ou saindo do cômodo.",
    3:  "precisa da mesma rotina para permanecer satisfeito(a) e calmo(a).",
    4:  "age de uma forma que interfere nas programações e planos da família.",
    5:  "precisa de ajuda para conseguir dormir.",
    6:  "é irritável em comparação com outros bebês.",
    7:  "dorme mais do que outros bebês.",
    8:  "presta atenção apenas quando eu o(a) toco (e a audição é normal).",
    # AUDITIVO
    9:  "gosta de fazer sons com a boca (por exemplo, barulhos com a língua e a boca, fazer barulhos com os lábios, murmúrios).",
    10: "me ignora quando estou falando.",
    11: "se incomoda com sons cotidianos repentinos.",
    12: "fica mais animado(a) e entretido(a) com músicas, conversas ou brinquedos sonoros.",
    # VISUAL
    13: "não faz contato visual comigo durante interações no dia a dia.",
    14: "desvia o olhar de brinquedos ou rostos.",
    15: "desvia o olhar ou fica inquieto(a) em ambientes barulhentos ou com brinquedos barulhentos.",
    16: "pisca bastante quando objetos ou pessoas se aproximam do seu rosto.",
    # TATO
    17: "fica incomodado(a) quando suas unhas são aparadas.",
    18: "precisa ser envolto(a) firmemente em uma manta ou agasalhado(a) para relaxar.",
    19: "se assusta com diferenças na textura (por exemplo, na grama, em tapetes, em cobertores).",
    # MOVIMENTOS
    20: "gosta de atividades rítmicas (por exemplo, balançar, ser embalado, passeios de carro).",
    21: "resiste quando sua cabeça é inclinada para trás durante o banho.",
    22: "chora ou reclama diante de movimentações cotidianas.",
    23: "precisa de mais apoio para a cabeça quando é segurado(a) no colo, em comparação com outros bebês.",
    # ORAL
    24: "tem dificuldade para fechar a boca ao mamar no peito ou mamadeira (por exemplo, não faz a pega no peito).",
    25: "gosta de fazer movimentos ou sons com a boca.",
}

# Quadrante de cada item
QUADRANTE_PS2_BEBE = {
    1: "OB", 2: "OB", 3: "SN", 4: None, 5: "SN",
    6: "SN", 7: None, 8: "OB",
    9: "EX", 10: None, 11: None, 12: "EX",
    13: "EV", 14: "EV", 15: "EV", 16: "SN",
    17: None, 18: "SN", 19: "SN",
    20: "EX", 21: "EV", 22: None, 23: "OB",
    24: None, 25: "EX",
}

ITENS_EX_BEBE = [i for i, q in QUADRANTE_PS2_BEBE.items() if q == "EX"]
ITENS_EV_BEBE = [i for i, q in QUADRANTE_PS2_BEBE.items() if q == "EV"]
ITENS_SN_BEBE = [i for i, q in QUADRANTE_PS2_BEBE.items() if q == "SN"]
ITENS_OB_BEBE = [i for i, q in QUADRANTE_PS2_BEBE.items() if q == "OB"]

TOTAL_ITENS_PS2_BEBE = 25

OPCOES_PS2 = [
    (5, "Quase sempre (90% ou mais)"),
    (4, "Frequentemente (75%)"),
    (3, "Metade do tempo (50%)"),
    (2, "Ocasionalmente (25%)"),
    (1, "Quase nunca (10% ou menos)"),
]


def calcular_pontuacao_ps2_bebe(respostas: dict) -> dict:
    """respostas: {numero_item: valor (1-5)}"""
    result = {}
    for secao in SECOES_PS2_BEBE:
        result[secao["id"]] = sum(respostas.get(i, 0) for i in secao["itens"])
    result["EX"] = sum(respostas.get(i, 0) for i in ITENS_EX_BEBE)
    result["EV"] = sum(respostas.get(i, 0) for i in ITENS_EV_BEBE)
    result["SN"] = sum(respostas.get(i, 0) for i in ITENS_SN_BEBE)
    result["OB"] = sum(respostas.get(i, 0) for i in ITENS_OB_BEBE)
    return result
