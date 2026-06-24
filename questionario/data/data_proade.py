# PROADE — Protocolo de Avaliação do Desempenho Escolar
# Baseado nos descritores curriculares da BNCC (1º ao 5º ano do EF)
# Aplicado pelo profissional durante a avaliação presencial

PROADE_OPCOES = [
    {"valor": 0, "label": "Não"},
    {"valor": 1, "label": "Parcialmente"},
    {"valor": 2, "label": "Sim"},
]

PROADE_AREAS = [
    {"id": "linguagem_oral", "nome": "Linguagem Oral",          "cor": "#3E73D1", "icone": "mic"},
    {"id": "leitura",        "nome": "Leitura",                 "cor": "#16A085", "icone": "book-open"},
    {"id": "escrita",        "nome": "Escrita",                 "cor": "#8E44AD", "icone": "pen-line"},
    {"id": "matematica",     "nome": "Matemática",              "cor": "#E67E22", "icone": "calculator"},
    {"id": "psicossocial",   "nome": "Aspectos Psicossociais",  "cor": "#E74C3C", "icone": "heart"},
]

PROADE_ANOS = [1, 2, 3, 4, 5]

# ─── Itens por área e ano ─────────────────────────────────────────────────────
# Formato: {area_id: {ano: [(numero, texto), ...]}}
# Numeração global: linguagem 1-30, leitura 31-60, escrita 61-90,
#                  matemática 91-120, psicossocial 121-150

PROADE_ITENS = {
    "linguagem_oral": {
        1: [
            (1,  "Nomeia objetos do cotidiano com vocabulário adequado para a faixa etária."),
            (2,  "Compreende e executa comandos verbais simples com dois passos."),
            (3,  "Relata eventos vivenciados mantendo uma sequência lógica."),
            (4,  "Usa frases com sujeito, verbo e complemento de forma espontânea."),
            (5,  "Faz perguntas para esclarecer dúvidas durante a comunicação."),
            (6,  "Pronuncia a maioria dos fonemas com clareza e inteligibilidade."),
        ],
        2: [
            (7,  "Descreve situações com detalhes e coerência."),
            (8,  "Usa pronomes e conectivos básicos de forma adequada."),
            (9,  "Compreende e executa instruções com três ou mais passos."),
            (10, "Narra histórias com início, meio e fim reconhecíveis."),
            (11, "Participa de conversas respeitando os turnos de fala."),
            (12, "Usa vocabulário mais amplo e variado que o esperado para o 1º ano."),
        ],
        3: [
            (13, "Expõe ideias com argumentação simples e coerente."),
            (14, "Usa vocabulário variado e preciso em diferentes contextos."),
            (15, "Compreende linguagem figurada simples (metáforas, provérbios conhecidos)."),
            (16, "Resume oralmente textos ouvidos com suas próprias palavras."),
            (17, "Faz inferências a partir de informações implícitas em textos orais."),
            (18, "Diferencia fatos de opiniões em discursos e conversas."),
        ],
        4: [
            (19, "Argumenta e defende um ponto de vista com fundamentação."),
            (20, "Usa vocabulário formal em situações de comunicação que exigem."),
            (21, "Compreende textos expositivos e informativos ouvidos."),
            (22, "Identifica a intenção comunicativa em diferentes contextos."),
            (23, "Realiza apresentações orais com organização e clareza."),
            (24, "Usa recursos expressivos como entonação e pausas de forma adequada."),
        ],
        5: [
            (25, "Produz discurso oral com coesão e coerência em diferentes situações."),
            (26, "Reconhece variações linguísticas regionais e formais/informais."),
            (27, "Argumenta com fundamentação lógica em debates e discussões."),
            (28, "Adapta o registro linguístico ao interlocutor e à situação."),
            (29, "Interpreta criticamente textos orais de maior complexidade."),
            (30, "Planeja e realiza apresentações orais com estrutura elaborada."),
        ],
    },

    "leitura": {
        1: [
            (31, "Reconhece e nomeia todas as letras do alfabeto."),
            (32, "Associa fonema a grafema com precisão."),
            (33, "Lê sílabas simples (CV, VC) com fluência."),
            (34, "Decifra palavras dissílabas de estrutura simples."),
            (35, "Identifica o título e a função de um texto."),
            (36, "Lê pequenas frases com compreensão."),
        ],
        2: [
            (37, "Lê palavras com sílabas complexas (CVC, CCV) sem suporte."),
            (38, "Lê frases simples com fluência e ritmo adequados."),
            (39, "Compreende pequenos textos narrativos após a leitura."),
            (40, "Identifica o assunto principal de um texto curto."),
            (41, "Reconhece a finalidade de diferentes tipos de texto."),
            (42, "Lê em voz alta com entonação adequada ao ponto final e ponto de interrogação."),
        ],
        3: [
            (43, "Lê textos de maior extensão com fluência e compreensão."),
            (44, "Localiza informações explícitas no texto sem dificuldade."),
            (45, "Faz inferências simples a partir do contexto do texto."),
            (46, "Identifica a sequência de eventos em textos narrativos."),
            (47, "Reconhece diferentes gêneros textuais e suas características."),
            (48, "Usa estratégias de leitura (título, imagens, subtítulos) antes de ler."),
        ],
        4: [
            (49, "Lê textos com vocabulário especializado com razoável compreensão."),
            (50, "Distingue informação principal de informações secundárias."),
            (51, "Relaciona informações de diferentes partes de um mesmo texto."),
            (52, "Identifica a intenção do autor em diferentes textos."),
            (53, "Compreende textos informativos e argumentativos simples."),
            (54, "Usa o contexto para inferir o significado de palavras desconhecidas."),
        ],
        5: [
            (55, "Lê textos de diferentes gêneros com proficiência e autonomia."),
            (56, "Analisa criticamente o conteúdo e a forma de textos lidos."),
            (57, "Relaciona o texto a conhecimentos prévios e a outros textos."),
            (58, "Identifica recursos estilísticos como ironia, humor e metáfora."),
            (59, "Compreende textos com múltiplas ideias e argumentos encadeados."),
            (60, "Realiza leitura autônoma e interpreta textos complexos sem apoio."),
        ],
    },

    "escrita": {
        1: [
            (61, "Escreve o próprio nome completo sem modelo."),
            (62, "Copia palavras e frases do quadro sem erros grosseiros."),
            (63, "Produz palavras ditadas de estrutura silábica simples (CV, VC)."),
            (64, "Escreve pequenas frases com sentido compreensível."),
            (65, "Utiliza espaço entre palavras adequadamente."),
            (66, "Escreve da esquerda para a direita e de cima para baixo de forma consistente."),
        ],
        2: [
            (67, "Produz palavras com sílabas complexas sem apoio."),
            (68, "Escreve frases completas com pontuação básica (ponto final, ponto de interrogação)."),
            (69, "Produz pequenos textos narrativos com início e fim reconhecíveis."),
            (70, "Usa maiúsculas no início de frases e em nomes próprios."),
            (71, "Organiza o texto com paragrafação básica."),
            (72, "Revisa e corrige erros ortográficos simples com apoio do professor."),
        ],
        3: [
            (73, "Produz textos narrativos com estrutura clara (início, desenvolvimento e fim)."),
            (74, "Usa pontuação variada com razoável adequação ao contexto."),
            (75, "Demonstra coerência e progressão temática no texto produzido."),
            (76, "Usa conectivos básicos para ligar ideias dentro do texto."),
            (77, "Escreve com legibilidade e organização visual adequadas."),
            (78, "Reescreve texto com mudanças solicitadas de forma adequada."),
        ],
        4: [
            (79, "Produz textos de diferentes gêneros (conto, carta, notícia, etc.)."),
            (80, "Usa vocabulário variado e expressivo na escrita."),
            (81, "Mantém coerência e coesão ao longo do texto."),
            (82, "Usa pontuação de forma adequada na maioria dos casos."),
            (83, "Revisa o próprio texto identificando e corrigindo erros ortográficos."),
            (84, "Adequa a linguagem ao gênero e ao interlocutor."),
        ],
        5: [
            (85, "Produz textos argumentativos com posicionamento claro e sustentado."),
            (86, "Usa recursos de coesão textual com domínio."),
            (87, "Demonstra domínio ortográfico na maioria das palavras."),
            (88, "Planeja e revisa o texto de forma autônoma e sistemática."),
            (89, "Adapta o registro ao gênero e à situação comunicativa."),
            (90, "Produz textos com criatividade, originalidade e organização."),
        ],
    },

    "matematica": {
        1: [
            (91,  "Conta e representa quantidades até 100."),
            (92,  "Lê e escreve numerais de 0 a 100."),
            (93,  "Compara e ordena números em sequência crescente e decrescente."),
            (94,  "Realiza adições simples com resultados até 20."),
            (95,  "Realiza subtrações simples com resultados até 20."),
            (96,  "Identifica formas geométricas básicas (círculo, quadrado, triângulo, retângulo)."),
        ],
        2: [
            (97,  "Lê e escreve numerais até 1.000."),
            (98,  "Realiza adições e subtrações com agrupamento e reagrupamento."),
            (99,  "Compreende o conceito de multiplicação como adição repetida."),
            (100, "Identifica metades e quartos de figuras e grupos de objetos."),
            (101, "Resolve problemas com uma operação matemática."),
            (102, "Mede comprimentos com unidades não convencionais."),
        ],
        3: [
            (103, "Opera com números até 10.000 sem dificuldade."),
            (104, "Realiza multiplicações e divisões simples com fluência."),
            (105, "Compreende frações simples (½, ¼, ⅓) e representa graficamente."),
            (106, "Resolve problemas com duas operações matemáticas."),
            (107, "Trabalha com unidades de medida convencionais (cm, m, kg, litro)."),
            (108, "Lê e interpreta tabelas e gráficos simples."),
        ],
        4: [
            (109, "Opera com números maiores incluindo decimais simples."),
            (110, "Realiza multiplicações e divisões com mais de um dígito."),
            (111, "Compreende e opera com frações equivalentes."),
            (112, "Calcula perímetro de figuras planas."),
            (113, "Resolve problemas com múltiplas etapas usando diferentes estratégias."),
            (114, "Interpreta dados em gráficos de barras e tabelas."),
        ],
        5: [
            (115, "Opera com números decimais e fracionários com segurança."),
            (116, "Calcula porcentagens simples e aplica em situações cotidianas."),
            (117, "Compreende e aplica o conceito de área de figuras planas."),
            (118, "Resolve problemas complexos com raciocínio lógico e estratégico."),
            (119, "Reconhece e usa regularidades e padrões numéricos."),
            (120, "Usa representações gráficas para comunicar soluções matemáticas."),
        ],
    },

    "psicossocial": {
        1: [
            (121, "Adapta-se à rotina e às regras da escola sem resistência excessiva."),
            (122, "Demonstra interesse pelas atividades escolares propostas."),
            (123, "Interage positivamente com colegas e professores."),
            (124, "Controla impulsos em situações de frustração de forma minimamente adequada."),
            (125, "Mantém atenção em tarefas por tempo adequado à faixa etária."),
            (126, "Solicita ajuda ao professor quando encontra dificuldades."),
        ],
        2: [
            (127, "Cumpre tarefas escolares com autonomia crescente."),
            (128, "Mantém organização mínima do material escolar."),
            (129, "Demonstra autoestima e confiança nas próprias capacidades."),
            (130, "Respeita regras em jogos e brincadeiras coletivas."),
            (131, "Gerencia conflitos com colegas de forma minimamente adequada."),
            (132, "Persiste em tarefas desafiadoras sem desistir rapidamente."),
        ],
        3: [
            (133, "Demonstra responsabilidade com compromissos escolares."),
            (134, "Trabalha bem em grupo, contribuindo e respeitando os colegas."),
            (135, "Regula emoções em situações de pressão ou avaliação."),
            (136, "Planeja e organiza suas atividades com apoio mínimo."),
            (137, "Demonstra motivação para aprender e buscar conhecimento."),
            (138, "Aceita críticas e feedbacks de forma construtiva."),
        ],
        4: [
            (139, "Organiza e planeja tarefas com crescente autonomia."),
            (140, "Demonstra iniciativa em atividades escolares e projetos."),
            (141, "Administra o tempo de forma eficaz nas tarefas escolares."),
            (142, "Resolve conflitos com estratégias socioemocioanais adequadas."),
            (143, "Demonstra empatia e respeito pela diversidade."),
            (144, "Lida com a pressão de desempenho escolar de forma equilibrada."),
        ],
        5: [
            (145, "Planeja e executa projetos com considerável autonomia."),
            (146, "Demonstra maturidade emocional e autorregulação adequadas."),
            (147, "Assume responsabilidade pelos próprios erros e aprendizagens."),
            (148, "Demonstra liderança e cooperação em atividades em grupo."),
            (149, "Tem perspectiva positiva em relação à sua própria escolarização."),
            (150, "Demonstra autoconhecimento das próprias dificuldades e potencialidades."),
        ],
    },
}

# Itens por número global → (area_id, ano)
PROADE_MAPA_ITEM = {}
for _area_id, _anos in PROADE_ITENS.items():
    for _ano, _itens in _anos.items():
        for _num, _ in _itens:
            PROADE_MAPA_ITEM[_num] = (_area_id, _ano)

PROADE_ITENS_POR_AREA = {
    area_id: 6
    for area_id in [a["id"] for a in PROADE_AREAS]
}

PROADE_MAX_AREA = 12  # 6 itens × 2 pontos
PROADE_MAX_TOTAL = 60  # 5 áreas × 12

PROADE_CLASSIFICACAO = [
    ("Desempenho esperado",              10, 12),
    ("Desempenho satisfatório",           7,  9),
    ("Dificuldades moderadas",            4,  6),
    ("Dificuldades significativas",       0,  3),
]


def classificar_area_proade(pontos: int) -> str:
    for label, mn, mx in PROADE_CLASSIFICACAO:
        if mn <= pontos <= mx:
            return label
    return PROADE_CLASSIFICACAO[-1][0]


def cor_classificacao_proade(label: str) -> str:
    return {
        "Desempenho esperado":      "#D1FAE5",
        "Desempenho satisfatório":  "#DBEAFE",
        "Dificuldades moderadas":   "#FEF3C7",
        "Dificuldades significativas": "#FEE2E2",
    }.get(label, "#F3F4F6")
