from .auth import *
from .seo import *
from .pacientes import *
from .sensorial import *
from .vineland import *
from .escolar import *
from .bebe import *
from .edm import *
from .mabc2 import *
from .beery import *
from .pedi import *
from .spm import *
from .convite import *
from .vineland3 import *
from .portage import *
from .sdq import *
from .snap_iv import *
from .mchat import *
from .cars import *
from .linguagem import *
from .alimentacao import *
from .habitos_orais import *
from .voz_infantil import *
from .processamento_auditivo import *
from .idv10 import *
from .desenvolvimento import *
from .sono import *
from .habilidades_adaptativas import *
from .comportamento_funcional import *
from .cognitivo import *
from .psicopedagogica import *
# ── Módulos de Psicologia ──────────────────────────────────────────────────
from .k10 import *
from .ucla import *
from .msi_bpd import *
from .gds15 import *
from .rosenberg import *
from .audit import *
from .bis11 import *
from .iar import *
from .pas import *
from .cdi import *
from .hama import *
from .lsas import *
from .risco_suicidio import *
from .agorafobia import *
from .panico import *
from .phq9 import *
from .gad7 import *
from .epds import *
from .pcl5 import *
from .ghq12 import *
from .bdi import *
from .bai import *
from .dass21 import *
from .had import *
from .bsl23 import *
from .aq10_adulto import *
from .aq10_child import *
from .dep_emocional import *
from .scq import *
# ── Lote 2 Psicologia ─────────────────────────────────────────────────────
from .conners import (
    nova_avaliacao_conners_pais, conners_pais_form, conners_pais_resultado,
    conners_pais_visualizar, conners_pais_deletar, salvar_observacoes_conners_pais,
    enviar_email_conners_pais, conners_pais_publico,
    nova_avaliacao_conners_prof, conners_prof_form, conners_prof_resultado,
    conners_prof_visualizar, conners_prof_deletar, salvar_observacoes_conners_prof,
    enviar_email_conners_prof, conners_prof_publico,
)
from .etdah import (
    nova_avaliacao_etdah_pais, etdah_pais_form, etdah_pais_resultado,
    etdah_pais_visualizar, etdah_pais_deletar, salvar_observacoes_etdah_pais,
    enviar_email_etdah_pais, etdah_pais_publico,
    nova_avaliacao_etdah_prof, etdah_prof_form, etdah_prof_resultado,
    etdah_prof_visualizar, etdah_prof_deletar, salvar_observacoes_etdah_prof,
    enviar_email_etdah_prof, etdah_prof_publico,
)
from .auqei import (
    nova_avaliacao_auqei, auqei_form, auqei_resultado, auqei_visualizar,
    auqei_deletar, salvar_observacoes_auqei, enviar_email_auqei, auqei_publico,
)
from .scared import (
    nova_avaliacao_scared, scared_form, scared_resultado, scared_visualizar,
    scared_deletar, salvar_observacoes_scared, enviar_email_scared, scared_publico,
)
from .masc import (
    nova_avaliacao_masc, masc_form, masc_resultado, masc_visualizar,
    masc_deletar, salvar_observacoes_masc, enviar_email_masc, masc_publico,
)
from .bpq import (
    nova_avaliacao_bpq, bpq_form, bpq_resultado, bpq_visualizar,
    bpq_deletar, salvar_observacoes_bpq, enviar_email_bpq, bpq_publico,
)
# ── Lote 3: Denver, QMPI, Dislexia ────────────────────────────────────────────
from .denver import (
    nova_avaliacao_denver, denver_form, denver_resultado,
    denver_visualizar, denver_deletar, salvar_observacoes_denver,
    denver_publico, enviar_email_denver,
)
from .qmpi import (
    nova_avaliacao_qmpi, qmpi_form, qmpi_resultado, qmpi_visualizar,
    qmpi_deletar, salvar_observacoes_qmpi, enviar_email_qmpi, qmpi_publico,
)
from .quest_dislexia import (
    nova_avaliacao_quest_dislexia, quest_dislexia_form, quest_dislexia_resultado,
    quest_dislexia_visualizar, quest_dislexia_deletar, salvar_observacoes_quest_dislexia,
    enviar_email_quest_dislexia, quest_dislexia_publico,
)
from .checklist_dislexia import (
    nova_avaliacao_checklist_dislexia, checklist_dislexia_form, checklist_dislexia_resultado,
    checklist_dislexia_visualizar, checklist_dislexia_deletar, salvar_observacoes_checklist_dislexia,
    enviar_email_checklist_dislexia, checklist_dislexia_publico,
)
from .prot_dislexia_prof import (
    nova_avaliacao_prot_dislexia_prof, prot_dislexia_prof_form, prot_dislexia_prof_resultado,
    prot_dislexia_prof_visualizar, prot_dislexia_prof_deletar, salvar_observacoes_prot_dislexia_prof,
    enviar_email_prot_dislexia_prof, prot_dislexia_prof_publico,
)
from .inventario_dislexia import (
    nova_avaliacao_inventario_dislexia, inventario_dislexia_form,
    inventario_dislexia_resultado, inventario_dislexia_deletar,
)
# ── Nutrição / Terapia Alimentar ───────────────────────────────────────────
from .terapia_alimentar import *
# ──────────────────────────────────────────────────────────────────────────
from .laudos import laudo_generico
from .pagamentos import solicitar_plano, painel_pagamentos, aprovar_solicitacao, rejeitar_solicitacao
