# Perfil Sensorial 2 — Criança Pequena (7–35 meses) — Winnie Dunn
# Escala: 5=Quase sempre, 4=Frequentemente, 3=Metade do tempo,
#         2=Ocasionalmente, 1=Quase nunca, 0=Não se aplica

# Itens marcados com * não fazem parte da pontuação bruta de sua seção
ITENS_EXTRAS_PS2_CP = [24, 25, 32, 33, 34, 35, 41]

SECOES_PS2_CP = [
    {"id": "geral",          "nome": "Processamento GERAL",                 "itens": list(range(1, 11))},
    {"id": "auditivo",       "nome": "Processamento AUDITIVO",               "itens": list(range(11, 18))},
    {"id": "visual",         "nome": "Processamento VISUAL",                 "itens": list(range(18, 26)), "extras": [24, 25]},
    {"id": "tato",           "nome": "Processamento do TATO",                "itens": list(range(26, 36)), "extras": [32, 33, 34, 35]},
    {"id": "movimentos",     "nome": "Processamento de MOVIMENTOS",          "itens": list(range(36, 42)), "extras": [41]},
    {"id": "oral",           "nome": "Processamento de SENSIBILIDADE ORAL",  "itens": list(range(42, 49))},
    {"id": "comportamental", "nome": "Respostas COMPORTAMENTAIS",            "itens": list(range(49, 55))},
]

PERGUNTAS_PS2_CP = {
    # GERAL
    1:  "precisa de uma rotina para permanecer satisfeito(a) ou calmo(a).",
    2:  "age de uma forma que interfere nas programações e planos da família.",
    3:  "resiste em brincar no meio de outras crianças.",
    4:  "leva mais tempo do que crianças da mesma idade para responder a perguntas ou ações.",
    5:  "se afasta de situações.",
    6:  "tem um padrão de sono imprevisível.",
    7:  "tem um padrão de alimentação imprevisível.",
    8:  "é despertado(a) facilmente.",
    9:  "não faz contato visual comigo durante interações no dia a dia.",
    10: "fica ansioso(a) em situações novas.",
    # AUDITIVO
    11: "presta atenção apenas se eu falar alto.",
    12: "presta atenção apenas quando eu o toco (e a audição é normal).",
    13: "se assusta facilmente com sons, em comparação com crianças da mesma idade (por exemplo, cachorro latindo, crianças gritando).",
    14: "se distrai em condições barulhentas.",
    15: "ignora sons, incluindo a minha voz.",
    16: "fica chateado(a) ou tenta escapar de condições barulhentas.",
    17: "leva bastante tempo para responder ao próprio nome.",
    # VISUAL
    18: "gosta de olhar para objetos em movimento ou rotação (por exemplo, ventiladores de teto, brinquedos com rodas).",
    19: "gosta de olhar para objetos brilhantes.",
    20: "é atraído(a) por telas de TV ou de computador com desenhos intensamente coloridos, em ritmo acelerado.",
    21: "se assusta com luzes brilhantes ou imprevisíveis (por exemplo, ao se deslocar de um ambiente interno a um externo).",
    22: "se incomoda com luzes brilhantes (por exemplo, se esconde da luz solar que reluz através da janela do carro).",
    23: "se incomoda mais com luzes brilhantes do que outras crianças da mesma idade.",
    24: "empurra brinquedos de coloração brilhante para longe de si.*",
    25: "não responde à sua imagem no espelho.*",
    # TATO
    26: "fica incomodado(a) quando suas unhas são aparadas.",
    27: "resiste a ser abraçado.",
    28: "se incomoda ao se deslocar entre espaços com temperaturas muito diferentes (por exemplo, mais frio, mais morno).",
    29: "se afasta após ter contato com superfícies ásperas, frias ou grudentas (por exemplo, carpete, bancadas).",
    30: "esbarra em coisas, sem conseguir notar objetos ou pessoas no caminho.",
    31: "remove roupas ou resiste a vesti-las.",
    32: "gosta de brincar de espirrar água durante o banho ou na natação.*",
    33: "se incomoda se suas próprias roupas, mãos ou rosto estão sujos.*",
    34: "demonstra ansiedade ao caminhar ou engatinhar em certas superfícies (por exemplo, grama, areia, carpete, azulejos).*",
    35: "se afasta de toques inesperados.*",
    # MOVIMENTOS
    36: "gosta de atividade física (por exemplo, pular, ser erguido(a) bem alto).",
    37: "gosta de atividades rítmicas (por exemplo, balançar, ser embalado, passeios de carro).",
    38: "se arrisca ao se movimentar ou escalar.",
    39: "se incomoda quando colocado(a) de barriga para cima (por exemplo, para ser trocado(a)).",
    40: "parece ter propensão para acidentes ou ser desastrado(a).",
    41: "reclama quando é movimentado(a) (por exemplo, ao caminhar, ao ser entregue para outra pessoa).*",
    # ORAL
    42: "mostra uma aversão evidente à maioria dos alimentos, com exceção de algumas opções.",
    43: "baba.",
    44: "prefere uma textura de alimentos (por exemplo, macio, crocante).",
    45: "bebe para se acalmar.",
    46: "tem ânsia de vômito com alimentos ou bebidas.",
    47: "mantém a comida nas bochechas antes de engolir.",
    48: "apresenta dificuldade na transição do leite materno para a alimentação sólida.",
    # COMPORTAMENTAL
    49: "faz birra.",
    50: "é muito apegado e dependente.",
    51: "se acalma somente quando é segurado(a) no colo.",
    52: "mostra inquietude ou irritabilidade.",
    53: "se incomoda com novos ambientes.",
    54: "fica tão incomodado(a) em novos ambientes que se torna difícil de acalmá-lo(a).",
}

QUADRANTE_PS2_CP = {
    1: "SN", 2: "SN", 3: "EV", 4: None, 5: None, 6: None, 7: None, 8: None, 9: "OB", 10: "EV",
    11: "OB", 12: "OB", 13: "SN", 14: "OB", 15: "OB", 16: "SN", 17: None,
    18: "EX", 19: "EX", 20: "EX", 21: None, 22: None, 23: "OB", 24: "OB", 25: "OB",
    26: "SN", 27: "EV", 28: "EV", 29: "EV", 30: "OB", 31: "SN",
    32: "EX", 33: "EV", 34: "SN", 35: "EV",
    36: "EX", 37: "EX", 38: "EX", 39: "SN", 40: "OB", 41: "SN",
    42: "EV", 43: None, 44: "SN", 45: "OB", 46: "SN", 47: None, 48: "SN",
    49: "EV", 50: None, 51: None, 52: "SN", 53: "EV", 54: "EV",
}

# Somente itens não-extras contribuem para os quadrantes
ITENS_PONTUADOS_PS2_CP = [i for i in range(1, 55) if i not in ITENS_EXTRAS_PS2_CP]

ITENS_EX_CP = [i for i in ITENS_PONTUADOS_PS2_CP if QUADRANTE_PS2_CP.get(i) == "EX"]
ITENS_EV_CP = [i for i in ITENS_PONTUADOS_PS2_CP if QUADRANTE_PS2_CP.get(i) == "EV"]
ITENS_SN_CP = [i for i in ITENS_PONTUADOS_PS2_CP if QUADRANTE_PS2_CP.get(i) == "SN"]
ITENS_OB_CP = [i for i in ITENS_PONTUADOS_PS2_CP if QUADRANTE_PS2_CP.get(i) == "OB"]

TOTAL_ITENS_PS2_CP = 54

OPCOES_PS2 = [
    (5, "Quase sempre (90% ou mais)"),
    (4, "Frequentemente (75%)"),
    (3, "Metade do tempo (50%)"),
    (2, "Ocasionalmente (25%)"),
    (1, "Quase nunca (10% ou menos)"),
]


def calcular_pontuacao_ps2_cp(respostas: dict) -> dict:
    """respostas: {numero_item: valor (1-5)}, extras excluídos automaticamente."""
    result = {}
    for secao in SECOES_PS2_CP:
        extras = secao.get("extras", [])
        pontuados = [i for i in secao["itens"] if i not in extras]
        result[secao["id"]] = sum(respostas.get(i, 0) for i in pontuados)
    result["EX"] = sum(respostas.get(i, 0) for i in ITENS_EX_CP)
    result["EV"] = sum(respostas.get(i, 0) for i in ITENS_EV_CP)
    result["SN"] = sum(respostas.get(i, 0) for i in ITENS_SN_CP)
    result["OB"] = sum(respostas.get(i, 0) for i in ITENS_OB_CP)
    return result
