# IntegraMente — Dados do Questionário Sensorial Escolar
# Preenchido pelo professor/educador

SECOES = [
    {"id": "auditivo", "nome": "Processamento Auditivo", "itens": list(range(1, 9))},
    {"id": "visual", "nome": "Processamento Visual", "itens": list(range(9, 16))},
    {"id": "tatil", "nome": "Processamento Tátil", "itens": list(range(16, 24))},
    {"id": "vestibular", "nome": "Vestibular e Proprioceptivo", "itens": list(range(24, 31))},
    {"id": "social", "nome": "Comportamento e Participação Social", "itens": list(range(31, 36))},
]

OPCOES = [
    (0, "Nunca"),
    (1, "Raramente"),
    (2, "Às vezes"),
    (3, "Frequentemente"),
    (4, "Sempre / Quase sempre"),
]

DOMINIO = {
    # Processamento Auditivo (1-8)
    1: "auditivo", 2: "auditivo", 3: "auditivo", 4: "auditivo",
    5: "auditivo", 6: "auditivo", 7: "auditivo", 8: "auditivo",
    # Processamento Visual (9-15)
    9: "visual", 10: "visual", 11: "visual", 12: "visual",
    13: "visual", 14: "visual", 15: "visual",
    # Processamento Tátil (16-23)
    16: "tatil", 17: "tatil", 18: "tatil", 19: "tatil",
    20: "tatil", 21: "tatil", 22: "tatil", 23: "tatil",
    # Vestibular e Proprioceptivo (24-30)
    24: "vestibular", 25: "vestibular", 26: "vestibular", 27: "vestibular",
    28: "vestibular", 29: "vestibular", 30: "vestibular",
    # Comportamento e Participação Social (31-35)
    31: "social", 32: "social", 33: "social", 34: "social", 35: "social",
}

DOMINIOS_CONFIG = {
    "auditivo":    {"nome": "Processamento Auditivo",              "max": 32, "itens": list(range(1, 9))},
    "visual":      {"nome": "Processamento Visual",                "max": 28, "itens": list(range(9, 16))},
    "tatil":       {"nome": "Processamento Tátil",                 "max": 32, "itens": list(range(16, 24))},
    "vestibular":  {"nome": "Vestibular e Proprioceptivo",         "max": 28, "itens": list(range(24, 31))},
    "social":      {"nome": "Comportamento e Participação Social", "max": 20, "itens": list(range(31, 36))},
}

PERGUNTAS = {
    # ── Processamento Auditivo ────────────────────────────────────────────────
    1:  "Fica perturbado com sons altos ou inesperados na sala de aula (ex.: campainha, grito, barulho de cadeira).",
    2:  "Coloca as mãos sobre os ouvidos para se proteger de ruídos do ambiente escolar.",
    3:  "Distrai-se facilmente com sons de fundo (ex.: ventilador, vozes de outras salas, chuva).",
    4:  "Tem dificuldade em seguir instruções verbais quando há barulho ao redor.",
    5:  "Reage de forma exagerada ao som de materiais sendo arrastados ou objetos caindo.",
    6:  "Canta, faz barulhos com a boca ou produz sons repetitivos durante as atividades.",
    7:  "Parece não ouvir quando chamado pelo nome, mesmo estando próximo e sem problema auditivo.",
    8:  "Apresenta dificuldade em discriminar sons semelhantes ao aprender a leitura/escrita.",
    # ── Processamento Visual ──────────────────────────────────────────────────
    9:  "Demonstra sensibilidade excessiva à luz natural ou artificial (pestaneja, desvia o olhar).",
    10: "Tem dificuldade em acompanhar texto na lousa ou no livro com os olhos.",
    11: "Perde facilmente o lugar ao ler ou copiar da lousa.",
    12: "Fica confuso em ambientes com muitos estímulos visuais (cartazes, cores, objetos).",
    13: "Esfrega os olhos com frequência ou apresenta olhos lacrimejantes sem motivo médico.",
    14: "Demonstra interesse excessivo em objetos que giram ou brilham, distanciando-se da tarefa.",
    15: "Tem dificuldade em organizar o espaço na folha (letras muito grandes, fora da linha, espaçamento irregular).",
    # ── Processamento Tátil ───────────────────────────────────────────────────
    16: "Reage negativamente ao toque inesperado de colegas (empurra, agride ou retira-se).",
    17: "Evita atividades que envolvem materiais com texturas (cola, areia, massa de modelar, tintas).",
    18: "Reclama da textura ou etiqueta das roupas uniformes, removendo-as sempre que possível.",
    19: "Apresenta dificuldade em ficar sentado em contato com superfícies de diferentes texturas.",
    20: "Busca tocar objetos e pessoas excessivamente, a ponto de incomodar os colegas.",
    21: "Parece não perceber que se machucou ou não demonstra reação adequada à dor.",
    22: "Tem dificuldade em manipular materiais escolares pequenos (lápis, tesoura, borracha).",
    23: "Apresenta sensibilidade excessiva a atividades de higiene (lavar as mãos, escovar os dentes).",
    # ── Vestibular e Proprioceptivo ───────────────────────────────────────────
    24: "Tem dificuldade em permanecer sentado quieto, levanta-se frequentemente ou balança na cadeira.",
    25: "Busca movimentos intensos de forma constante (girar, pular, balançar, correr na sala).",
    26: "Apresenta tônus muscular baixo, apoia-se na mesa ou escorrega na cadeira com frequência.",
    27: "Tem dificuldade em atividades que exigem equilíbrio (subir degraus, pular em um pé).",
    28: "Bate, pressiona ou aperta objetos e pessoas com força excessiva.",
    29: "Apresenta coordenação motora ampla abaixo do esperado para a idade (tropeça, cai com frequência).",
    30: "Tem dificuldade em planejar e executar sequências motoras (recortar, colar, dobrar papel).",
    # ── Comportamento e Participação Social ───────────────────────────────────
    31: "Evita participar de atividades em grupo ou rejeita brincadeiras coletivas.",
    32: "Apresenta reações emocionais intensas e desproporcionais a situações cotidianas.",
    33: "Tem dificuldade em adaptar-se a mudanças de rotina, atividades ou ambientes.",
    34: "Demonstra baixa tolerância à frustração, desistindo rapidamente de tarefas desafiadoras.",
    35: "Apresenta dificuldade em manter a atenção em tarefas estruturadas por tempo adequado à faixa etária.",
}


def calcular_pontuacao_escolar(respostas: dict) -> dict:
    """
    respostas: {numero_item: valor (0-4)}
    Retorna dict com pontuação por domínio.
    """
    result = {}
    for dom_id, config in DOMINIOS_CONFIG.items():
        total = sum(respostas.get(item, 0) for item in config["itens"])
        result[dom_id] = total
    return result


def classificar_escolar(valor: int, maximo: int) -> str:
    """Classifica a pontuação de um domínio."""
    if maximo == 0:
        return "—"
    pct = valor / maximo * 100
    if pct <= 25:
        return "Processamento típico"
    elif pct <= 50:
        return "Dificuldade leve"
    elif pct <= 75:
        return "Dificuldade moderada"
    else:
        return "Dificuldade significativa"
