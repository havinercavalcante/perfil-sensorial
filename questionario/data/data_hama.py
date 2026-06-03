# HAM-A — Hamilton Anxiety Rating Scale (Hamilton, 1959)
# Escala aplicada pelo clínico. 14 itens, 0-4 cada.
HAMA_OPCOES = [
    {"valor": 0, "label": "Ausente"},
    {"valor": 1, "label": "Leve"},
    {"valor": 2, "label": "Moderado"},
    {"valor": 3, "label": "Grave"},
    {"valor": 4, "label": "Muito grave / Incapacitante"},
]
HAMA_ITENS = [
    (1,  "Humor ansioso — Preocupação, antecipação do pior, apreensão (antecipação com medo), irritabilidade"),
    (2,  "Tensão — Sensação de tensão, fatigabilidade, reação de susto, choro fácil, tremor, sensação de inquietação, incapacidade de relaxar"),
    (3,  "Medos — De escuro, de estranhos, de animais, de trânsito, de multidão"),
    (4,  "Insônia — Dificuldade para adormecer, sono entrecortado, sono não-satisfatório com fadiga ao acordar, sonhos, pesadelos, terrores noturnos"),
    (5,  "Intelectual (cognitivo) — Dificuldade de concentração, memória fraca"),
    (6,  "Humor deprimido — Perda de interesse, pouco prazer em passatempos, depressão, acordar cedo, variação diurna"),
    (7,  "Somático (muscular) — Dores e fadigas musculares, rigidez, espasmos, contrações, mioclônus, ranger os dentes, voz insegura, tono muscular aumentado"),
    (8,  "Somático (sensorial) — Zumbidos, visão embaçada, ondas de calor ou frio, sensação de fraqueza, sensação de formigamento"),
    (9,  "Sintomas cardiovasculares — Taquicardia, palpitações, dor no peito, pulsação em vasos, sensação de desmaio, extrassístole"),
    (10, "Sintomas respiratórios — Pressão ou constrição no peito, sensação de sufocamento, suspiros, dispneia"),
    (11, "Sintomas gastrintestinais — Dificuldade para engolir, flatulência, dor abdominal, sensação de ardor, plenitude abdominal, náusea, vômito, intestino preso, perda de peso, constipação"),
    (12, "Sintomas genitourinários — Frequência urinária, urgência, amenorreia, menorragia, libido reduzida, ejaculação precoce, perda de ereção"),
    (13, "Sintomas do sistema nervoso autônomo — Boca seca, vermelhidão, palidez, tendência à sudorese, tontura, cefaleia tensional, calafrios"),
    (14, "Comportamento na entrevista — Inquietação, agitação ou andar de um lado para outro, tremor das mãos, cenho franzido, face tensa, suspiros ou respiração rápida, palidez facial, engolir saliva, etc."),
]
HAMA_CORTE = [
    ("Normal",               0,  7),
    ("Ansiedade leve",       8, 14),
    ("Ansiedade moderada",  15, 23),
    ("Ansiedade grave",     24, 30),
    ("Ansiedade muito grave",31, 56),
]