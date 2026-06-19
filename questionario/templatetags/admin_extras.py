from django import template
from django.conf import settings as django_settings
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from questionario.models import (
    Paciente, Avaliacao, AvaliacaoVineland, AvaliacaoEscolar, AvaliacaoBebe,
    AvaliacaoEDM, AvaliacaoMABC2, AvaliacaoBeery, AvaliacaoPEDI, AvaliacaoSPM,
    AvaliacaoVineland3, AvaliacaoPortage, LinkConvite, PerfilMedico,
    SolicitacaoPlano, PageVisit,
)

_VALOR_PLANO = {
    "start": Decimal("39.90"),
    "plus":  Decimal("79.90"),
    "elite": Decimal("149.90"),
}

register = template.Library()

_EVAL_NOMES = {
    'avaliacoes':                        'Perfil Sensorial',
    'avaliacoes_vineland':               'Vineland',
    'avaliacoes_escolar':                'Esc. Sensorial',
    'avaliacoes_bebe':                   'Bebê/Criança Peq.',
    'avaliacoes_edm':                    'EDM',
    'avaliacoes_mabc2':                  'MABC-2',
    'avaliacoes_beery':                  'Beery VMI',
    'avaliacoes_pedi':                   'PEDI',
    'avaliacoes_spm':                    'SPM',
    'avaliacoes_vineland3':              'Vineland-3',
    'avaliacoes_portage':                'Guia Portage',
    'avaliacoes_sdq':                    'SDQ',
    'avaliacoes_snap_iv':                'SNAP-IV',
    'avaliacoes_mchat':                  'M-CHAT-R',
    'avaliacoes_cars':                   'CARS-2',
    'avaliacoes_linguagem':              'Linguagem',
    'avaliacoes_alimentacao':            'Alimentação Selet.',
    'avaliacoes_habitos_orais':          'Hábitos Orais',
    'avaliacoes_voz_infantil':           'Voz Infantil',
    'avaliacoes_processamento_auditivo': 'Proc. Auditivo',
    'avaliacoes_idv10':                  'IDV-10',
    'avaliacoes_desenvolvimento':        'Marcos Desenv.',
    'avaliacoes_sono':                   'Sono Infantil',
    'avaliacoes_habilidades_adaptativas':'Hab. Adaptativas',
    'avaliacoes_comportamento_funcional':'Comp. Funcional',
    'avaliacoes_cognitivo':              'Rastreio Cognitivo',
    'avaliacoes_psicopedagogica':        'Psicopedagógica',
    'avaliacoes_bdi':                    'BDI',
    'avaliacoes_bai':                    'BAI',
    'avaliacoes_dass21':                 'DASS-21',
    'avaliacoes_had':                    'HAD',
    'avaliacoes_bsl23':                  'BSL-23',
    'avaliacoes_aq10_adulto':            'AQ-10 Adulto',
    'avaliacoes_aq10_child':             'AQ-10 Criança',
    'avaliacoes_dep_emocional':          'Dep. Emocional',
    'avaliacoes_scq':                    'SCQ',
    'avaliacoes_conners':                'Conners',
    'avaliacoes_etdah':                  'ETDAH',
    'avaliacoes_auqei':                  'AUQEI',
    'avaliacoes_scared':                 'SCARED',
    'avaliacoes_masc':                   'MASC',
    'avaliacoes_bpq':                    'BPQ',
    'avaliacoes_denver':                 'Denver',
    'avaliacoes_qmpi':                   'QMPI',
    'avaliacoes_quest_dislexia':         'Quest. Dislexia',
    'avaliacoes_checklist_dislexia':     'Check. Dislexia',
    'avaliacoes_prot_dislexia_prof':     'Prot. Dislexia',
    'avaliacoes_inventario_dislexia':    'Inv. Dislexia',
    'avaliacoes_phq9':                   'PHQ-9',
    'avaliacoes_gad7':                   'GAD-7',
    'avaliacoes_epds':                   'EPDS',
    'avaliacoes_pcl5':                   'PCL-5',
    'avaliacoes_ghq12':                  'GHQ-12',
    'avaliacoes_k10':                    'K-10',
    'avaliacoes_ucla':                   'UCLA',
    'avaliacoes_msi_bpd':               'MSI-BPD',
    'avaliacoes_gds15':                  'GDS-15',
    'avaliacoes_rosenberg':              'Rosenberg',
    'avaliacoes_audit':                  'AUDIT',
    'avaliacoes_bis11':                  'BIS-11',
    'avaliacoes_iar':                    'IAR',
    'avaliacoes_pas':                    'PAS',
    'avaliacoes_cdi':                    'CDI',
    'avaliacoes_hama':                   'HAM-A',
    'avaliacoes_lsas':                   'LSAS',
    'avaliacoes_risco_suicidio':         'Risco Suicídio',
    'avaliacoes_agorafobia':             'Agorafobia',
    'avaliacoes_panico':                 'Pânico',
    'avaliacoes_recordatorio':           'Recordatório',
    'avaliacoes_anamnese':               'Anamnese',
}


def _tipos_avaliacoes_por_paciente(pacientes):
    """Retorna dict {paciente_id: [lista de nomes de avaliação]}."""
    pac_ids = [p.id for p in pacientes]
    resultado = {pid: [] for pid in pac_ids}
    if not pac_ids:
        return resultado

    for field in Paciente._meta.get_fields():
        if not (field.is_relation and field.one_to_many):
            continue
        rn = field.get_accessor_name()
        nome = _EVAL_NOMES.get(rn)
        if nome is None:
            continue
        pids = (
            field.related_model.objects
            .filter(paciente_id__in=pac_ids)
            .values_list('paciente_id', flat=True)
            .distinct()
        )
        for pid in pids:
            resultado[pid].append(nome)

    return resultado


@register.simple_tag
def logo_url():
    return f"{django_settings.SITE_URL}{django_settings.STATIC_URL}logonav.png"


@register.simple_tag
def dashboard_stats():
    trinta_dias = timezone.now() - timedelta(days=30)
    sete_dias = timezone.now() - timedelta(days=7)

    modulos_contagem = [
        {'nome': 'Perfil Sensorial', 'total': Avaliacao.objects.count(),
         'concluidas': Avaliacao.objects.filter(status='concluida').count()},
        {'nome': 'Vineland', 'total': AvaliacaoVineland.objects.count(),
         'concluidas': AvaliacaoVineland.objects.filter(status='concluida').count()},
        {'nome': 'Escolar', 'total': AvaliacaoEscolar.objects.count(),
         'concluidas': AvaliacaoEscolar.objects.filter(status='concluida').count()},
        {'nome': 'Bebê/Criança', 'total': AvaliacaoBebe.objects.count(),
         'concluidas': AvaliacaoBebe.objects.filter(status='concluida').count()},
        {'nome': 'EDM', 'total': AvaliacaoEDM.objects.count(), 'concluidas': AvaliacaoEDM.objects.count()},
        {'nome': 'MABC-2', 'total': AvaliacaoMABC2.objects.count(), 'concluidas': AvaliacaoMABC2.objects.count()},
        {'nome': 'Beery VMI', 'total': AvaliacaoBeery.objects.count(), 'concluidas': AvaliacaoBeery.objects.count()},
        {'nome': 'PEDI', 'total': AvaliacaoPEDI.objects.count(), 'concluidas': AvaliacaoPEDI.objects.count()},
        {'nome': 'SPM', 'total': AvaliacaoSPM.objects.count(),
         'concluidas': AvaliacaoSPM.objects.filter(status='concluida').count()},
        {'nome': 'Vineland-3', 'total': AvaliacaoVineland3.objects.count(),
         'concluidas': AvaliacaoVineland3.objects.filter(status='concluida').count()},
        {'nome': 'Portage', 'total': AvaliacaoPortage.objects.count(),
         'concluidas': AvaliacaoPortage.objects.filter(status='concluida').count()},
    ]
    modulos_contagem.sort(key=lambda x: x['total'], reverse=True)

    total_avaliacoes = sum(m['total'] for m in modulos_contagem)
    total_concluidas = sum(m['concluidas'] for m in modulos_contagem)
    total_links = LinkConvite.objects.count()

    # Pacientes cadastrados por dia nos últimos 30 dias
    pacientes_por_dia = list(
        Paciente.objects
        .filter(criado_em__gte=trinta_dias)
        .extra(select={'dia': "date(criado_em)"})
        .values('dia')
        .annotate(total=Count('id'))
        .order_by('dia')
    )

    pacientes_recentes = list(
        Paciente.objects.select_related('medico').order_by('-criado_em')[:10]
    )
    tipos_por_pac = _tipos_avaliacoes_por_paciente(pacientes_recentes)
    for p in pacientes_recentes:
        p.tipos_avaliacoes = tipos_por_pac[p.id]

    # ── Solicitações de plano ────────────────────────────────────────────────
    sol_pendentes = list(
        SolicitacaoPlano.objects.filter(status='pendente')
        .select_related('user').order_by('-criado_em')[:6]
    )
    sol_total_pendentes = SolicitacaoPlano.objects.filter(status='pendente').count()
    sol_total_aprovadas = SolicitacaoPlano.objects.filter(status='aprovado').count()

    # ── Financeiro (MRR) ─────────────────────────────────────────────────────
    agora = timezone.now()
    ativos = list(
        PerfilMedico.objects.filter(
            plano__in=('start', 'plus', 'elite'),
            user__is_active=True,
            plano_expiracao__gt=agora,
        )
    )
    mrr = sum(_VALOR_PLANO.get(p.plano, Decimal('0')) for p in ativos)
    fin_breakdown = {
        'start': sum(1 for p in ativos if p.plano == 'start'),
        'plus':  sum(1 for p in ativos if p.plano == 'plus'),
        'elite': sum(1 for p in ativos if p.plano == 'elite'),
    }
    def _brl(v):
        s = f"{float(v):,.2f}"
        return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")
    mrr_fmt = _brl(mrr)
    total_ativos = len(ativos)

    # ── Visitas de páginas ───────────────────────────────────────────────────
    hoje = timezone.localdate()
    visitas = {
        row['pagina']: row['total']
        for row in PageVisit.objects.filter(
            visitado_em__date=hoje
        ).values('pagina').annotate(total=Count('id'))
    }
    visitas_total = sum(visitas.values())

    return {
        'total_medicos': PerfilMedico.objects.count(),
        'total_pacientes': Paciente.objects.count(),
        'total_avaliacoes': total_avaliacoes,
        'total_concluidas': total_concluidas,
        'total_links': total_links,
        'links_usados': LinkConvite.objects.filter(usado_em__isnull=False).count(),
        'novos_pacientes_30d': Paciente.objects.filter(criado_em__gte=trinta_dias).count(),
        'pacientes_7d': Paciente.objects.filter(criado_em__gte=sete_dias).count(),
        'modulos_contagem': modulos_contagem,
        'pacientes_recentes': pacientes_recentes,
        'medicos': list(
            PerfilMedico.objects
            .annotate(n_pacientes=Count('user__pacientes'))
            .select_related('user')
            .prefetch_related('modulos_liberados')
            .order_by('-n_pacientes')
        ),
        'pacientes_por_dia': pacientes_por_dia,
        # solicitações
        'sol_pendentes':       sol_pendentes,
        'sol_total_pendentes': sol_total_pendentes,
        'sol_total_aprovadas': sol_total_aprovadas,
        # financeiro
        'mrr':            mrr_fmt,
        'fin_total_ativos': total_ativos,
        'fin_breakdown':  fin_breakdown,
        # visitas
        'visitas':        visitas,
        'visitas_total':  visitas_total,
    }
