from django.db import migrations

NOVOS_MODULOS = [
    # ── Psicologia — Triagem Infantil (Pais/Responsáveis) ────────────────────
    ("conners_pais",         "Conners-3 — Avaliação TDAH (Pais)",          "Conners 3rd Edition — Parent Form"),
    ("etdah_pais",           "ETDAH — Avaliação TDAH (Pais)",              "Escala de Transtorno de Déficit de Atenção/Hiperatividade"),
    ("auqei",                "AUQEI — Qualidade de Vida Infantil",         "Autoquestionnaire Qualité de Vie Enfant Imagé"),
    ("aq10_child",           "AQ-10 Criança — Rastreio de Autismo",        "Autism Quotient — 10 itens (criança)"),
    ("scared",               "SCARED — Ansiedade Infantil (Pais)",         "Screen for Child Anxiety Related Emotional Disorders"),
    ("masc",                 "MASC — Ansiedade Multidimensional",          "Multidimensional Anxiety Scale for Children"),
    ("scq",                  "SCQ — Comunicação Social",                   "Social Communication Questionnaire"),
    ("anamnese_tea_inf",     "Anamnese TEA Infantil",                      "Anamnese clínica para TEA — versão infantil"),
    ("anamnese_tdah_inf",    "Anamnese TDAH Infantil",                     "Anamnese clínica para TDAH — versão infantil"),
    # ── Psicologia — Triagem por Professor ───────────────────────────────────
    ("conners_prof",         "Conners-3 — Avaliação TDAH (Professor)",     "Conners 3rd Edition — Teacher Form"),
    ("etdah_prof",           "ETDAH — Avaliação TDAH (Professor)",         "ETDAH — versão professor"),
    # ── Psicologia — Instrumentos para Adultos ───────────────────────────────
    ("bdi",                  "BDI — Inventário de Depressão de Beck",      "Beck Depression Inventory"),
    ("bai",                  "BAI — Inventário de Ansiedade de Beck",      "Beck Anxiety Inventory"),
    ("dass21",               "DASS-21 — Depressão, Ansiedade e Estresse",  "Depression Anxiety Stress Scales — 21 itens"),
    ("had",                  "HAD — Ansiedade e Depressão Hospitalar",     "Hospital Anxiety and Depression Scale"),
    ("bsl23",                "BSL-23 — Sintomas Borderline",               "Borderline Symptom List — 23 itens"),
    ("aq10_adulto",          "AQ-10 Adulto — Rastreio de Autismo",         "Autism Quotient — 10 itens (adulto)"),
    ("dep_emocional",        "Questionário de Dependência Emocional",      "Questionário de Dependência Emocional"),
    ("bpq",                  "BPQ — Personalidade Borderline",             "Borderline Personality Questionnaire"),
    ("anamnese_adulto",      "Anamnese Adulto",                            "Anamnese clínica — versão adulto"),
    ("anamnese_tdah_adulto", "Anamnese TDAH Adulto",                       "Anamnese clínica para TDAH — adulto"),
    # ── Pediatria / Neuropediatria ────────────────────────────────────────────
    ("denver",               "Checklist Denver II — Desenvolvimento",      "Denver Developmental Screening Test II"),
    # ── Neuropsicologia ───────────────────────────────────────────────────────
    ("qmpi",                 "QMPI — Memória Prospectiva Infantil",        "Questionnaire for Prospective Memory"),
    # ── Psicopedagogia ────────────────────────────────────────────────────────
    ("quest_dislexia",       "Questionário de Dislexia (Pais)",            "Questionário de rastreio de dislexia — pais"),
    ("checklist_dislexia",   "Checklist de Dislexia",                      "Checklist clínico de sinais de dislexia"),
    ("prot_dislexia_prof",   "Protocolo Dislexia — Avaliação Escolar",     "Protocolo de avaliação de dislexia — professor"),
    ("inventario_dislexia",  "Inventário de Sinais Disléxicos",            "Inventário de sinais e sintomas disléxicos"),
]


def popular(apps, schema_editor):
    ModuloAvaliacao = apps.get_model("questionario", "ModuloAvaliacao")
    for codigo, nome, descricao in NOVOS_MODULOS:
        ModuloAvaliacao.objects.get_or_create(
            codigo=codigo,
            defaults={"nome": nome, "descricao": descricao},
        )


def reverter(apps, schema_editor):
    ModuloAvaliacao = apps.get_model("questionario", "ModuloAvaliacao")
    ModuloAvaliacao.objects.filter(codigo__in=[m[0] for m in NOVOS_MODULOS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("questionario", "0035_add_novos_modulos_avaliacao"),
    ]

    operations = [
        migrations.RunPython(popular, reverter),
    ]
