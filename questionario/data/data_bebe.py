# IntegraMente — Dados do Perfil Sensorial Bebê/Criança Pequena (Winnie Dunn)
# Preenchido pelo cuidador/responsável

# ── Faixa Bebê (0–6 meses) ──────────────────────────────────────────────────

SECOES_BEBE = [
    {"id": "busca",         "nome": "Busca Sensorial",        "itens": list(range(1, 8)),  "quadrante": "busca"},
    {"id": "evitamento",    "nome": "Evitamento Sensorial",   "itens": list(range(8, 15)), "quadrante": "evitamento"},
    {"id": "sensibilidade", "nome": "Sensibilidade Sensorial","itens": list(range(15, 22)),"quadrante": "sensibilidade"},
    {"id": "registro",      "nome": "Registro Sensorial",     "itens": list(range(22, 29)),"quadrante": "registro"},
]

PERGUNTAS_BEBE = {
    # ── Busca Sensorial (1-7) ─────────────────────────────────────────────────
    1: "Demonstra prazer intenso ao ser balançado ou embalado (sorri, vocaliza, pede mais).",
    2: "Explora ativamente com a boca objetos que alcança (chupa, morde, lambe).",
    3: "Busca ativamente estímulos visuais coloridos ou em movimento, virando a cabeça para seguir.",
    4: "Agita os braços e pernas com animação quando recebe estímulos táteis (carinho, massagem).",
    5: "Demonstra prazer ao ouvir sons musicais ou vozes animadas, aumentando sua movimentação.",
    6: "Procura ativamente o contato físico com o cuidador, movendo-se em sua direção.",
    7: "Reage com entusiasmo a estímulos olfativos como o cheiro do leite ou do cuidador.",
    # ── Evitamento Sensorial (8-14) ───────────────────────────────────────────
    8:  "Chora ou fica agitado com sons altos inesperados (campainha, aspirador, latido).",
    9:  "Apresenta dificuldade para ser acalmado após receber estímulos intensos.",
    10: "Chora ou arqueja ao ser trocado de posição de forma rápida ou inesperada.",
    11: "Reage negativamente ao toque de pessoas desconhecidas (chora, endurece o corpo).",
    12: "Demonstra desconforto intenso ao usar roupas de determinadas texturas.",
    13: "Chora ou desvia o olhar quando exposto a luzes brilhantes ou ambientes muito iluminados.",
    14: "Recusa-se a mamar ou fica agitado com determinadas texturas de bicos ou mamadeiras.",
    # ── Sensibilidade Sensorial (15-21) ──────────────────────────────────────
    15: "Acorda facilmente com sons leves ou mudanças de luz no ambiente.",
    16: "Reage ao menor toque no rosto ou corpo, mesmo que suave.",
    17: "Demonstra desconforto visível com mudanças de temperatura (água do banho, ar condicionado).",
    18: "Nota imediatamente quando há mudanças no ambiente (nova pessoa, novo objeto).",
    19: "Reage de forma perceptível a cheiros novos ou diferentes do habitual.",
    20: "Interrompe o que está fazendo ao menor estímulo auditivo do ambiente.",
    21: "Demonstra sensibilidade excessiva ao ser manipulado durante cuidados (troca, banho, vesti).",
    # ── Registro Sensorial (22-28) ────────────────────────────────────────────
    22: "Parece não notar quando alguém entra no campo visual ou o chama pelo nome.",
    23: "Não reage a sons altos próximos, mesmo sem problema auditivo identificado.",
    24: "Permanece indiferente a estímulos táteis moderados (toque, carinho, temperatura).",
    25: "Não demonstra desconforto ao ficar longo tempo na mesma posição.",
    26: "Parece alheio a cheiros fortes ou odores no ambiente.",
    27: "Não expressa prazer ou desprazer em resposta a diferentes sabores do leite.",
    28: "Permanece passivo e pouco responsivo durante interações com o cuidador.",
}

# ── Faixa Criança Pequena (7–36 meses) ──────────────────────────────────────
# Itens numerados de 101 a 136 para evitar conflitos

SECOES_PEQUENA = [
    {"id": "busca",         "nome": "Busca Sensorial",        "itens": list(range(101, 110)), "quadrante": "busca"},
    {"id": "evitamento",    "nome": "Evitamento Sensorial",   "itens": list(range(110, 119)), "quadrante": "evitamento"},
    {"id": "sensibilidade", "nome": "Sensibilidade Sensorial","itens": list(range(119, 128)), "quadrante": "sensibilidade"},
    {"id": "registro",      "nome": "Registro Sensorial",     "itens": list(range(128, 137)), "quadrante": "registro"},
]

PERGUNTAS_PEQUENA = {
    # ── Busca Sensorial (101-109) ─────────────────────────────────────────────
    101: "Busca ativamente brincadeiras com movimentos intensos (girar, pular, balançar).",
    102: "Coloca objetos na boca além da fase típica de exploração oral.",
    103: "Demonstra interesse excessivo por objetos com texturas diferentes, tocando tudo ao redor.",
    104: "Procura sons altos ou músicas com volume elevado, aumentando o volume quando pode.",
    105: "Fica muito animado com estímulos visuais fortes (luzes piscando, telas brilhantes).",
    106: "Busca o contato físico intenso com outras pessoas (abraços fortes, pressão no corpo).",
    107: "Demonstra fascínio por cheiros, cheirando pessoas, objetos e alimentos antes de interagir.",
    108: "Busca estímulos proprioceptivos como carregar objetos pesados, empurrar móveis ou pular.",
    109: "Prefere brincadeiras de contato físico intenso a brincadeiras tranquilas.",
    # ── Evitamento Sensorial (110-118) ───────────────────────────────────────
    110: "Fica agitado ou chora em ambientes com muitas pessoas e barulho (festas, shoppings).",
    111: "Recusa alimentos com determinadas texturas, consistências ou temperaturas.",
    112: "Chora ou resiste ao corte de cabelo, higiene bucal ou limpeza do rosto e nariz.",
    113: "Demonstra medo ou resistência a equipamentos de playground (escorregador, balanço).",
    114: "Reage de forma intensa ao toque inesperado, empurrando ou retirando-se.",
    115: "Fica irritado ou ansioso quando usa roupas com costuras, etiquetas ou tecidos ásperos.",
    116: "Recusa-se a caminhar descalço em superfícies como areia, grama ou texturas irregulares.",
    117: "Demonstra resistência ou angústia intensa durante cuidados de higiene (banho, escovação).",
    118: "Fica perturbado com luzes brilhantes ou ambientes muito iluminados, fechando os olhos.",
    # ── Sensibilidade Sensorial (119-127) ────────────────────────────────────
    119: "Nota pequenas diferenças no ambiente, como um objeto novo ou fora do lugar.",
    120: "Reage intensamente a sons moderados que outras crianças ignoram.",
    121: "Demonstra desconforto imediato com a mínima sujeira nas mãos ou no rosto.",
    122: "Interrompe a brincadeira ao menor barulho ou movimento ao redor.",
    123: "É sensível a mudanças de temperatura no ambiente ou nos alimentos.",
    124: "Nota e comenta odores que adultos dificilmente percebem.",
    125: "Reage visivelmente a sabores e texturas alimentares sutis.",
    126: "Demonstra consciência aguçada de suas roupas (costuras, etiquetas, ajuste).",
    127: "Acorda facilmente com sons ou luz durante o sono.",
    # ── Registro Sensorial (128-136) ─────────────────────────────────────────
    128: "Parece não perceber quando fica com a roupa suja, molhada ou desajeita.",
    129: "Não reage quando é chamado pelo nome em ambiente tranquilo.",
    130: "Parece alheio a quedas ou pequenos machucados, não demonstrando dor.",
    131: "Não nota objetos ou pessoas que entram em seu campo de visão.",
    132: "Parece não perceber cheiros fortes ou desagradáveis no ambiente.",
    133: "Demora a responder a estímulos táteis ou demostra respostas tardias ao toque.",
    134: "Parece não perceber quando está com frio ou calor intenso.",
    135: "Não demonstra reação a sabores fortes (muito doce, salgado, azedo).",
    136: "Parece alheio ao que acontece ao redor durante atividades rotineiras.",
}

# ── Escala de respostas ───────────────────────────────────────────────────────
# 1=Sempre, 2=Frequentemente, 3=Às vezes, 4=Raramente, 5=Nunca
# Pontuação menor = mais frequente (comportamento mais presente)

OPCOES_BEBE = [
    (1, "Sempre"),
    (2, "Frequentemente"),
    (3, "Às vezes"),
    (4, "Raramente"),
    (5, "Nunca"),
]

# ── Mapeamento item → quadrante ──────────────────────────────────────────────

QUADRANTE_BEBE = {
    **{i: "busca"         for i in range(1, 8)},
    **{i: "evitamento"    for i in range(8, 15)},
    **{i: "sensibilidade" for i in range(15, 22)},
    **{i: "registro"      for i in range(22, 29)},
}

QUADRANTE_PEQUENA = {
    **{i: "busca"         for i in range(101, 110)},
    **{i: "evitamento"    for i in range(110, 119)},
    **{i: "sensibilidade" for i in range(119, 128)},
    **{i: "registro"      for i in range(128, 137)},
}

# ── Configuração dos quadrantes ───────────────────────────────────────────────
# Bebê (0-6m): 7 itens × max 5 = 35 por quadrante
# Criança pequena (7-36m): 9 itens × max 5 = 45 por quadrante

QUADRANTES_CONFIG = {
    "busca": {
        "nome": "Busca Sensorial",
        "cor": "#E8793A",
        "max_bebe": 35,
        "max_pequena": 45,
    },
    "evitamento": {
        "nome": "Evitamento Sensorial",
        "cor": "#6B8DD6",
        "max_bebe": 35,
        "max_pequena": 45,
    },
    "sensibilidade": {
        "nome": "Sensibilidade Sensorial",
        "cor": "#E8B84B",
        "max_bebe": 35,
        "max_pequena": 45,
    },
    "registro": {
        "nome": "Registro Sensorial",
        "cor": "#7DB87D",
        "max_bebe": 35,
        "max_pequena": 45,
    },
}


def calcular_pontuacao_bebe(respostas: dict, faixa: str) -> dict:
    """
    respostas: {numero_item: valor (1-5)}
    faixa: 'bebe' ou 'crianca_pequena'
    Retorna dict com pontuação por quadrante: busca, evitamento, sensibilidade, registro
    """
    if faixa == "bebe":
        secoes = SECOES_BEBE
    else:
        secoes = SECOES_PEQUENA

    result = {}
    for secao in secoes:
        quad = secao["quadrante"]
        total = sum(respostas.get(item, 0) for item in secao["itens"])
        result[quad] = total
    return result


def classificar_bebe(valor: int, maximo: int) -> str:
    """
    Classifica a pontuação de um quadrante.
    Pontuação menor = comportamento MAIS presente (1=Sempre).
    Pontuação maior = comportamento MENOS presente (5=Nunca).
    Escala 1–5 por item → mínimo possível = 20% do máximo.
    Threshold "Mais" em 22% para que "Muito mais" seja atingível.
    """
    if maximo == 0:
        return "—"
    pct = valor / maximo * 100
    if pct >= 85:
        return "Muito menos que os pares"
    elif pct >= 75:
        return "Menos que os pares"
    elif pct >= 25:
        return "Semelhante aos pares"
    elif pct >= 22:
        return "Mais que os pares"
    else:
        return "Muito mais que os pares"
