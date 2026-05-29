"""
Analisa, classifica e importa os documentos em docs_extraidos/docs/
"""
import os, sys, re, hashlib, unicodedata, django
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "perfil_sensorial.settings")
django.setup()

from django.core.files import File
from documentos.models import CategoriaDocumento, Documento
from questionario.models import Especialidade

DOCS_DIR = BASE_DIR / "docs_extraidos" / "docs"
EXTENSOES_OK = {".pdf", ".docx", ".doc"}


# ── Normalização ─────────────────────────────────────────────────────────────
def norm(texto):
    """Normaliza para comparação: minúsculo, sem acentos, separadores → espaço."""
    # NFC: converte decomposed (NFD) para composed (NFC) antes de qualquer coisa
    t = unicodedata.normalize("NFC", texto).lower()
    # Remove extensão para matching
    t = re.sub(r'\.(pdf|docx|doc|xlsx|xls)$', '', t)
    for src, dst in [
        ("ã","a"),("â","a"),("á","a"),("à","a"),("ä","a"),
        ("ê","e"),("é","e"),("è","e"),("ë","e"),
        ("î","i"),("í","i"),("ï","i"),
        ("ô","o"),("ó","o"),("õ","o"),("ö","o"),
        ("û","u"),("ú","u"),("ü","u"),
        ("ç","c"),("ñ","n"),
        ("-"," "),("_"," "),("+","  "),
    ]:
        t = t.replace(src, dst)
    # Colapsa múltiplos espaços
    t = t.replace(",", " ").replace(".", " ")
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def match(nome_arquivo, *padroes):
    n = norm(nome_arquivo)
    for p in padroes:
        np = norm(p).strip()
        if np and np in n:
            return True
    return False


# ── Regras de categoria ─────────────────────────────────────────────────────
# (codigo, nome, icone, ordem, palavras-chave)
REGRAS_CATEGORIA = [
    ("anamnese", "Anamnese", "clipboard", 1, [
        "anamnese", "anamnse", "entrevista com os pais", "entrevista semiestruturada",
        "histórico", "historico",
        "modelo de entrevista", "entrevista boderline", "entrevista borderline",
    ]),
    ("atestado", "Atestado / Declaração / Autorização", "shield-check", 2, [
        "atestado", "declaracao", "declaração", "autorização", "autorizacao",
        "autorizacao-para", "atestado-de", "atestado-psicologico",
    ]),
    ("laudo", "Laudo", "file-check", 3, [
        "laudo",
    ]),
    ("relatorio", "Relatório", "bar-chart-2", 4, [
        "relatório", "relatorio", "relatórios", "relatorios",
    ]),
    ("contrato", "Contrato / Termo", "file-text", 5, [
        "contrato", "termo", "tcle", "consentimento", "prestação de serviço",
        "acordo de regras", "compromisso", "carta de solicitação", "carta-de",
        "carta para transporte", "solicitacao de credenciamento", "reembolso ao convenio",
        "solicitação de reembolso",
    ]),
    ("carta", "Carta / Encaminhamento", "mail", 6, [
        "carta-de-recomendacao", "carta-de-pedido", "candidatura",
        "carta-para-transporte", "encaminhamento", "encaminhamento-",
        "modelo de encaminhamento",
    ]),
    ("questionario", "Questionário", "list", 7, [
        "questionário", "questionario", "quastionario", "quociente",
        "quandro de sintomas",
    ]),
    ("escala", "Escala / Inventário", "bar-chart", 8, [
        "escala", "inventário", "inventario",
        "bis-11", "bis 11", "scl 90", "s.c.l", "dsq-40", "dsq 40",
        "snap", "sdq", "cars", "mchat", "m-chat", "m chat",
        "masc", "pas ", "dcdq", "conners",
        "lpi", "bpi", "bpq", "qmpi", "cdrs", "scared",
        "vineland", "vbmapp", "vb maap",
        "abc iça", "ica ", "auqei", "esdm", "ces-d", "adape",
        "executive skills", "had ", "had.",
        "aq10", "aq 10", "aq ", "aq_",
        "dass-21", "dass 21",
        "etdah", "iar ", "iar-", "iar1",
        "avaliação do uso de substâncias",
        "avaliação do objetivo de abstinência",
        "lista de sintomas limitrofes", "bsl 23",
        "borderline personality questionnaire",
        "iapssm", "eedm",
        "sintomas", "diagnóstico",
        "ucla ", "resiliencia",
        "avaliacao-do-risco-de-suicidio", "risco de suicidio", "risco-de-suicidio",
        "avaliacao do risco", "avaliação do risco",
        "wisc", "wisc-iv",
        "token test", "token-test",
        "teste de transtorno de personalidade",
        "17)+qa",
    ]),
    ("teste", "Teste / Prova", "search", 8, [
        "teste", "prova de leitura", "prova para lateralidade",
        "torre de londres", "trilhas",
        "cancelamento", "cloze", "pede ",
        "avaliação exploratoria", "avaliacao exploratoria",
        "avaliação exloratoria", "avaliacao exloratoria",
        "teste contrastivo", "compreensão auditiva e de leitura",
        "niveis da escrita", "nível da escrita", "nivel da escrita",
        "modelo de prova para",
        "kit 1 super atencao", "kit 1", "kit 5", "kit 6",
        "super atencao", "mente ativa", "aprendizagem sem barreiras",
        "saiba como reconhecer o bom funcionamento",
        "coordenacao motora", "coordenação motora",
    ]),
    ("protocolo", "Protocolo / Instrumento", "clipboard-list", 9, [
        "protocolo", "instrumento",
        "checklist", "check list", "check-list",
        "pdi", "snap-iv", "snap iv",
        "afls", "ablls", "ablls-r", "kit-ablls", "kit ablls",
        "aplicação abbls", "aplicacao ablls", "ablls programas",
        "acompanhamento-de-experiencia", "acompanhamento de experiencia",
        "atividade-de-treinamento", "avaliacao-inicial",
        "avaliacao-postural",
    ]),
    ("recurso", "Recurso Terapêutico", "heart", 10, [
        "recurso", "exercício", "exercicio", "técnica", "tecnica",
        "habilidade", "enfrentamento",
        "planilha", "plano de", "plano de emergência", "plano de prevencao",
        "roda das", "onda de", "tabuleiro",
        "tempestade", "iceberg", "registro de pensamento", "registro-pensamento",
        "distorções", "distorcoes", "gratidão", "gratidao",
        "autoestima", "autoimagem", "medos",
        "crenças", "crencas", "mindfulness", "meditação", "meditacao",
        "metas", "tomando decisões", "trabalhando emoções",
        "emoções", "regulação", "regulacao",
        "gráfico", "grafico",
        "baralho", "cartas mel", "cartas raiva", "cartas divertidamente",
        "cartas emocionopolis",
        "combater a ansiedade", "ciclo de", "ciclo da",
        "mapeando a ansiedade",
        "ansiedade.pdf", "b. ansiedade", "ansiedade social",
        "pensamentos ansiosos", "pensamentos negativos", "pensamento-negativos",
        "depressão pos parto", "depressao pos parto",
        "ferramentas para lidar", "ferramentastratamento",
        "ferramentas terapeuticas",
        "estratégias para controlar", "estrategias para controlar",
        "estratégias para lidar", "estrategias para lidar",
        "dicas de manejo", "dicas para os pais",
        "maneiras de ajudar",
        "balança decisória", "balanca decisoria",
        "exame de vantagens", "estágios de mudança", "estagios de mudanca",
        "ação alternativa", "acao alternativa",
        "construindo novos hábitos", "construindo novos habitos",
        "contruindo ambivelencia",
        "diagrama do cérebro", "diagrama do cerebro",
        "gatilhos", "gatilho",
        "annex ", "anexo ",
        "amostra de automonitoramento",
        "diario de progresso", "diário de progresso",
        "raiva ", "cartas raiva", "tabuleiro raiva", "instruçoes raiva",
        "quando a raiva", "o ciclo da raiva",
        "burnout", "identificandoburnout",
        "analise seus problemas",
        "dependencia emocional", "dependência emocional",
        "mantendo-se bem", "sinais de alerta",
        "kit-tcc", "kit tcc",
        "atividades positivas", "melhor eu possível", "melhor eu possivel",
        "exploracao de pontos fortes", "exploração de pontos fortes",
        "registro-pensamentos",
        "pessoas lugares e coisas", "pessoas, lugares",
        "auto conhecimento", "autoconhecimento",
        "que tipo de procrastinador",
        "cadernodepressao", "caderno de depressao",
        "ideias de atividades",
        "lista de meritos", "lista de méritos",
        "apoio social",
        "amostra de automonitoramento",
        "baralho investigando", "baralho dependencia",
        "baralho caminhos",
        "combo borderline", "combo relacionamento",
        "caderno agendamento", "caderno de terapia",
        "diario ", "jornal de comunicação",
        "acalme-se", "a c a l m e",
        "lutar ou fugir", "beneficio do exercicio",
        "exercicio fisico",
        "explorando a ansiedade", "explorando-a-ansiedade",
        "desafiando-pensamentos", "ataque-de-panico",
        "informacao-sobre-depressao", "atividades-positivas",
        "registro-pensamentos", "habilidade-de-enfrentamento",
        "ciclo-de", "ciclo-da",
        "meditacao", "mindfulness",
        "trauma ", "lutar-ou-fugir",
        "resolucao de conflitos", "resolução de conflitos",
        "calendário do humor", "calendario do humor",
        "cópia de custos do gerenciamento",
        "cópia de estilos desadaptativos",
        "cópia de questoes de avaliação",
        "estilo de aprendizagem",
        "superando trauma",
    ]),
    ("roteiro_sessao", "Roteiro de Sessão", "layout", 11, [
        "roteiro", "sessão", "sessao",
        "perguntas para", "perguntas terapeuticas", "perguntas norteadoras",
        "perguntas para crianças", "perguntas para o paciente",
        "500 perguntas", "1000-perguntas", "1000 perguntas",
        "100-perguntas", "100 perguntas",
        "130 perguntas", "300 perguntas", "300 perguntas",
        "neuroplasticidade-500",
        "sessão de avaliação",
        "conduzindo entrevistas", "conduzindo-entrevistas",
        "apostila terapeuta de casal", "apostila",
        "psicoterapia para adolescentes",
        "psicoterapia com adolescentes",
        "como funciona a terapia",
        "fomentando esperança",
        "combo borderline",
        "9-perguntas", "perguntas de exploracao", "perguntas de exploração",
        "conversas dificeis", "conversasdificeis",
    ]),
    ("psicoeducacao", "Psicoeducação", "book-open", 12, [
        "psicoeducação", "psicoeducacao",
        "informação sobre depressão", "informacao sobre depressao",
        "transtorno bipolar sinais",
        "bipolar sinais de alerta",
        "neuroplasticidade",
        "modelo cognitivo", "modelo comportamental", "modelo-comportamental",
        "terapia-cognitiva", "terapia cognitiva",
        "o ciclo da ansiedade",
    ]),
    ("material_infantil", "Material Infantil / TEA", "smile", 13, [
        "criança", "crianca", "infantil",
        "tea ", "tod.", "trem do pensamento",
        "emocionópolis", "emocionopolis",
        "opostos",
        "rotina banheiro", "rotina_",
        "flipbook", "arasaac", "caa_",
        "comunicação alternativa", "comunicacao alternativa",
        "regras trem", "regras emocionop",
        "mudando os planos", "acalmar",
        "nível ", "nivel ",
        "manhã tarde e noite", "manha tarde e noite",
        "labirinto",
        "quadro incentivo desfralde", "atividades tod",
        "instrução mel", "instrucao mel",
        "criando uma sala de aula",
        "como estimular a linguagem",
        "cartas mel e abelhas", "instrução mel e abelhas",
        "explorando o tdah de forma divertida",
        "jogo - emocionopolis", "jogo emocionopolis",
        "caixa-divertidamente", "trabalhando-o-filme-divertidamente",
        "minhas-emocoes-divertidamente", "cartas-divertidamente",
        "copia de safari", "tea cognicao", "tea cognição",
        "tea mudando", "tod. acalmar",
        "copia de caixa", "copia de cartas-divertidamente",
        "copia de trabalhando",
        "cópia de livreto das emocoes",
    ]),
    ("manual", "Manual / Referência", "book", 14, [
        "manual", "dsm", "cid ",
        "101 técnicas", "101-tecnicas",
        "300 exercícios", "300 exercicios",
        "normative data", "normative-data",
        "livro de registro",
        "apostila",
        "guia de",
    ]),
    ("avaliacao_psicologica", "Avaliação Psicológica", "search", 15, [
        "avaliação psicologica", "avaliação psicológica",
        "avaliacao psicologica",
        "avaliacao inicial de psicologia",
        "avaliacao postural",
    ]),
    ("ficha", "Ficha / Prontuário", "user", 16, [
        "ficha", "prontuário", "prontuario", "cadastro", "triagem",
        "atendimentos", "formulário", "formulario",
        "auxílio à coleta", "auxilio a coleta",
        "livreto das emocoes", "livreto das emoções",
    ]),
    ("outros", "Outros", "file", 99, []),
]

# ── Regras de especialidade (normalizado) ───────────────────────────────────
REGRAS_ESPECIALIDADE = {
    "psicologo": [
        "laudo", "anamnese", "questionário", "questionario",
        "psicoeducação", "psicoeducacao",
        "tcc", "terapia cognitiva", "borderline", "tpb",
        "depressão", "depressao", "ansiedade", "trauma",
        "bipolar", "esquizofrenia", "tdah", "transtorno",
        "suicid", "fobia", "toc", "burnout",
        "dsq", "scl", "lpi", "bsl", "bpq", "bpi",
        "atestado", "declaração", "declaracao",
        "perguntas para", "perguntas terapeuticas",
        "relatório", "relatorio",
        "registro de pensamento", "distorções",
        "conners", "snap", "sdq", "masc", "scared", "cdrs", "ces-d",
        "inventário", "inventario", "etdah", "iar",
        "had ", "aq10", "dass-21",
        "dependencia emocional", "dependência emocional",
        "substâncias", "abstinência", "abuso",
        "burnout", "gatilhos", "estágios de mudança",
        "combo", "apostila terapeuta de casal",
    ],
    "terapeuta_ocupacional": [
        "sensorial", "vineland", "vbmapp", "vmi", "beery",
        "pedi", "mabc", "portage", "edm figueiredo",
        "habilidades adaptativas", "alimentação", "alimentacao",
        "habitos orais", "processamento auditivo",
        "rotina banheiro", "desfralde",
        "flipbook", "arasaac", "comunicação alternativa",
        "nivel ", "nível ",
        "avaliacao postural",
    ],
    "neuropsicoplogo": [
        "neuropsic", "nepsy", "torre de londres", "trilhas",
        "cancelamento", "bateria", "rastreio cognitivo",
        "cognição", "cognicao", "tea cognição",
        "tde ", "tabela com idade cronologica",
        "entrevista semiestruturada de funções executivas",
        "executive skills",
    ],
    "psicopedagogo": [
        "dislexia", "disgrafia", "discalculia", "disortografia",
        "aprendizagem", "escolar", "leitura e escrita", "ele ",
        "prova", "cloze", "pede ", "lateralidade", "provas piaget",
        "adape", "aee ", "psicopedagogia",
        "criando uma sala de aula", "identificando os problemas de seu filho",
    ],
    "analista_aba": [
        "vbmapp", "vb maap", "aba", "comportamento funcional",
        "habilidades adaptativas", "autismo", "autista",
        "tea ", "m-chat", "mchat", "cars",
        "afls", "ablls",
        "nivel ", "nível ",
    ],
    "fonoaudiologo": [
        "linguagem", "fonoaud", "compreensão auditiva",
        "processamento auditivo", "leitura", "comunicação social",
        "scq", "voz", "como estimular a linguagem",
        "comunicação alternativa", "caa_",
    ],
    "pediatra": [
        "desenvolvimento", "marcos", "denver",
        "m-chat", "mchat", "crianca", "criança", "pediatr",
    ],
}

# Arquivos para EXCLUIR
EXCLUIR_PADROES = [
    "pacote+premium+de+certificados",
    "seu mestre mandou",
    "0ab0d7d71ae9d9efa495",
    "acesse+aqui+as+palestras",
    "bo_nus+-+banco+de+frases",
    "bo_nus+-+guia+de+oratoria",
    "website pedi-cat",
    "curriculum-vitae",
    "carta-de-pedido-de-emprego",
    "candidatura-a-uma-vaga",
    "carta-de-recomendacao",
    "carta-de-pedido",
    "_+pacote+premium",
    "kit documentos compilado",
    "acompanhamento-no-periodo-de-experiencia",  # doc de RH, não clínico
    "acompanhamento de experiencia",
]


# ── Funções auxiliares ──────────────────────────────────────────────────────
def md5_arquivo(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(8192), b""):
            h.update(bloco)
    return h.hexdigest()


def limpar_titulo(nome):
    stem = Path(nome).stem
    stem = re.sub(r'\s*\(\d+\)\s*$', '', stem)
    stem = re.sub(r'^\d+[\)\-\+\s]+', '', stem)
    stem = stem.replace("_", " ").replace("+", " ")
    stem = re.sub(r'\.(pdf|docx|doc)$', '', stem, flags=re.IGNORECASE)
    stem = re.sub(r'_\d{8}_\d{6}_\d{4}', '', stem)
    # Remove hashes MD5-like no final ou no nome
    stem = re.sub(r'_[a-f0-9]{20,}(\s*\(\d+\))?$', '', stem)
    stem = re.sub(r'[a-f0-9]{20,}[-_]', '', stem)
    stem = re.sub(r'\s+', ' ', stem).strip()
    # Capitaliza a primeira letra de cada palavra relevante
    if stem == stem.upper():  # se estava tudo maiúsculo
        stem = stem.title()
    stem = stem[0].upper() + stem[1:] if stem else stem
    # Remove prefixo "Cópia De "
    stem = re.sub(r'^Cópia De ', '', stem, flags=re.IGNORECASE)
    stem = re.sub(r'^Copia De ', '', stem, flags=re.IGNORECASE)
    return stem.strip() or "Documento"


def detectar_categoria(nome_arquivo):
    for codigo, nome_cat, icone, ordem, palavras in REGRAS_CATEGORIA:
        if match(nome_arquivo, *palavras):
            return codigo, nome_cat, icone, ordem
    return "outros", "Outros", "file", 99


def detectar_especialidades(nome_arquivo):
    encontradas = set()
    for esp, palavras in REGRAS_ESPECIALIDADE.items():
        if match(nome_arquivo, *palavras):
            encontradas.add(esp)
    return encontradas


def definir_plano(categoria_codigo, nome_arquivo):
    if categoria_codigo in ("laudo", "escala", "protocolo", "avaliacao_psicologica"):
        return "plus"
    if categoria_codigo == "manual":
        if match(nome_arquivo, "dsm", "cid ", "101 técnicas", "101-tecnicas", "300 exercícios"):
            return "elite"
        return "plus"
    return "start"


def nome_base_sem_sufixo(nome):
    stem = Path(nome).stem
    stem = re.sub(r'\s*\(\d+\)\s*$', '', stem).strip().lower()
    return stem


def eh_lixo(nome):
    n = nome.lower()
    for p in EXCLUIR_PADROES:
        if norm(p) in norm(n):
            return True
    return False


# ── Lógica principal ────────────────────────────────────────────────────────
def analisar_e_importar(dry_run=False):
    arquivos = [
        f for f in DOCS_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in EXTENSOES_OK
    ]

    print(f"\n{'='*65}")
    print(f"  Total de arquivos encontrados: {len(arquivos)}")
    print(f"{'='*65}\n")

    # ── 1. Duplicatas por hash ───────────────────────────────────────────
    print("► Detectando duplicatas por conteúdo (MD5)...")
    hash_map = defaultdict(list)
    for f in arquivos:
        try:
            hash_map[md5_arquivo(f)].append(f)
        except Exception:
            pass

    excluidos_hash = set()
    for h, paths in hash_map.items():
        if len(paths) > 1:
            paths.sort(key=lambda p: len(p.name))
            for dup in paths[1:]:
                excluidos_hash.add(dup)
                print(f"  [DUP-hash] {dup.name[:60]}")

    # ── 2. Duplicatas por nome (MESMO sufixo, ex: (1)) ──────────────────
    # IMPORTANTE: não deduplica PDF vs DOCX do mesmo documento
    print("\n► Detectando duplicatas por nome (mesma extensão)...")
    nome_ext_map = defaultdict(list)
    for f in arquivos:
        if f in excluidos_hash:
            continue
        chave = (nome_base_sem_sufixo(f.name), f.suffix.lower())
        nome_ext_map[chave].append(f)

    excluidos_nome = set()
    for (chave, ext), paths in nome_ext_map.items():
        if len(paths) > 1:
            paths.sort(key=lambda p: len(p.name))
            for dup in paths[1:]:
                excluidos_nome.add(dup)
                print(f"  [DUP-nome] {dup.name[:60]}")

    # ── 3. Lixo / irrelevantes ───────────────────────────────────────────
    print("\n► Filtrando arquivos irrelevantes...")
    excluidos_lixo = set()
    for f in arquivos:
        if eh_lixo(f.name):
            excluidos_lixo.add(f)
            print(f"  [LIXO]     {f.name[:70]}")

    # ── 4. Lista final ───────────────────────────────────────────────────
    excluidos_todos = excluidos_hash | excluidos_nome | excluidos_lixo
    para_importar = [f for f in arquivos if f not in excluidos_todos]

    print(f"\n{'='*65}")
    print(f"  Duplicatas conteúdo : {len(excluidos_hash)}")
    print(f"  Duplicatas nome     : {len(excluidos_nome)}")
    print(f"  Irrelevantes        : {len(excluidos_lixo)}")
    print(f"  Para importar       : {len(para_importar)}")
    print(f"{'='*65}\n")

    if dry_run:
        cat_count = defaultdict(int)
        cat_nome_map = {}
        outros_lista = []
        for f in para_importar:
            cat_cod, cat_nome, *_ = detectar_categoria(f.name)
            cat_count[cat_cod] += 1
            cat_nome_map[cat_cod] = cat_nome
            if cat_cod == "outros":
                outros_lista.append(f.name)

        print("► Distribuição por categoria:")
        for cat, qtd in sorted(cat_count.items(), key=lambda x: -x[1]):
            print(f"  {cat_nome_map[cat]:<40} {qtd:>4} docs")

        if outros_lista:
            print(f"\n► Arquivos ainda em 'Outros' ({len(outros_lista)}):")
            for nome in sorted(outros_lista):
                print(f"  {nome}")
        return

    # ── 5. Criar categorias ──────────────────────────────────────────────
    print("► Criando categorias no banco...")
    cat_cache = {}
    for codigo, nome_cat, icone, ordem, _ in REGRAS_CATEGORIA:
        cat, criado = CategoriaDocumento.objects.get_or_create(
            codigo=codigo,
            defaults={"nome": nome_cat, "icone": icone, "ordem": ordem}
        )
        cat_cache[codigo] = cat
        if criado:
            print(f"  [+] {nome_cat}")

    # ── 6. Importar ──────────────────────────────────────────────────────
    print(f"\n► Importando {len(para_importar)} documentos...\n")
    criados = pulados = erros = 0

    for f in sorted(para_importar, key=lambda x: x.name.lower()):
        titulo    = limpar_titulo(f.name)
        cat_cod, _, _, _ = detectar_categoria(f.name)
        categoria = cat_cache[cat_cod]
        plano     = definir_plano(cat_cod, f.name)
        espec_cod = detectar_especialidades(f.name)

        if Documento.objects.filter(titulo=titulo).exists():
            pulados += 1
            continue

        try:
            with open(f, "rb") as arq:
                doc = Documento(titulo=titulo, categoria=categoria,
                                plano_minimo=plano, ativo=True)
                doc.arquivo.save(f.name, File(arq), save=False)
                doc.save()

            if espec_cod:
                doc.especialidades.set(
                    Especialidade.objects.filter(codigo__in=espec_cod)
                )

            print(f"  [OK] {titulo[:55]:<55} | {cat_cod:<22} | {plano}")
            criados += 1

        except Exception as e:
            print(f"  [ERRO] {f.name}: {e}")
            erros += 1

    print(f"\n{'='*65}")
    print(f"  Importados : {criados}")
    print(f"  Já existiam: {pulados}")
    print(f"  Erros      : {erros}")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    analisar_e_importar(dry_run=dry_run)
