"""
Metadados e prompt compartilhados entre os leitores de formulário via IA
(gemini_reader.py e openai_reader.py) — descrição de cada instrumento
suportado, schema de resposta e o texto do prompt enviado ao modelo de
visão computacional.
"""

# ── Metadados de cada instrumento suportado ─────────────────────────────────
INSTRUMENTOS = {
    "spm_p": {
        "label": "SPM-P Casa (2–5 anos)",
        "total_itens": 75,
        "opcoes": ["N", "O", "F", "S"],
        "descricao_opcoes": "N=Nunca, O=Ocasionalmente, F=Frequentemente, S=Sempre",
        "descricao_form": (
            "Formulário 'SPM-P — Sensory Processing Measure-Preschool', faixa CASA, "
            "para crianças de 2 a 5 anos. Cabeçalho vermelho com 'spm-p' e 'CASA'. "
            "75 itens numerados, 4 colunas de resposta (N | O | F | S) no lado "
            "ESQUERDO da página, à esquerda do texto de cada item. Cada item tem "
            "uma das 4 letras circulada à mão."
        ),
    },
    "spm_casa": {
        "label": "SPM Casa (5–12 anos)",
        "total_itens": 75,
        "opcoes": ["N", "O", "F", "S"],
        "descricao_opcoes": "N=Nunca, O=Ocasionalmente, F=Frequentemente, S=Sempre",
        "descricao_form": (
            "Formulário 'SPM — Sensory Processing Measure', faixa CASA, para "
            "crianças de 5 a 12 anos (não-pré-escolar). 75 itens, mesma estrutura "
            "de 4 colunas (N | O | F | S) no lado ESQUERDO da página."
        ),
    },
    "ps2_bebe_wd": {
        "label": "PS2 Bebê (0–6 meses)",
        "total_itens": 25,
        "opcoes": ["5", "4", "3", "2", "1", "0"],
        "descricao_opcoes": (
            "5=Quase sempre (90%+), 4=Frequentemente (75%), 3=Metade do tempo (50%), "
            "2=Ocasionalmente (25%), 1=Quase nunca (10% ou menos), "
            "0=Não se aplica (coluna extra e mais estreita, à DIREITA da coluna '1', "
            "separada das outras 5 — geralmente sem rótulo de porcentagem)"
        ),
        "descricao_form": (
            "Formulário 'Bebê — Perfil Sensorial 2' (Winnie Dunn), faixa etária "
            "0 a 6 meses, 'Questionário do cuidador'. 25 itens numerados, 6 colunas "
            "de resposta no lado DIREITO da página: 5|4|3|2|1 e depois uma coluna "
            "extra '0' (Não se aplica) ainda mais à direita."
        ),
    },
    "ps2_cp_wd": {
        "label": "PS2 Criança Pequena (7–35 meses)",
        "total_itens": 54,
        "opcoes": ["5", "4", "3", "2", "1", "0"],
        "descricao_opcoes": (
            "5=Quase sempre (90%+), 4=Frequentemente (75%), 3=Metade do tempo (50%), "
            "2=Ocasionalmente (25%), 1=Quase nunca (10% ou menos), "
            "0=Não se aplica (coluna extra e mais estreita, à DIREITA da coluna '1', "
            "separada das outras 5 — geralmente sem rótulo de porcentagem)"
        ),
        "descricao_form": (
            "Formulário 'Criança Pequena — Perfil Sensorial 2' (Winnie Dunn), "
            "faixa etária 7 a 35 meses, 'Questionário do cuidador'. 54 itens "
            "numerados (alguns marcados com * são itens extras/bônus, mas mesmo "
            "assim devem ser extraídos), 6 colunas de resposta no lado DIREITO da "
            "página: 5|4|3|2|1 e depois uma coluna extra '0' (Não se aplica) ainda "
            "mais à direita, separada visualmente das outras."
        ),
    },
    "adulto_sensorial": {
        "label": "Perfil Sensorial Adulto/Adolescente",
        "total_itens": 60,
        "opcoes": ["1", "2", "3", "4", "5"],
        "descricao_opcoes": (
            "1=Quase nunca, 2=Raramente, 3=Ocasionalmente, 4=Frequentemente, "
            "5=Quase sempre"
        ),
        "descricao_form": (
            "Formulário 'Perfil Sensorial do Adulto/Adolescente'. 60 itens, 5 "
            "colunas de resposta (1|2|3|4|5, da esquerda — Quase nunca — para a "
            "direita — Quase sempre) no lado DIREITO da página."
        ),
    },
    "sensorial": {
        "label": "Perfil Sensorial 2 — Criança (3–14 anos)",
        "total_itens": 86,
        "opcoes": ["5", "4", "3", "2", "1", "0"],
        "descricao_opcoes": (
            "5=Quase sempre (90%+), 4=Frequentemente (75%), 3=Metade do tempo (50%), "
            "2=Ocasionalmente (25%), 1=Quase nunca (10% ou menos), "
            "0=Não se aplica (coluna extra e mais estreita, à DIREITA da coluna '1', "
            "separada das outras 5 — geralmente sem rótulo de porcentagem)"
        ),
        "descricao_form": (
            "Formulário 'Perfil Sensorial 2' para crianças de 3 a 14 anos. 86 "
            "itens numerados, 6 colunas de resposta no lado DIREITO da página: "
            "5|4|3|2|1 e depois uma coluna extra '0' (Não se aplica) ainda mais "
            "à direita."
        ),
    },
}

_RESPOSTA_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "item": {"type": "integer", "description": "Número do item no formulário"},
        "valor": {
            "type": "string",
            "description": (
                "A opção marcada/circulada para este item. Para SPM use uma das "
                "letras N, O, F, S. Para PS2/Adulto use o número da coluna "
                "marcada (string, ex: '5'; ou '0' para a coluna extra 'Não se "
                "aplica' quando presente no formulário). Use string vazia '' "
                "se nenhuma marca for identificável com segurança."
            ),
        },
        "confianca": {
            "type": "string",
            "enum": ["alta", "baixa"],
            "description": "alta se a marca está clara e inequívoca; baixa se está ambígua, leve ou entre duas opções",
        },
    },
    "required": ["item", "valor", "confianca"],
}

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "instrumento": {
            "type": "string",
            "enum": list(INSTRUMENTOS.keys()) + ["desconhecido"],
            "description": "Código do instrumento identificado na capa/cabeçalho do formulário",
        },
        "nome_crianca": {"type": "string", "description": "Nome completo da criança/paciente, do cabeçalho. Vazio se não encontrado."},
        "nome_responsavel": {"type": "string", "description": "Nome do pai/mãe/cuidador/responsável que preencheu. Vazio se não encontrado."},
        "data_nascimento": {"type": "string", "description": "Data de nascimento no formato AAAA-MM-DD. Vazio se não encontrado."},
        "respostas": {
            "type": "array",
            "items": _RESPOSTA_ITEM_SCHEMA,
        },
    },
    "required": ["instrumento", "respostas"],
}


def montar_prompt(forcar_tipo: str = None) -> str:
    if forcar_tipo and forcar_tipo in INSTRUMENTOS:
        info = INSTRUMENTOS[forcar_tipo]
        contexto_instrumento = (
            f"O instrumento já foi confirmado como: {forcar_tipo} — {info['label']}.\n"
            f"{info['descricao_form']}\n"
            f"Opções de resposta possíveis: {info['descricao_opcoes']}.\n"
            f"O formulário tem {info['total_itens']} itens numerados de 1 a "
            f"{info['total_itens']}. Extraia TODOS eles, mesmo os marcados com "
            f"asterisco (*) ou que pareçam itens 'bônus'.\n"
            f"No campo 'instrumento' da resposta, retorne exatamente '{forcar_tipo}'."
        )
    else:
        lista = "\n".join(
            f"- {codigo}: {info['label']} — {info['descricao_form']}"
            for codigo, info in INSTRUMENTOS.items()
        )
        contexto_instrumento = (
            "Primeiro identifique QUAL dos instrumentos abaixo está nas imagens, "
            "olhando o título/capa e a quantidade de itens e colunas:\n" + lista
        )

    return f"""Você é um assistente especializado em digitar formulários clínicos de
avaliação sensorial (Perfil Sensorial / SPM, de Winnie Dunn / Pearson / WPS),
preenchidos à mão por pais, cuidadores ou profissionais.

{contexto_instrumento}

Cada item do formulário tem uma pergunta numerada e, ao lado, colunas de
resposta com letras ou números. O respondente CIRCULA ou MARCA uma das
opções por item (às vezes com X, círculo, ou traço sobre a letra/número).

Para CADA item numerado visível nas imagens, identifique:
- "item": o número do item (inteiro)
- "valor": qual opção foi marcada (letra N/O/F/S para SPM, ou número 1-5 para PS2/Adulto).
  ATENÇÃO nos formulários PS2 (Bebê, Criança Pequena, Criança 3-14): existe uma
  coluna "0" (Não se aplica) separada e MAIS À DIREITA da coluna "1" — não
  confunda uma marca na coluna "0" com a coluna "1". Se a marca estiver
  claramente na coluna mais à direita (separada, sem % de frequência), retorne
  valor="0".
  Se nenhuma marca for visível ou estiver ambígua entre duas opções, retorne
  valor="" e confianca="baixa".
- "confianca": "alta" se a marca é clara, "baixa" se está leve, borrada, ou
  ambígua entre duas colunas adjacentes.

ATENÇÃO ESPECIAL nos formulários SPM (spm_p, spm_casa): em cada linha existem
QUATRO letras lado a lado bem à esquerda — N, O, F, S — e o respondente
desenha um círculo À MÃO em volta de APENAS UMA letra por linha (círculo
pequeno e apertado em torno da letra, ex.: "Ⓝ" ou "Ⓞ"). Para decidir o
"valor", olhe exatamente qual letra está dentro do traço de caneta — não
adivinhe pela posição. Ignore totalmente os números impressos acima de cada
coluna (em algumas seções aparecem como 1,2,3,4 e em outras como 4,3,2,1):
esses números são só pontuação manual de referência do formulário e NÃO
indicam a resposta — o que importa é unicamente qual letra (N/O/F/S) foi
circulada.

PROIBIDO "chutar" ou inferir a resposta por suposição (ex.: assumir que uma
criança típica responderia "Sempre" em itens positivos). Você DEVE basear
cada "valor" exclusivamente na marca de caneta realmente visível na imagem
para aquele item, examinando cada uma das 4 letras da linha individualmente.
Se ao olhar com atenção você não enxergar nenhum traço de caneta claro em
nenhuma das 4 letras daquela linha, retorne valor="" e confianca="baixa" —
isso é preferível a inventar uma resposta plausível.

IMPORTANTE:
- NÃO pule itens. Retorne uma entrada para CADA número de item do formulário,
  mesmo que a marca não seja legível (nesse caso valor="", confianca="baixa").
- Preste atenção especial a marcas na coluna mais à esquerda (geralmente
  "Nunca"/menor valor) — elas costumam ser sutis e fáceis de perder.
- Também extraia do cabeçalho/capa: nome da criança (nome completo, juntando
  "Primeiro nome" + "Sobrenome" se estiverem em campos separados), nome do
  responsável que preencheu, e data de nascimento (formato AAAA-MM-DD).

Responda SOMENTE com o JSON estruturado conforme o schema fornecido."""
