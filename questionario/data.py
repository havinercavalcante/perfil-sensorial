# CeciSys - Dados das Perguntas e Pontuação

SECOES = [
    {"id": "auditiva", "nome": "Processamento AUDITIVO", "itens": list(range(1, 9)), "max": 40},
    {"id": "visual", "nome": "Processamento VISUAL", "itens": list(range(9, 16)), "max": 30,
     "nota": "Item 15 não faz parte da Pontuação bruta VISUAL"},
    {"id": "tato", "nome": "Processamento do TATO", "itens": list(range(16, 27)), "max": 55},
    {"id": "movimento", "nome": "Processamento de MOVIMENTOS", "itens": list(range(27, 35)), "max": 40},
    {"id": "posicao", "nome": "Processamento da POSIÇÃO DO CORPO", "itens": list(range(35, 43)), "max": 40},
    {"id": "oral", "nome": "Processamento de SENSIBILIDADE ORAL", "itens": list(range(43, 53)), "max": 50},
    {"id": "conduta", "nome": "CONDUTA associada ao processamento sensorial", "itens": list(range(53, 62)), "max": 45},
    {"id": "socioemocional", "nome": "Respostas SOCIOEMOCIONAIS", "itens": list(range(62, 76)), "max": 70},
    {"id": "atencao", "nome": "Respostas de ATENÇÃO", "itens": list(range(76, 87)), "max": 50,
     "nota": "Item 86 não faz parte da Pontuação bruta de ATENÇÃO"},
]

# Itens excluídos da pontuação bruta
ITENS_EXCLUIDOS = [15, 86]

# Quadrante de cada pergunta: EX=Exploração, EV=Esquiva, SN=Sensibilidade, OB=Observação
QUADRANTE = {
    1: "EV", 2: "EV", 3: "SN", 4: "SN", 5: "EV", 6: "SN", 7: "SN", 8: "OB",
    9: "SN", 10: None, 11: None, 12: "OB", 13: "SN", 14: "EX", 15: "EV",
    16: "SN", 17: None, 18: "EV", 19: "SN", 20: "SN", 21: "EX", 22: "EX",
    23: "OB", 24: "OB", 25: "EX", 26: "OB",
    27: "EX", 28: "EX", 29: None, 30: "EX", 31: "EX", 32: "EX", 33: "OB", 34: "OB",
    35: "OB", 36: "OB", 37: "OB", 38: "OB", 39: "OB", 40: "OB", 41: "EX", 42: None,
    43: None, 44: "SN", 45: "SN", 46: "SN", 47: "SN", 48: "EX", 49: "EX", 50: "EX", 51: "EX", 52: "SN",
    53: "OB", 54: "OB", 55: "EX", 56: "EX", 57: "OB", 58: "EV", 59: "EV", 60: "EX", 61: "EV",
    62: "OB", 63: "EV", 64: "EV", 65: "EV", 66: "EV", 67: "EV", 68: "EV", 69: "SN",
    70: "EV", 71: "EV", 72: "EV", 73: "SN", 74: "EV", 75: "EV",
    76: "OB", 77: "SN", 78: "SN", 79: "OB", 80: "OB", 81: "EV", 82: "EX", 83: "EX",
    84: "SN", 85: "OB", 86: "OB",
}

# Itens por quadrante (para cálculo)
ITENS_EX = [14, 21, 22, 25, 27, 28, 30, 31, 32, 41, 48, 49, 50, 51, 55, 56, 60, 82, 83]
ITENS_EV = [1, 2, 5, 15, 18, 58, 59, 61, 63, 64, 65, 66, 67, 68, 70, 71, 72, 74, 75, 81]
ITENS_SN = [3, 4, 6, 7, 9, 13, 16, 19, 20, 44, 45, 46, 47, 52, 69, 73, 77, 78, 84]
ITENS_OB = [8, 12, 23, 24, 26, 33, 34, 35, 36, 37, 38, 39, 40, 53, 54, 57, 62, 76, 79, 80, 85, 86]

QUADRANTES_CONFIG = {
    "EX": {"nome": "Exploração", "subtitulo": "Criança exploradora", "max": 95, "cor": "#E8793A",
           "faixas": [(0, 6, "Muito menos"), (7, 19, "Menos"), (20, 47, "Típico"), (48, 60, "Mais"), (61, 95, "Muito mais")]},
    "EV": {"nome": "Esquiva", "subtitulo": "Criança que se esquiva", "max": 100, "cor": "#6B8DD6",
           "faixas": [(0, 7, "Muito menos"), (8, 20, "Menos"), (21, 46, "Típico"), (47, 59, "Mais"), (60, 100, "Muito mais")]},
    "SN": {"nome": "Sensibilidade", "subtitulo": "Criança sensível", "max": 95, "cor": "#E8B84B",
           "faixas": [(0, 6, "Muito menos"), (7, 17, "Menos"), (18, 42, "Típico"), (43, 53, "Mais"), (54, 95, "Muito mais")]},
    "OB": {"nome": "Observação", "subtitulo": "Criança observadora", "max": 110, "cor": "#7DB87D",
           "faixas": [(0, 6, "Muito menos"), (7, 18, "Menos"), (19, 43, "Típico"), (44, 55, "Mais"), (56, 110, "Muito mais")]},
}

SECOES_CONFIG = {
    "auditiva":       {"nome": "Auditivo",        "max": 40,  "faixas": [(0,2,"Muito menos"),(3,9,"Menos"),(10,24,"Típico"),(25,31,"Mais"),(32,40,"Muito mais")]},
    "visual":         {"nome": "Visual",           "max": 30,  "faixas": [(0,4,"Muito menos"),(5,8,"Menos"),(9,17,"Típico"),(18,21,"Mais"),(22,30,"Muito mais")]},
    "tato":           {"nome": "Tato",             "max": 55,  "faixas": [(0,0,"Muito menos"),(1,7,"Menos"),(8,21,"Típico"),(22,28,"Mais"),(29,55,"Muito mais")]},
    "movimento":      {"nome": "Movimento",        "max": 40,  "faixas": [(0,1,"Muito menos"),(2,6,"Menos"),(7,18,"Típico"),(19,24,"Mais"),(25,40,"Muito mais")]},
    "posicao":        {"nome": "Posição do corpo", "max": 40,  "faixas": [(0,0,"Muito menos"),(1,4,"Menos"),(5,15,"Típico"),(16,19,"Mais"),(20,40,"Muito mais")]},
    "oral":           {"nome": "Oral",             "max": 50,  "faixas": [(0,0,"Muito menos"),(1,7,"Menos"),(8,24,"Típico"),(25,32,"Mais"),(33,50,"Muito mais")]},
    "conduta":        {"nome": "Conduta",          "max": 45,  "faixas": [(0,1,"Muito menos"),(2,8,"Menos"),(9,22,"Típico"),(23,29,"Mais"),(30,45,"Muito mais")]},
    "socioemocional": {"nome": "Socioemocional",   "max": 70,  "faixas": [(0,2,"Muito menos"),(3,12,"Menos"),(13,31,"Típico"),(32,41,"Mais"),(42,70,"Muito mais")]},
    "atencao":        {"nome": "Atenção",          "max": 50,  "faixas": [(0,0,"Muito menos"),(1,8,"Menos"),(9,24,"Típico"),(25,31,"Mais"),(32,50,"Muito mais")]},
}

PERGUNTAS = {
    1: "Reage intensamente a sons inesperados ou barulhentos (por exemplo, sirenes, cachorro latindo, secador de cabelo).",
    2: "Coloca as mãos sobre os ouvidos para protegê-los do som.",
    3: "Tem dificuldade em concluir tarefas quando há música tocando ou a TV está ligada.",
    4: "Se distrai quando há muito barulho ao redor.",
    5: "Torna-se improdutivo(a) com ruídos de fundo (por exemplo, ventilador, geladeira).",
    6: "Para de prestar atenção em mim ou parece que me ignora.",
    7: "Parece não ouvir quando eu o(a) chamo por seu nome (mesmo com sua audição sendo normal).",
    8: "Gosta de barulhos estranhos ou faz barulho(s) para se divertir.",
    9: "Prefere brincar ou fazer tarefas em condições de pouca luz.",
    10: "Prefere vestir-se com roupas de cores brilhantes ou estampadas.",
    11: "Se diverte ao olhar para detalhes visuais em objetos.",
    12: "Precisa de ajuda para encontrar objetos que são óbvios para outros.",
    13: "Se incomoda mais com luzes brilhantes do que outras crianças da mesma idade.",
    14: "Observa as pessoas conforme elas se movem ao redor da sala.",
    15: "Se incomoda com luzes brilhantes (por exemplo, se esconde da luz solar que reluz através da janela do carro).*",
    16: "Mostra desconforto durante momentos de cuidado pessoal (por exemplo, briga ou chora durante o corte de cabelo, lavagem do rosto, corte das unhas das mãos).",
    17: "Se irrita com o uso de sapatos ou meias.",
    18: "Mostra uma resposta emocional ou agressiva ao ser tocado(a).",
    19: "Fica ansioso(a) quando fica de pé em proximidade a outros (por exemplo, em uma fila).",
    20: "Esfrega ou coça uma parte do corpo que foi tocada.",
    21: "Toca as pessoas ou objetos a ponto de incomodar outros.",
    22: "Exibe a necessidade de tocar brinquedos, superfícies ou texturas (por exemplo, quer obter a sensação de tudo ao redor).",
    23: "Parece não ter consciência quanto à dor.",
    24: "Parece não ter consciência quanto a mudanças de temperatura.",
    25: "Toca pessoas e objetos mais do que crianças da mesma idade.",
    26: "Parece alheio(a) quanto ao fato de suas mãos ou face estarem sujas.",
    27: "Busca movimentar-se até o ponto que interfere com rotinas diárias (por exemplo, não consegue ficar quieto, demonstra inquietude).",
    28: "Faz movimento de balançar na cadeira, no chão ou enquanto está em pé.",
    29: "Hesita subir ou descer calçadas ou degraus (por exemplo, é cauteloso, para antes de se movimentar).",
    30: "Fica animado(a) durante tarefas que envolvem movimento.",
    31: "Se arrisca ao se movimentar ou escalar de modo perigoso.",
    32: "Procura oportunidades para cair sem se importar com a própria segurança (por exemplo, cai de propósito).",
    33: "Perde o equilíbrio inesperadamente ao caminhar sobre uma superfície irregular.",
    34: "Esbarra em coisas, sem conseguir notar objetos ou pessoas no caminho.",
    35: "Move-se de modo rígido.",
    36: "Fica cansado(a) facilmente, principalmente quando está em pé ou mantendo o corpo em uma posição.",
    37: "Parece ter músculos fracos.",
    38: "Se apoia para se sustentar (por exemplo, segura a cabeça com as mãos, apoia-se em uma parede).",
    39: "Se segura a objetos, paredes ou corrimões mais do que as crianças da mesma idade.",
    40: "Ao andar, faz barulho, como se os pés fossem pesados.",
    41: "Se inclina para se apoiar em móveis ou em outras pessoas.",
    42: "Precisa de cobertores pesados para dormir.",
    43: "Fica com ânsia de vômito facilmente com certas texturas de alimentos ou utensílios alimentares na boca.",
    44: "Rejeita certos gostos ou cheiros de comida que são, normalmente, parte de dietas de crianças.",
    45: "Se alimenta somente de certos sabores (por exemplo, doce, salgado).",
    46: "Limita-se quanto a certas texturas de alimentos.",
    47: "É exigente para comer, principalmente com relação às texturas de alimentos.",
    48: "Cheira objetos não comestíveis.",
    49: "Mostra uma forte preferência por certos sabores.",
    50: "Deseja intensamente certos alimentos, gostos ou cheiros.",
    51: "Coloca objetos na boca (por exemplo, lápis, mãos).",
    52: "Morde a língua ou lábios mais do que as crianças da mesma idade.",
    53: "Parece propenso(a) a acidentes.",
    54: "Se apressa em atividades de colorir, escrever ou desenhar.",
    55: "Se expõe a riscos excessivos (por exemplo, sobe alto em uma árvore, salta de móveis altos) que comprometem sua própria segurança.",
    56: "Parece ser mais ativo(a) do que crianças da mesma idade.",
    57: "Faz as coisas de uma maneira mais difícil do que o necessário (por exemplo, perde tempo, move-se lentamente).",
    58: "Pode ser teimoso(a) e não cooperativo(a).",
    59: "Faz birra.",
    60: "Parece se divertir quando cai.",
    61: "Resiste ao contato visual comigo ou com outros.",
    62: "Parece ter baixa autoestima (por exemplo, dificuldade de gostar de si mesmo(a)).",
    63: "Precisa de apoio positivo para enfrentar situações desafiadoras.",
    64: "É sensível às críticas.",
    65: "Possui medos definidos e previsíveis.",
    66: "Se expressa sentindo-se como um fracasso.",
    67: "É demasiadamente sério(a).",
    68: "Tem fortes explosões emocionais quando não consegue concluir uma tarefa.",
    69: "Tem dificuldade de interpretar linguagem corporal ou expressões faciais.",
    70: "Fica frustrado(a) facilmente.",
    71: "Possui medos que interferem nas rotinas diárias.",
    72: "Fica angustiado(a) com mudanças nos planos, rotinas ou expectativas.",
    73: "Precisa de mais proteção contra acontecimentos da vida do que crianças da mesma idade (por exemplo, é indefeso(a) física ou emocionalmente).",
    74: "Interage ou participa em grupos menos que crianças da mesma idade.",
    75: "Tem dificuldade com amizades (por exemplo, fazer ou manter amigos).",
    76: "Não faz contato visual comigo durante interações no dia a dia.",
    77: "Tem dificuldade para prestar atenção.",
    78: "Se desvia de tarefas para observar todas as ações na sala.",
    79: "Parece alheio(a) dentro de um ambiente ativo (por exemplo, não tem consciência quanto à atividade).",
    80: "Olha fixamente, de maneira intensa, para objetos.",
    81: "Olha fixamente, de maneira intensa, para as pessoas.",
    82: "Observa a todos conforme se movem ao redor da sala.",
    83: "Muda de uma coisa para outra de modo a interferir com as atividades.",
    84: "Se perde facilmente.",
    85: "Tem dificuldade para encontrar objetos em espaços cheios de coisas (por exemplo, sapatos em um quarto bagunçado, lápis na gaveta de bagunças).",
    86: "Parece não se dar conta quando pessoas entram na sala.*",
}

OPCOES = [
    (5, "Quase sempre (90% ou mais)"),
    (4, "Frequentemente (75%)"),
    (3, "Metade do tempo (50%)"),
    (2, "Ocasionalmente (25%)"),
    (1, "Quase nunca (10% ou menos)"),
    (0, "Não se aplica"),
]


def calcular_pontuacao(respostas: dict) -> dict:
    """
    respostas: dict {numero_item: valor (1-5)}
    Retorna dict com pontuações brutas por seção e quadrante.
    """
    result = {}

    # Pontuações por seção
    for secao in SECOES:
        sid = secao["id"]
        total = 0
        for item in secao["itens"]:
            if item in ITENS_EXCLUIDOS:
                continue
            total += respostas.get(item, 0)
        result[sid] = total

    # Pontuações por quadrante
    for quad, itens in [("EX", ITENS_EX), ("EV", ITENS_EV), ("SN", ITENS_SN), ("OB", ITENS_OB)]:
        result[quad] = sum(respostas.get(i, 0) for i in itens)

    return result


def classificar(valor, faixas):
    """Retorna a classificação baseada nas faixas."""
    for min_v, max_v, label in faixas:
        if min_v <= valor <= max_v:
            return label
    return "—"
