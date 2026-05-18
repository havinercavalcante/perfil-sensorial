from django import template
from django.conf import settings as django_settings
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from questionario.models import (
    Paciente, Avaliacao, AvaliacaoVineland, AvaliacaoEscolar, AvaliacaoBebe,
    AvaliacaoEDM, AvaliacaoMABC2, AvaliacaoBeery, AvaliacaoPEDI, AvaliacaoSPM,
    AvaliacaoVineland3, AvaliacaoPortage, LinkConvite, PerfilMedico,
)

register = template.Library()


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
        'pacientes_recentes': list(
            Paciente.objects.select_related('medico').order_by('-criado_em')[:10]
        ),
        'medicos': list(
            PerfilMedico.objects
            .annotate(n_pacientes=Count('user__pacientes'))
            .select_related('user')
            .prefetch_related('modulos_liberados')
            .order_by('-n_pacientes')
        ),
        'pacientes_por_dia': pacientes_por_dia,
    }
