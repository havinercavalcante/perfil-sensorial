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

# Seções que compõem o TOT (sem SOC e sem PLA — conforme tabelas normativas)
TOT_SECOES = ["vis", "hea", "tou", "sme", "bod", "bal"]

# ── Tabelas normativas: raw score → T-score ───────────────────────────────────
# SPM-P Casa (3–5 anos)
SPM_P_TSCORE: dict[str, dict[int, int]] = {
    "soc": {8:40,9:40,10:44,11:47,12:50,13:52,14:54,15:56,16:59,17:63,18:66,19:67,
            20:68,21:69,22:70,23:71,24:73,25:75,26:76,27:79,28:80,29:80,30:80,31:80,32:80},
    "vis": {11:40,12:43,13:47,14:50,15:53,16:56,17:58,18:60,19:62,20:64,21:66,22:67,
            23:69,24:70,25:71,26:72,27:72,28:73,29:74,30:75,31:75,32:76,33:76,34:76,
            35:77,36:77,37:79,38:80,39:80,40:80,41:80,42:80,43:80,44:80},
    "hea": {9:40,10:47,11:52,12:55,13:58,14:60,15:62,16:64,17:66,18:67,19:69,20:70,
            21:71,22:72,23:72,24:73,25:75,26:76,27:77,28:78,29:79,30:80,31:80,32:80,
            33:80,34:80,35:80,36:80},
    "tou": {14:40,15:43,16:46,17:49,18:53,19:55,20:58,21:60,22:62,23:63,24:64,25:65,
            26:66,27:67,28:68,29:69,30:70,31:71,32:72,33:74,34:76,35:77,36:80,37:80,
            38:80,39:80,40:80,41:80,42:80,43:80,44:80,45:80,46:80,47:80,48:80,49:80,
            50:80,51:80,52:80,53:80,54:80,55:80,56:80},
    "bod": {9:40,10:46,11:50,12:54,13:57,14:60,15:62,16:65,17:66,18:68,19:69,20:71,
            21:72,22:74,23:76,24:77,25:78,26:79,27:80,28:80,29:80,30:80,31:80,32:80,
            33:80,34:80,35:80,36:80},
    "bal": {11:42,12:50,13:55,14:58,15:62,16:64,17:67,18:67,19:68,20:70,21:71,22:72,
            23:73,24:75,25:75,26:75,27:75,28:76,29:76,30:76,31:76,32:77,33:80,34:80,
            35:80,36:80,37:80,38:80,39:80,40:80,41:80,42:80,43:80,44:80},
    "pla": {9:40,10:48,11:52,12:55,13:58,14:61,15:64,16:65,17:67,18:69,19:71,20:72,
            21:74,22:74,23:75,24:75,25:76,26:76,27:77,28:78,29:80,30:80,31:80,32:80,
            33:80,34:80,35:80,36:80},
    "tot": {58:40,59:40,60:40,61:40,62:40,63:42,64:43,65:45,66:46,67:47,68:48,69:49,
            70:50,71:51,72:52,73:52,74:53,75:54,76:55,77:56,78:56,79:57,80:58,81:58,
            82:59,83:59,84:60,85:60,86:61,87:61,88:62,89:63,90:63,91:64,92:64,93:65,
            94:65,95:66,96:66,97:66,98:66,99:67,100:67,101:67,102:67,103:67,104:68,
            105:68,106:69,107:69,108:69,109:69,110:69,111:70,112:70,113:71,114:71,
            115:71,116:71,117:71,118:71,119:72,120:72,121:72,122:72,123:72,124:72,
            125:72,126:72,127:72,128:72,129:72,130:72,131:72,132:72,133:72,134:72,
            135:72,136:72,137:73,138:73,139:74,140:75,141:76,142:76,143:76,144:76,
            145:76,146:76,147:76,148:77,149:78,150:78,151:79,152:79,153:80,154:80,
            155:80,156:80,157:80,158:80,159:80,160:80,161:80,162:80,163:80,164:80,
            165:80,166:80,167:80,168:80,169:80,170:80,171:80,172:80,173:80,174:80,
            175:80,176:80,177:80,178:80,179:80,180:80,181:80,182:80,183:80,184:80,
            185:80,186:80,187:80,188:80,189:80,190:80,191:80,192:80,193:80,194:80,
            195:80,196:80,197:80,198:80,199:80,200:80,201:80,202:80,203:80,204:80,
            205:80,206:80,207:80,208:80,209:80,210:80,211:80,212:80,213:80,214:80,
            215:80,216:80,217:80,218:80,219:80,220:80,221:80,222:80,223:80,224:80,
            225:80,226:80,227:80,228:80,229:80,230:80,231:80,232:80},
}

# SPM Casa (5–12 anos)
SPM_CASA_TSCORE: dict[str, dict[int, int]] = {
    "soc": {10:40,11:40,12:43,13:45,14:47,15:49,16:51,17:53,18:55,19:56,20:58,21:60,
            22:62,23:63,24:64,25:65,26:66,27:67,28:69,29:70,30:71,31:73,32:75,33:76,
            34:78,35:79,36:79,37:80,38:80,39:80,40:80},
    "vis": {11:41,12:50,13:54,14:57,15:59,16:61,17:63,18:64,19:65,20:67,21:68,22:68,
            23:69,24:70,25:71,26:72,27:74,28:75,29:75,30:76,31:77,32:78,33:79,34:79,
            35:80,36:80,37:80,38:80,39:80,40:80,41:80,42:80,43:80,44:80},
    "hea": {8:43,9:52,10:56,11:59,12:62,13:63,14:64,15:66,16:67,17:68,18:69,19:70,
            20:71,21:72,22:74,23:75,24:76,25:77,26:78,27:79,28:79,29:80,30:80,31:80,32:80},
    "tou": {11:40,12:47,13:52,14:55,15:57,16:59,17:61,18:63,19:64,20:65,21:66,22:67,
            23:68,24:68,25:69,26:71,27:72,28:73,29:73,30:74,31:74,32:75,33:77,34:78,
            35:78,36:79,37:80,38:80,39:80,40:80,41:80,42:80,43:80,44:80},
    "bod": {10:40,11:48,12:52,13:55,14:57,15:59,16:60,17:61,18:63,19:64,20:65,21:66,
            22:67,23:68,24:69,25:70,26:71,27:72,28:73,29:74,30:75,31:76,32:77,33:78,
            34:79,35:79,36:80,37:80,38:80,39:80,40:80},
    "bal": {11:40,12:47,13:51,14:54,15:57,16:59,17:61,18:63,19:64,20:65,21:66,22:68,
            23:69,24:71,25:72,26:74,27:75,28:75,29:76,30:76,31:77,32:77,33:78,34:79,
            35:80,36:80,37:80,38:80,39:80,40:80,41:80,42:80,43:80,44:80},
    "pla": {9:40,10:45,11:48,12:51,13:53,14:55,15:57,16:58,17:60,18:61,19:63,20:64,
            21:65,22:66,23:67,24:69,25:70,26:72,27:73,28:74,29:75,30:77,31:79,32:79,
            33:80,34:80,35:80,36:80},
    "tot": {56:40,57:40,58:40,59:42,60:44,61:46,62:47,63:48,64:50,65:51,66:52,67:53,
            68:53,69:54,70:55,71:56,72:56,73:57,74:57,75:58,76:58,77:59,78:59,79:60,
            80:60,81:61,82:61,83:61,84:62,85:62,86:62,87:62,88:63,89:63,90:63,91:63,
            92:64,93:64,94:65,95:65,96:65,97:65,98:65,99:66,100:66,101:66,102:66,
            103:67,104:67,105:67,106:68,107:68,108:68,109:68,110:69,111:69,112:69,
            113:69,114:69,115:69,116:69,117:69,118:69,119:70,120:70,121:70,122:71,
            123:71,124:71,125:71,126:71,127:71,128:71,129:72,130:72,131:73,132:73,
            133:74,134:74,135:74,136:74,137:75,138:75,139:75,140:76,141:76,142:77,
            143:77,144:77,145:77,146:77,147:77,148:77,149:77,150:77,151:77,152:77,
            153:77,154:78,155:78,156:78,157:78,158:78,159:78,160:78,161:78,162:78,
            163:78,164:79,165:79,166:79,167:79,168:79,169:79,170:80,171:80,172:80,
            173:80,174:80,175:80,176:80,177:80,178:80,179:80,180:80,181:80,182:80,
            183:80,184:80,185:80,186:80,187:80,188:80,189:80,190:80,191:80,192:80,
            193:80,194:80,195:80,196:80,197:80,198:80,199:80,200:80,201:80,202:80,
            203:80,204:80,205:80,206:80,207:80,208:80,209:80,210:80,211:80,212:80,
            213:80,214:80,215:80,216:80,217:80,218:80,219:80,220:80,221:80,222:80,
            223:80,224:80},
}


def tscore_spm(raw: int | None, secao_id: str, faixa: str) -> int | None:
    """
    Converte raw score em T-score usando as tabelas normativas do SPM.
    Retorna None para seções sem tabela (SME/Olfato e Paladar).
    Clampeia ao mínimo (40) ou máximo (80) se o raw estiver fora da faixa da tabela.
    """
    tables = SPM_P_TSCORE if faixa == "spm_p" else SPM_CASA_TSCORE
    table = tables.get(secao_id)
    if table is None or raw is None:
        return None
    t = table.get(raw)
    if t is not None:
        return t
    # Extrapola: abaixo do mínimo → 40, acima do máximo → 80
    return 40 if raw < min(table) else 80


def classificar_tscore_spm(t: int | None) -> str:
    """
    Classificação por T-score conforme manual SPM:
      40–59T → Típico
      60–69T → Possível disfunções
      70–80T → Disfunções
    """
    if t is None:
        return "N/D"
    if t >= 70:
        return "Disfunções"
    if t >= 60:
        return "Possível disfunções"
    return "Típico"


def calcular_pontuacao_spm(respostas: dict, faixa: str) -> dict:
    """
    respostas: {numero_item: valor (1–4)}
    faixa: 'spm_p' ou 'spm_casa'
    Retorna {secao_id: raw_score, ..., 'tot': total}
    Itens invertidos: score = 5 − valor; demais: score = valor
    TOT = VIS + HEA + TOU + SME + BOD + BAL (sem SOC e sem PLA,
    conforme tabelas normativas do manual SPM).
    """
    if faixa == "spm_p":
        secoes = SECOES_SPM_P
        reversed_set = REVERSED_SPM_P
    else:
        secoes = SECOES_SPM_CASA
        reversed_set = REVERSED_SPM_CASA

    result = {}
    for secao in secoes:
        score = 0
        for item in secao["itens"]:
            v = respostas.get(item, 1)
            score += (5 - v) if item in reversed_set else v
        result[secao["id"]] = score
    result["tot"] = sum(result.get(s, 0) for s in TOT_SECOES)
    return result


def max_score_spm(faixa: str) -> dict:
    """Retorna pontuação máxima por seção e para o TOT (VIS+HEA+TOU+SME+BOD+BAL)."""
    secoes = SECOES_SPM_P if faixa == "spm_p" else SECOES_SPM_CASA
    result = {s["id"]: len(s["itens"]) * 4 for s in secoes}
    result["tot"] = sum(result.get(s, 0) for s in TOT_SECOES)
    return result


def classificar_spm_pct(pct: float) -> str:
    """Mantido para compatibilidade. Prefira classificar_tscore_spm()."""
    if pct >= 75:
        return "Disfunções"
    elif pct >= 60:
        return "Possível disfunções"
    else:
        return "Típico"
