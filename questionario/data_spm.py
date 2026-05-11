# SPM — Sensory Processing Measure
# SPM-P Casa (2–5 anos) e SPM Casa (5–12 anos)
# Respostas armazenadas como inteiros: N=1, O=2, F=3, S=4
# Pontuação: itens normais → score = valor; itens invertidos (SOC + item 57 SPM Casa) → score = 5 − valor

OPCOES_SPM = [
    (1, "Nunca"),
    (2, "Ocasionalmente"),
    (3, "Frequentemente"),
    (4, "Sempre"),
]

# ── SPM-P CASA (2–5 anos) ─────────────────────────────────────────────────────

SECOES_SPM_P = [
    {"id": "soc", "nome": "Participação Social",   "sigla": "SOC", "itens": list(range(1,  9)),  "invertida": True},
    {"id": "vis", "nome": "Visão",                  "sigla": "VIS", "itens": list(range(9,  20)), "invertida": False},
    {"id": "hea", "nome": "Audição",                "sigla": "HEA", "itens": list(range(20, 29)), "invertida": False},
    {"id": "tou", "nome": "Tato",                   "sigla": "TOU", "itens": list(range(29, 43)), "invertida": False},
    {"id": "sme", "nome": "Olfato e Paladar",       "sigla": "SME", "itens": list(range(43, 47)), "invertida": False},
    {"id": "bod", "nome": "Consciência Corporal",   "sigla": "BOD", "itens": list(range(47, 56)), "invertida": False},
    {"id": "bal", "nome": "Equilíbrio e Movimento", "sigla": "BAL", "itens": list(range(56, 67)), "invertida": False},
    {"id": "pla", "nome": "Planejamento e Ideação", "sigla": "PLA", "itens": list(range(67, 76)), "invertida": False},
]

REVERSED_SPM_P = set(range(1, 9))  # apenas SOC

PERGUNTAS_SPM_P = {
    # SOC (1–8) — invertido: N=4, O=3, F=2, S=1
    1:  "Brinca com os amigos de forma cooperativa.",
    2:  "Compartilha coisas quando lhe é pedido.",
    3:  "Participa de jogos em grupo sem interromper a atividade.",
    4:  "Participa e interage apropriadamente nos períodos das refeições.",
    5:  "Participa adequadamente de passeios familiares, como jantar fora ou ir a um museu ou shopping.",
    6:  "Participa adequadamente de reuniões de família, como feriados, casamento e aniversários.",
    7:  "Participa de forma adequada em atividades com amigos, como festas e brincadeiras e brinquedos de playground.",
    8:  "Ajuda nas atividades familiares como carregar sacolas de compras e buscar seus irmãos na escola.",
    # VIS (9–19)
    9:  "Parece incomodado com claridade, especialmente luzes claras (pisca, aperta os olhos, chora, fecha os olhos, etc.).",
    10: "Tem dificuldade para encontrar um objeto quando ele está junto de outras coisas.",
    11: "Tem dificuldade em reconhecer se os objetos são semelhantes ou diferentes com base em suas cores, formas ou tamanhos.",
    12: "Gosta de observar os objetos rodando ou em movimento, mais do que a maioria das crianças a sua idade.",
    13: "Anda entre objetos ou pessoas como se elas não estivessem ali.",
    14: "Gosta de ligar e desligar interruptores de luz repetidamente.",
    15: "Gosta de olhar objetos em movimento com o canto de seu olho.",
    16: "Tem dificuldade para prestar atenção se está em um local com muitas coisas para olhar.",
    17: "Fica incomodado em locais com muitos estímulos visuais, como um quarto muito bagunçado ou uma loja cheia de itens.",
    18: "Distrai-se facilmente ao olhar as coisas ao seu redor quando está caminhando.",
    19: "Tem dificuldade em completar tarefas simples, quando há muitas coisas para olhar.",
    # HEA (20–28)
    20: "Parece incomodado com sons normais em uma casa, como o do aspirador de pó, secador de cabelo, ou barulho da descarga.",
    21: "Responde negativamente a ruídos altos, fugindo, chorando, ou tampando os ouvidos com as mãos.",
    22: "Parece não ouvir certos sons.",
    23: "Mostra-se perturbado ou extremamente interessado com sons que normalmente não são ouvidos por outras pessoas.",
    24: "Parece facilmente distraído por ruídos do ambiente, como de um cortador de grama fora da casa, ar condicionado, uma geladeira, etc.",
    25: "Gosta de fazer certos barulhos repetidamente, como apertar a descarga do banheiro muitas vezes.",
    26: "Mostra angústia com sons estridentes, como apitos, apetrechos de festa, flautas e trompetes.",
    27: "Demonstra incomodo em locais com muitos estímulos auditivos, como em uma festa ou em locais lotados.",
    28: "Assusta-se facilmente ao ouvir um som alto ou inesperado.",
    # TOU (29–42)
    29: "Afasta-se ao ser levemente tocado.",
    30: "Prefere tocar a ser tocado.",
    31: "Estressa-se ao cortarem suas unhas.",
    32: "Sente-se incomodado ao tocarem seu rosto.",
    33: "Evita brincar com pintura de dedo, areia, argila, barro, cola, ou outras coisas que sujem.",
    34: "Apresenta alta tolerância à dor.",
    35: "Não gosta de escovar os dentes mais do que outras crianças da sua idade.",
    36: "Parece ter prazer com sensações dolorosas, como cair no chão ou bater o seu próprio corpo.",
    37: "Não gosta de pentear, escovar e arrumar o cabelo.",
    38: "Não gosta de cortar o cabelo.",
    39: "Evita alimentos com certas texturas.",
    40: "Vomita ou tem ânsia de vômito ao ingerir alimentos com determinadas texturas.",
    41: "Não gosta quando tentam limpar ou lavar seu rosto.",
    42: "Baba mais que outras crianças da sua idade.",
    # SME (43–46)
    43: "Gosta de ingerir produtos não alimentares como colas, tintas, etc.",
    44: "Parece ignorar ou não perceber odores fortes, aos quais outras crianças reagiriam.",
    45: "Prefere sabores de certos alimentos a ponto de recusar comer outros alimentos oferecidos.",
    46: "Recusa usar creme dental na escova de dente.",
    # BOD (47–55)
    47: "Segura objetos (como um lápis ou uma colher) tão firmemente que fica difícil usar o objeto.",
    48: "Parece buscar atividades como empurrar, puxar, arrastar, levantar e saltar.",
    49: "Mostra-se inseguro ao levantar ou abaixar o corpo durante o movimento, como para sentar ou passar sobre um objeto.",
    50: "Segura objetos (como lápis ou colher) tão frouxamente que fica difícil usar o objeto.",
    51: "Parece exercer demasiada pressão em tarefas como caminhadas (caminha pesadamente), bater portas ou pressiona muito fortemente ao usar lápis ou giz de cera.",
    52: "Salta muito.",
    53: "Tende a acariciar animais com muita força.",
    54: "Bate ou empurra outras crianças.",
    55: "Mastiga brinquedos, roupas ou outros objetos mais que as outras crianças da mesma idade.",
    # BAL (56–66)
    56: "Demonstra medo exagerado ao movimento, como subir e descer escadas ou brincar em balanços, gira-gira, etc.",
    57: "Evita atividades de equilíbrio, como andar em freios e em solos desnivelados.",
    58: "Cai da cadeira ao tentar endireitar-se.",
    59: "Falha ao tentar se segurar quando está caindo.",
    60: "Parece não ficar tonto quando os outros normalmente ficariam.",
    61: "Costuma brincar de rodar o próprio corpo mais que outras crianças da sua idade.",
    62: "Mostra desespero quando a cabeça está inclinada, em posição não vertical.",
    63: "Apresenta coordenação motora ruim e parece uma criança desajeitada.",
    64: "Ao tentar se levantar, apoia-se em pessoas ou mobiliários.",
    65: "Balança seu corpo quando acorda e se senta.",
    66: "Parece ter medo de descer escadas ou ladeiras.",
    # PLA (67–75)
    67: "Tem dificuldade para descobrir como carregar vários objetos ao mesmo tempo.",
    68: "Parece confuso sobre como arrumar os materiais e pertences em seus lugares corretos.",
    69: "Fica confuso com a sequência adequada de ações rotineiras, como vestir-se ou ir para a cama.",
    70: "Não consegue completar tarefas com várias etapas.",
    71: "Apresenta dificuldade para imitar ações demonstradas, tais como jogos de movimento ou canções com gestos.",
    72: "Não consegue copiar outra criança ou um adulto na construção com blocos.",
    73: "Tem dificuldades em apresentar ideias novas durante as atividades lúdicas.",
    74: "Tende a desempenhar as mesmas atividades várias vezes, ao invés de mudar para novas atividades quando dada a oportunidade.",
    75: "Tem problemas quando sobe ou desce da cadeirinha no carro.",
}

# ── SPM CASA (5–12 anos) ──────────────────────────────────────────────────────

SECOES_SPM_CASA = [
    {"id": "soc", "nome": "Participação Social",   "sigla": "SOC", "itens": list(range(1,  11)), "invertida": True},
    {"id": "vis", "nome": "Visão",                  "sigla": "VIS", "itens": list(range(11, 22)), "invertida": False},
    {"id": "hea", "nome": "Audição",                "sigla": "HEA", "itens": list(range(22, 30)), "invertida": False},
    {"id": "tou", "nome": "Tato",                   "sigla": "TOU", "itens": list(range(30, 41)), "invertida": False},
    {"id": "sme", "nome": "Olfato e Paladar",       "sigla": "SME", "itens": list(range(41, 46)), "invertida": False},
    {"id": "bod", "nome": "Consciência Corporal",   "sigla": "BOD", "itens": list(range(46, 56)), "invertida": False},
    {"id": "bal", "nome": "Equilíbrio e Movimento", "sigla": "BAL", "itens": list(range(56, 67)), "invertida": False},
    {"id": "pla", "nome": "Planejamento e Ideação", "sigla": "PLA", "itens": list(range(67, 76)), "invertida": False},
]

# SOC (1–10) + item 57 "Tem bom equilíbrio?" (positivamente enunciado)
REVERSED_SPM_CASA = set(range(1, 11)) | {57}

PERGUNTAS_SPM_CASA = {
    # SOC (1–10) — invertido: N=4, O=3, F=2, S=1
    1:  "Brinca com amigos cooperativamente (sem muitos questionamentos)?",
    2:  "Interage apropriadamente com os pais e outros adultos próximos (comunica-se bem, segue instruções, mostra respeito, etc.)?",
    3:  "Compartilha coisas quando é solicitado?",
    4:  "Mantém uma conversa sem se levantar ou sentar muito próximo aos outros?",
    5:  "Mantém contato visual apropriadamente durante uma conversa?",
    6:  "Entra em jogos com outras pessoas sem interromper a atividade?",
    7:  "Participa e interage apropriadamente de uma conversa durante a refeição?",
    8:  "Participa apropriadamente nos passeios com familiares, como sair para jantar ou ir ao parque, museus ou cinema?",
    9:  "Participa apropriadamente em reuniões familiares, como férias, casamento e aniversário?",
    10: "Participa apropriadamente em atividades com amigos, como festas, ir ao shopping, andar de bicicleta/skate/patinete?",
    # VIS (11–21)
    11: "Parece incomodado com a luz, especialmente luz clara (pisca/desvia/fecha os olhos, lacrimeja etc)?",
    12: "Tem dificuldade para procurar objetos, quando este está junto de outras coisas?",
    13: "Fecha um dos olhos, ou vira a cabeça quando olha para algo ou alguém?",
    14: "Fica incomodado em locais com estímulos visuais incomuns, como um quarto claro ou colorido ou com baixa iluminação?",
    15: "Tem dificuldade em controlar o movimento dos olhos quando segue um objeto com os olhos, como uma bola?",
    16: "Tem dificuldade para identificar se os objetos são semelhantes ou diferentes, baseado nas cores, formato ou tamanho?",
    17: "Gosta de observar objetos girando ou se movendo, mais do que outras crianças na sua idade?",
    18: "Anda entre objetos ou pessoas, como se eles não estivessem ali?",
    19: "Gosta de ligar e desligar o interruptor da luz repetidamente?",
    20: "Não gosta de certos tipos de luz, como o sol do meio dia, luz estroboscópica, luz piscante ou fluorescente?",
    21: "Gosta de olhar objetos em movimento com o canto dos olhos?",
    # HEA (22–29)
    22: "Parece incomodado com os sons normais em uma casa, tais como o do aspirador de pó, secador de cabelo, barulho de descarga?",
    23: "Responde negativamente aos barulhos altos, fugindo, chorando ou tapando os ouvidos com as mãos?",
    24: "Parece não ouvir certos sons?",
    25: "Parece perturbado ou interessado intensamente em sons que usualmente não são notados por outras pessoas?",
    26: "Parece assustado com sons que usualmente não causam incômodo em crianças da mesma idade?",
    27: "Parece se distrair facilmente com ruídos do ambiente, tais como cortador de grama, ar condicionado, geladeira ou luzes fluorescentes?",
    28: "Gosta de fazer certos barulhos repetidamente, como apertar a descarga de banheiro muitas vezes?",
    29: "Mostra incômodo à sons agudos ou estridentes, como apito, chocalho, flauta e trompete?",
    # TOU (30–40)
    30: "Recua quando tocado levemente?",
    31: "Parece não perceber quando é tocado?",
    32: "Fica incomodado pelo contato com roupas novas?",
    33: "Prefere tocar a ser tocado?",
    34: "Fica incomodado ao cortarem suas unhas dos pés e das mãos?",
    35: "Parece incomodado quando alguém toca sua face?",
    36: "Evita tocar ou brincar com pintura a dedo, pasta, areia, barro, lama, cola ou outras coisas que sujem?",
    37: "Tem alta tolerância a dor?",
    38: "Não gosta de escovar os dentes, mais do que a maioria das crianças de sua idade?",
    39: "Parece gostar de sensações que podem ser doloridas, como cair no chão ou bater no próprio corpo?",
    40: "Tem problemas para encontrar coisas no bolso ou bolsa, mochila, usando somente o tato, sem olhar?",
    # SME (41–45)
    41: "Gosta de experimentar itens não comestíveis, como cola ou tinta?",
    42: "Tem ânsia quando pensa em comidas que o desagradam, como espinafre cozido?",
    43: "Gosta de cheirar objetos não comestíveis e pessoas?",
    44: "Mostra desconforto com os cheiros que outras crianças não notam?",
    45: "Parece ignorar ou não notar odores fortes, que outra criança reagiria?",
    # BOD (46–55)
    46: "Agarra objetos (como lápis ou colher) tão firmemente, que fica difícil utilizá-los?",
    47: "Parece buscar atividades como puxar, empurrar, arrastar, levantar e saltar?",
    48: "Parece inseguro sobre o quanto pode abaixar ou levantar o corpo durante o movimento como sentar-se ou ficar em pé em cima de um objeto?",
    49: "Agarra objetos (como lápis ou colher), tão frouxamente que fica difícil utilizar o objeto?",
    50: "Parece exercer muita pressão para tarefas, como andar pesadamente, fechar porta com força ou apertar fortemente o lápis ou giz de cera?",
    51: "Salta muito?",
    52: "Tende a acariciar os animais com muita força?",
    53: "Bate ou empurra outras crianças?",
    54: "Mastiga os brinquedos, roupas ou outros objetos, mais que outras crianças?",
    55: "Quebra coisas ao pressioná-las ou empurrá-las muito forte?",
    # BAL (56–66) — item 57 é invertido ("Tem bom equilíbrio?")
    56: "Demonstra medo exagerado com movimento, como subir e descer escadas, subir na gangorra/balanço/escorregador ou outros equipamentos do parque?",
    57: "Tem bom equilíbrio?",
    58: "Evita atividade de equilíbrio, como andar em um piso desnivelado, meio fio?",
    59: "Cai da cadeira quando muda o corpo de posição?",
    60: "Falha ao controlar o próprio corpo quando cai?",
    61: "Parece não ficar tonto quando outros normalmente ficariam?",
    62: "Gira ou roda seu corpo mais do que outras crianças?",
    63: "Mostra-se incomodado quando sua cabeça inclina, vira ou sai da posição vertical ereta?",
    64: "Tem má coordenação motora e parece ser desajeitado?",
    65: "Demonstra medo ao entrar em elevadores ou utilizar escada rolante?",
    66: "Se apoia em outras pessoas ou móveis ao se sentar ou quando tenta se levantar?",
    # PLA (67–75)
    67: "Executa de maneira inconsistente as tarefas diárias?",
    68: "Tem dificuldade para planejar como carregar vários objetos ao mesmo tempo?",
    69: "Parece confuso sobre como guardar os materiais ou objetos em seus lugares corretos?",
    70: "Falha ao executar tarefas numa sequência apropriada, como vestir-se ou arrumar a mesa?",
    71: "Falha ao completar tarefas com várias etapas?",
    72: "Tem dificuldade para imitar ações demonstradas, como jogos com movimentos e músicas com sequência de movimentos?",
    73: "Tem dificuldade para construir a cópia de um modelo, como ao usar o lego ou blocos para construir algo que corresponda ao modelo?",
    74: "Tem dificuldade em apresentar ideias para novos jogos e atividades?",
    75: "Tende a brincar com as mesmas atividades repetidamente, ao invés de mudar para novas atividades quando lhe é dada chance?",
}

# ── Configuração das seções ───────────────────────────────────────────────────

SECOES_CONFIG_SPM = {
    "soc": {"nome": "Participação Social",    "sigla": "SOC", "cor": "#3E73D1"},
    "vis": {"nome": "Visão",                  "sigla": "VIS", "cor": "#6B8DD6"},
    "hea": {"nome": "Audição",                "sigla": "HEA", "cor": "#E8793A"},
    "tou": {"nome": "Tato",                   "sigla": "TOU", "cor": "#E8B84B"},
    "sme": {"nome": "Olfato e Paladar",       "sigla": "SME", "cor": "#7DB87D"},
    "bod": {"nome": "Consciência Corporal",   "sigla": "BOD", "cor": "#0F274F"},
    "bal": {"nome": "Equilíbrio e Movimento", "sigla": "BAL", "cor": "#8E44AD"},
    "pla": {"nome": "Planejamento e Ideação", "sigla": "PLA", "cor": "#E74C3C"},
}


def calcular_pontuacao_spm(respostas: dict, faixa: str) -> dict:
    """
    respostas: {numero_item: valor (1–4)}
    faixa: 'spm_p' ou 'spm_casa'
    Retorna {secao_id: raw_score, ..., 'tot': total}
    Itens invertidos: score = 5 − valor; demais: score = valor
    """
    if faixa == "spm_p":
        secoes = SECOES_SPM_P
        reversed_set = REVERSED_SPM_P
    else:
        secoes = SECOES_SPM_CASA
        reversed_set = REVERSED_SPM_CASA

    result = {}
    total = 0
    for secao in secoes:
        score = 0
        for item in secao["itens"]:
            v = respostas.get(item, 1)
            score += (5 - v) if item in reversed_set else v
        result[secao["id"]] = score
        total += score
    result["tot"] = total
    return result


def max_score_spm(faixa: str) -> dict:
    """Retorna pontuação máxima por seção e total."""
    secoes = SECOES_SPM_P if faixa == "spm_p" else SECOES_SPM_CASA
    result = {s["id"]: len(s["itens"]) * 4 for s in secoes}
    result["tot"] = sum(result.values())
    return result


def classificar_spm_pct(pct: float) -> str:
    """Classificação baseada em percentual do máximo (proxy sem tabela normativa)."""
    if pct >= 75:
        return "Disfunção Definitiva"
    elif pct >= 60:
        return "Alguns Problemas"
    else:
        return "Típico"
