from django.conf import settings
import uuid
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

logger = logging.getLogger("auditoria")

from ..models import (
    Paciente, Avaliacao, AvaliacaoVineland, AvaliacaoEscolar, AvaliacaoBebe,
    AvaliacaoSPM, AvaliacaoEDM, AvaliacaoMABC2, AvaliacaoBeery, AvaliacaoPEDI,
    AvaliacaoPS2Bebe, AvaliacaoAdultoSensorial,
    AvaliacaoVineland3, AvaliacaoPortage,
    AvaliacaoSDQ, AvaliacaoSNAPIV, AvaliacaoMCHAT, AvaliacaoCARS,
    AvaliacaoLinguagem, AvaliacaoAlimentacao,
    AvaliacaoHabitosOrais, AvaliacaoVozInfantil, AvaliacaoProcessamentoAuditivo, AvaliacaoIDV10,
    AvaliacaoDesenvolvimento, AvaliacaoSono,
    AvaliacaoHabilidadesAdaptativas, AvaliacaoComportamentoFuncional,
    AvaliacaoRastreioCognitivo, AvaliacaoPsicopedagogica,
    # Módulos de psicologia
    AvaliacaoBDI, AvaliacaoBAI, AvaliacaoDASS21, AvaliacaoHAD, AvaliacaoBSL23,
    AvaliacaoAQ10Adulto, AvaliacaoAQ10Child, AvaliacaoDepEmocional, AvaliacaoSCQ,
    # Lote 2
    AvaliacaoConners, AvaliacaoETDAH, AvaliacaoAUQEI, AvaliacaoSCARED,
    AvaliacaoMASC, AvaliacaoBPQ,
    # Lote 3
    AvaliacaoDenver, AvaliacaoQMPI,
    AvaliacaoQuestDislexia, AvaliacaoChecklistDislexia,
    AvaliacaoProtDislexiaProf, AvaliacaoInventarioDislexia,
    # Triagem geral
    AvaliacaoPHQ9, AvaliacaoGAD7, AvaliacaoEPDS, AvaliacaoPCL5, AvaliacaoGHQ12,
    # Escalas adicionais
    AvaliacaoK10, AvaliacaoUCLA, AvaliacaoMSI_BPD, AvaliacaoGDS15, AvaliacaoRosenberg,
    AvaliacaoAUDIT, AvaliacaoBIS11, AvaliacaoIAR, AvaliacaoPAS, AvaliacaoCDI,
    AvaliacaoHAMA, AvaliacaoLSAS, AvaliacaoRiscoSuicidio, AvaliacaoAgorafobia, AvaliacaoPanico,
    # Escalas de Alimentação Infantil
    AvaliacaoEBAI, AvaliacaoSEPS, AvaliacaoECA, AvaliacaoTOD,
    # VB-MAPP
    AvaliacaoVBMAPP, AvaliacaoVBMAPPBarreiras, AvaliacaoVBMAPPTransicao, AvaliacaoVBMAPPTaskAnalysis,
)
from ..services import build_lista_com_link, build_lista_sem_pagina
from ..tasks import enviar_email
from django.urls import reverse


def _build_pedi_lista(queryset, request):
    result = []
    for av in queryset:
        if not av.token and av.fs_autocuidado is None:
            av.token = str(uuid.uuid4())
            av.save(update_fields=["token"])
        link_publico = None
        if av.token and av.fs_autocuidado is None:
            path = reverse("pedi_publico", kwargs={"token": av.token, "pagina": 1})
            link_publico = request.build_absolute_uri(path)
        result.append({"obj": av, "link_publico": link_publico})
    return result


def contato_view(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        mensagem = request.POST.get("mensagem", "").strip()
        if not nome or not email or not mensagem:
            return render(request, "questionario/landing.html", {"contato_erro": "Preencha todos os campos."})
        enviar_email.delay(
            subject=f"[IntegraMente] Contato de {nome}",
            message=f"Nome: {nome}\nE-mail: {email}\n\n{mensagem}",
            recipient_list=["integramente.pro@gmail.com"],
            fail_silently=True,
        )
        return render(request, "questionario/landing.html", {"contato_enviado": True})
    return redirect("index")


def index(request):
    if not request.user.is_authenticated:
        return render(request, "questionario/landing.html")

    from django.db.models import Count, Q
    from django.utils import timezone as tz

    pacientes = list(Paciente.objects.filter(medico=request.user).order_by("nome"))
    total_pacientes = len(pacientes)

    total_avaliacoes = 0
    concluidas = 0
    novas_mes = 0
    totals = {}

    if pacientes:
        patient_ids = [p.pk for p in pacientes]
        totals = {pid: 0 for pid in patient_ids}
        hoje = tz.now().date()
        inicio_mes = hoje.replace(day=1)

        for Model in _MODELS_WITH_STATUS:
            for row in (
                Model.objects.filter(paciente_id__in=patient_ids)
                .values("paciente_id")
                .annotate(
                    cnt=Count("pk"),
                    conc=Count("pk", filter=Q(status="concluida")),
                    novas=Count("pk", filter=Q(criado_em__date__gte=inicio_mes)),
                )
            ):
                pid = row["paciente_id"]
                totals[pid] += row["cnt"]
                total_avaliacoes += row["cnt"]
                concluidas += row["conc"]
                novas_mes += row["novas"]

        for Model in _MODELS_NO_STATUS:
            for row in (
                Model.objects.filter(paciente_id__in=patient_ids)
                .values("paciente_id")
                .annotate(
                    cnt=Count("pk"),
                    novas=Count("pk", filter=Q(criado_em__date__gte=inicio_mes)),
                )
            ):
                pid = row["paciente_id"]
                totals[pid] += row["cnt"]
                total_avaliacoes += row["cnt"]
                concluidas += row["cnt"]
                novas_mes += row["novas"]

        for p in pacientes:
            p.total_avals = totals.get(p.pk, 0)

    em_andamento = total_avaliacoes - concluidas

    ultimas_avaliacoes = list(
        Avaliacao.objects.filter(paciente__medico=request.user, status="concluida")
        .select_related("paciente").order_by("-data")[:5]
    )

    return render(request, "questionario/auth/index.html", {
        "pacientes": pacientes,
        "total_pacientes": total_pacientes,
        "total_avaliacoes": total_avaliacoes,
        "concluidas": concluidas,
        "em_andamento": em_andamento,
        "novas_mes": novas_mes,
        "ultimas_avaliacoes": ultimas_avaliacoes,
    })


_MODELS_WITH_STATUS = [
    Avaliacao, AvaliacaoVineland, AvaliacaoEscolar, AvaliacaoBebe, AvaliacaoSPM,
    AvaliacaoPS2Bebe, AvaliacaoAdultoSensorial,
    AvaliacaoVineland3, AvaliacaoPortage, AvaliacaoSDQ, AvaliacaoSNAPIV,
    AvaliacaoMCHAT, AvaliacaoCARS, AvaliacaoLinguagem, AvaliacaoAlimentacao,
    AvaliacaoHabitosOrais, AvaliacaoVozInfantil, AvaliacaoProcessamentoAuditivo,
    AvaliacaoIDV10, AvaliacaoDesenvolvimento, AvaliacaoSono,
    AvaliacaoHabilidadesAdaptativas, AvaliacaoComportamentoFuncional,
    AvaliacaoRastreioCognitivo, AvaliacaoPsicopedagogica,
    AvaliacaoBDI, AvaliacaoBAI, AvaliacaoDASS21, AvaliacaoHAD, AvaliacaoBSL23,
    AvaliacaoAQ10Adulto, AvaliacaoAQ10Child, AvaliacaoDepEmocional, AvaliacaoSCQ,
    AvaliacaoConners, AvaliacaoETDAH, AvaliacaoAUQEI, AvaliacaoSCARED,
    AvaliacaoMASC, AvaliacaoBPQ,
    AvaliacaoDenver, AvaliacaoQMPI, AvaliacaoQuestDislexia, AvaliacaoChecklistDislexia,
    AvaliacaoProtDislexiaProf, AvaliacaoInventarioDislexia,
    AvaliacaoPHQ9, AvaliacaoGAD7, AvaliacaoEPDS, AvaliacaoPCL5, AvaliacaoGHQ12,
    AvaliacaoK10, AvaliacaoUCLA, AvaliacaoMSI_BPD, AvaliacaoGDS15, AvaliacaoRosenberg,
    AvaliacaoAUDIT, AvaliacaoBIS11, AvaliacaoIAR, AvaliacaoPAS, AvaliacaoCDI,
    AvaliacaoHAMA, AvaliacaoLSAS, AvaliacaoRiscoSuicidio, AvaliacaoAgorafobia, AvaliacaoPanico,
]
_MODELS_NO_STATUS = [AvaliacaoEDM, AvaliacaoMABC2, AvaliacaoBeery, AvaliacaoPEDI]


def _compute_patient_totals(patient_ids):
    from django.db.models import Count, Q
    totals = {pid: 0 for pid in patient_ids}
    concluded = {pid: 0 for pid in patient_ids}
    for Model in _MODELS_WITH_STATUS:
        for row in (
            Model.objects.filter(paciente_id__in=patient_ids)
            .values("paciente_id")
            .annotate(cnt=Count("pk"), conc=Count("pk", filter=Q(status="concluida")))
        ):
            pid = row["paciente_id"]
            totals[pid] += row["cnt"]
            concluded[pid] += row["conc"]
    for Model in _MODELS_NO_STATUS:
        for row in (
            Model.objects.filter(paciente_id__in=patient_ids)
            .values("paciente_id")
            .annotate(cnt=Count("pk"))
        ):
            pid = row["paciente_id"]
            totals[pid] += row["cnt"]
            concluded[pid] += row["cnt"]
    return totals, concluded


@login_required
def lista_pacientes(request):
    import json
    from django.core.paginator import Paginator
    from django.db.models import Exists, OuterRef
    q = request.GET.get("q", "").strip()
    filtro = request.GET.get("filtro", "").strip()
    qs = Paciente.objects.filter(medico=request.user).order_by("nome")
    if q:
        qs = qs.filter(nome__icontains=q)
    if filtro == "andamento":
        qs = qs.filter(
            Exists(Avaliacao.objects.filter(paciente=OuterRef("pk"), status="em_andamento"))
            | Exists(AvaliacaoVineland.objects.filter(paciente=OuterRef("pk"), status="em_andamento"))
            | Exists(AvaliacaoEscolar.objects.filter(paciente=OuterRef("pk"), status="em_andamento"))
            | Exists(AvaliacaoBebe.objects.filter(paciente=OuterRef("pk"), status="em_andamento"))
            | Exists(AvaliacaoSPM.objects.filter(paciente=OuterRef("pk"), status="em_andamento"))
            | Exists(AvaliacaoVineland3.objects.filter(paciente=OuterRef("pk"), status="em_andamento"))
        )
    paginator = Paginator(qs, 10)
    page = paginator.get_page(request.GET.get("page"))
    patient_ids = [p.pk for p in page.object_list]
    if patient_ids:
        totals, concluded = _compute_patient_totals(patient_ids)
        for p in page.object_list:
            p.total_avals = totals.get(p.pk, 0)
            p.total_concs = concluded.get(p.pk, 0)
    todos_pacientes = Paciente.objects.filter(medico=request.user).order_by("nome").values("uuid", "nome")
    pacientes_json = json.dumps([{"uuid": str(p["uuid"]), "nome": p["nome"]} for p in todos_pacientes])
    modulos_liberados = set()
    if hasattr(request.user, 'perfil'):
        modulos_liberados = set(
            request.user.perfil.modulos_liberados.values_list("codigo", flat=True)
        )
    return render(request, "questionario/pacientes/lista_pacientes.html", {
        "pacientes": page, "q": q, "filtro": filtro, "paginator": paginator,
        "pacientes_json": pacientes_json, "modulos_liberados": modulos_liberados,
    })


# Modelos de avaliação com campo `status` (EDM, MABC2, Beery e PEDI não têm status).
# Compartilhado entre avaliacoes_pendentes e evolucao_paciente para listar/agrupar
# avaliações de qualquer instrumento sem duplicar a lista.
MODELOS_AVALIACAO = [
    (Avaliacao,                     "Perfil Sensorial",             "sensorial"),
    (AvaliacaoVineland,             "Escala Vineland",              "vineland"),
    (AvaliacaoEscolar,              "Sensorial Escolar",            "escolar"),
    (AvaliacaoBebe,                 "Bebê / Criança Pequena",       "bebe"),
    (AvaliacaoSPM,                  "SPM",                          "spm"),
    (AvaliacaoPS2Bebe,              "PS2 Bebê/CP (Winnie Dunn)",    "ps2_bebe"),
    (AvaliacaoAdultoSensorial,      "Perf. Sensorial Adulto",       "adulto_sensorial"),
    (AvaliacaoVineland3,            "Vineland-3",                   "vineland3"),
    (AvaliacaoPortage,              "Guia Portage",                 "portage"),
    (AvaliacaoSDQ,                  "SDQ",                          "sdq"),
    (AvaliacaoSNAPIV,               "SNAP-IV",                      "snap_iv"),
    (AvaliacaoMCHAT,                "M-CHAT-R",                     "mchat"),
    (AvaliacaoCARS,                 "CARS-2",                       "cars"),
    (AvaliacaoLinguagem,            "Linguagem",                    "linguagem"),
    (AvaliacaoAlimentacao,          "Alimentação Seletiva",         "alimentacao"),
    (AvaliacaoHabitosOrais,         "Hábitos Orais",                "habitos_orais"),
    (AvaliacaoVozInfantil,          "Voz Infantil",                 "voz_infantil"),
    (AvaliacaoProcessamentoAuditivo,"Proc. Auditivo",               "proc_auditivo"),
    (AvaliacaoIDV10,                "IDV-10",                       "idv10"),
    (AvaliacaoDesenvolvimento,      "Desenvolvimento",              "desenvolvimento"),
    (AvaliacaoSono,                 "Sono Infantil",                "sono"),
    (AvaliacaoHabilidadesAdaptativas,"Habilidades Adaptativas",     "habilidades"),
    (AvaliacaoComportamentoFuncional,"Comportamento Funcional",     "comportamento"),
    (AvaliacaoRastreioCognitivo,    "Rastreio Cognitivo",           "cognitivo"),
    (AvaliacaoPsicopedagogica,      "Psicopedagógica",              "psicopedagogica"),
    # Psicologia — Lote 1
    (AvaliacaoBDI,                  "BDI",                          "bdi"),
    (AvaliacaoBAI,                  "BAI",                          "bai"),
    (AvaliacaoDASS21,               "DASS-21",                      "dass21"),
    (AvaliacaoHAD,                  "HAD",                          "had"),
    (AvaliacaoBSL23,                "BSL-23",                       "bsl23"),
    (AvaliacaoAQ10Adulto,           "AQ-10 Adulto",                 "aq10_adulto"),
    (AvaliacaoAQ10Child,            "AQ-10 Criança",                "aq10_child"),
    (AvaliacaoDepEmocional,         "Dep. Emocional",               "dep_emocional"),
    (AvaliacaoSCQ,                  "SCQ",                          "scq"),
    # Psicologia — Lote 2
    (AvaliacaoConners,              "Conners-3",                    "conners"),
    (AvaliacaoETDAH,                "ETDAH",                        "etdah"),
    (AvaliacaoAUQEI,                "AUQEI",                        "auqei"),
    (AvaliacaoSCARED,               "SCARED",                       "scared"),
    (AvaliacaoMASC,                 "MASC",                         "masc"),
    (AvaliacaoBPQ,                  "BPQ",                          "bpq"),
    # Lote 3
    (AvaliacaoDenver,               "Denver II",                    "denver"),
    (AvaliacaoQMPI,                 "QMPI",                         "qmpi"),
    (AvaliacaoQuestDislexia,        "Quest. Dislexia",              "quest_dislexia"),
    (AvaliacaoChecklistDislexia,    "Checklist Dislexia",           "checklist_dislexia"),
    (AvaliacaoProtDislexiaProf,     "Prot. Dislexia Prof.",         "prot_dislexia_prof"),
    (AvaliacaoInventarioDislexia,   "Inventário Dislexia",          "inventario_dislexia"),
    (AvaliacaoVBMAPP,               "VB-MAPP — Marcos",             "vbmapp"),
    (AvaliacaoVBMAPPBarreiras,      "VB-MAPP — Barreiras",          "vbmapp_barreiras"),
    (AvaliacaoVBMAPPTransicao,      "VB-MAPP — Transição",          "vbmapp_transicao"),
    (AvaliacaoVBMAPPTaskAnalysis,   "VB-MAPP — Task Analysis",      "vbmapp_task_analysis"),
]


@login_required
def avaliacoes_pendentes(request):
    from django.core.paginator import Paginator

    q = request.GET.get("q", "").strip()
    tipo_filtro = request.GET.get("tipo", "").strip()

    pendentes = []
    for Model, label, slug in MODELOS_AVALIACAO:
        if tipo_filtro and tipo_filtro != slug:
            continue
        qs = (
            Model.objects.filter(paciente__medico=request.user, status="em_andamento")
            .select_related("paciente")
            .order_by("-criado_em")
        )
        if q:
            qs = qs.filter(paciente__nome__icontains=q)
        for av in qs:
            pendentes.append({
                "paciente_nome": av.paciente.nome,
                "paciente_uuid": av.paciente.uuid,
                "uuid": str(av.uuid),
                "tipo": label,
                "tipo_slug": slug,
                "criado_em": av.criado_em,
                "data": av.data,
                "tem_token": bool(getattr(av, "token", None)),
            })

    pendentes.sort(key=lambda x: x["criado_em"], reverse=True)
    total = len(pendentes)

    paginator = Paginator(pendentes, 10)
    page = paginator.get_page(request.GET.get("page"))

    tipos_disponiveis = [(slug, label) for _, label, slug in MODELOS_AVALIACAO]

    return render(request, "questionario/avaliacoes/pendentes.html", {
        "pendentes": page,
        "q": q,
        "tipo_filtro": tipo_filtro,
        "tipos_disponiveis": tipos_disponiveis,
        "total": total,
        "paginator": paginator,
    })


@login_required
def novo_paciente(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        data_nascimento = request.POST.get("data_nascimento", "")
        responsavel = request.POST.get("responsavel", "").strip()
        email = request.POST.get("email_responsavel", "").strip()
        telefone = request.POST.get("telefone", "").strip()
        tipo_paciente = request.POST.get("tipo_paciente", "crianca")

        if tipo_paciente == "adulto" and not responsavel:
            responsavel = nome

        if not nome or not data_nascimento or (tipo_paciente != "adulto" and not responsavel):
            messages.error(request, "Preencha os campos obrigatórios.")
            return render(request, "questionario/pacientes/novo_paciente.html", {"post": request.POST})

        paciente = Paciente.objects.create(
            medico=request.user,
            nome=nome, data_nascimento=data_nascimento,
            responsavel=responsavel, email_responsavel=email, telefone=telefone,
        )
        logger.info("PACIENTE_CRIADO user=%s paciente_uuid=%s", request.user.username, paciente.uuid)
        messages.success(request, "Paciente cadastrado com sucesso.")
        destino = reverse("detalhe_paciente", kwargs={"paciente_id": paciente.uuid})
        abrir_tipo = request.GET.get("abrir_tipo")
        if abrir_tipo:
            destino += "?abrir_tipo=" + abrir_tipo
        elif request.GET.get("nova_avaliacao") == "1":
            destino += "?nova_avaliacao=1"
        return redirect(destino)

    return render(request, "questionario/pacientes/novo_paciente.html")


@login_required
def editar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        data_nascimento = request.POST.get("data_nascimento", "")
        responsavel = request.POST.get("responsavel", "").strip()
        email = request.POST.get("email_responsavel", "").strip()
        telefone = request.POST.get("telefone", "").strip()
        if not nome or not data_nascimento or not responsavel:
            messages.error(request, "Preencha os campos obrigatórios.")
            return render(request, "questionario/pacientes/editar_paciente.html", {"paciente": paciente, "post": request.POST})
        paciente.nome = nome
        paciente.data_nascimento = data_nascimento
        paciente.responsavel = responsavel
        paciente.email_responsavel = email
        paciente.telefone = telefone
        paciente.save()
        messages.success(request, "Dados do paciente atualizados com sucesso.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    return render(request, "questionario/pacientes/editar_paciente.html", {"paciente": paciente})


@login_required
def detalhe_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)

    # Módulos liberados para este médico
    modulos_liberados = set()
    if hasattr(request.user, 'perfil'):
        modulos_liberados = set(
            request.user.perfil.modulos_liberados.values_list("codigo", flat=True)
        )

    avaliacoes = []
    for av in paciente.avaliacoes.all():
        if not av.token and av.status != "concluida":
            av.token = str(uuid.uuid4())
            av.save(update_fields=["token"])
        link_publico = None
        if av.token and av.status != "concluida":
            link_publico = request.build_absolute_uri(f"/questionario/publico/{av.token}/{av.pagina_atual}/")
        avaliacoes.append({"obj": av, "link_publico": link_publico})
    avaliacoes_vineland = []
    for av in paciente.avaliacoes_vineland.all():
        link_publico = None
        if av.token and av.status != "concluida":
            link_publico = request.build_absolute_uri(f"/vineland/publico/{av.token}/1/")
        avaliacoes_vineland.append({"obj": av, "link_publico": link_publico})
    return render(request, "questionario/pacientes/detalhe_paciente.html", {
        "paciente": paciente,
        "modulos_liberados": modulos_liberados,
        "avaliacoes": avaliacoes,
        "avaliacoes_vineland": avaliacoes_vineland,
        "avaliacoes_escolar": build_lista_com_link(paciente.avaliacoes_escolar.all(), request, "escolar_publico"),
        "avaliacoes_bebe": build_lista_com_link(paciente.avaliacoes_bebe.all(), request, "bebe_publico"),
        "avaliacoes_spm": build_lista_com_link(paciente.avaliacoes_spm.all(), request, "spm_publico"),
        "avaliacoes_edm": paciente.avaliacoes_edm.all(),
        "avaliacoes_mabc2": paciente.avaliacoes_mabc2.all(),
        "avaliacoes_beery": paciente.avaliacoes_beery.all(),
        "avaliacoes_pedi": _build_pedi_lista(paciente.avaliacoes_pedi.all(), request),
        "avaliacoes_vineland3": build_lista_com_link(paciente.avaliacoes_vineland3.all(), request, "vineland3_publico"),
        "avaliacoes_portage": build_lista_com_link(paciente.avaliacoes_portage.all(), request, "portage_publico"),
        "avaliacoes_sdq": build_lista_com_link(paciente.avaliacoes_sdq.all(), request, "sdq_publico"),
        "avaliacoes_snap_iv": build_lista_com_link(paciente.avaliacoes_snap_iv.all(), request, "snap_iv_publico"),
        "avaliacoes_mchat": build_lista_sem_pagina(paciente.avaliacoes_mchat.all(), request, "mchat_publico"),
        "avaliacoes_cars": build_lista_sem_pagina(paciente.avaliacoes_cars.all(), request, "cars_publico"),
        "avaliacoes_linguagem": build_lista_com_link(paciente.avaliacoes_linguagem.all(), request, "linguagem_publico"),
        "avaliacoes_alimentacao": build_lista_com_link(paciente.avaliacoes_alimentacao.all(), request, "alimentacao_publico"),
        "avaliacoes_habitos_orais": build_lista_com_link(paciente.avaliacoes_habitos_orais.all(), request, "habitos_publico"),
        "avaliacoes_voz_infantil": build_lista_com_link(paciente.avaliacoes_voz_infantil.all(), request, "voz_publico"),
        "avaliacoes_processamento_auditivo": build_lista_com_link(paciente.avaliacoes_processamento_auditivo.all(), request, "auditivo_publico"),
        "avaliacoes_idv10": build_lista_com_link(paciente.avaliacoes_idv10.all(), request, "idv_publico"),
        "avaliacoes_desenvolvimento": build_lista_com_link(paciente.avaliacoes_desenvolvimento.all(), request, "desenvolvimento_publico"),
        "avaliacoes_sono": build_lista_com_link(paciente.avaliacoes_sono.all(), request, "sono_publico"),
        "avaliacoes_habilidades": build_lista_com_link(paciente.avaliacoes_habilidades_adaptativas.all(), request, "habilidades_publico"),
        "avaliacoes_comportamento": build_lista_com_link(paciente.avaliacoes_comportamento_funcional.all(), request, "comportamento_publico"),
        "avaliacoes_cognitivo": build_lista_com_link(paciente.avaliacoes_cognitivo.all(), request, "cognitivo_publico"),
        "avaliacoes_psicopedagogica": build_lista_com_link(paciente.avaliacoes_psicopedagogica.all(), request, "psicopedagogica_publico"),
        "avaliacoes_proade": [{"obj": av} for av in paciente.avaliacoes_proade.all()],
        # Novas escalas
        "avaliacoes_k10": build_lista_com_link(paciente.avaliacoes_k10.all(), request, "k10_publico"),
        "avaliacoes_ucla": build_lista_com_link(paciente.avaliacoes_ucla.all(), request, "ucla_publico"),
        "avaliacoes_msi_bpd": build_lista_com_link(paciente.avaliacoes_msi_bpd.all(), request, "msi_bpd_publico"),
        "avaliacoes_gds15": build_lista_com_link(paciente.avaliacoes_gds15.all(), request, "gds15_publico"),
        "avaliacoes_rosenberg": build_lista_com_link(paciente.avaliacoes_rosenberg.all(), request, "rosenberg_publico"),
        "avaliacoes_audit": build_lista_com_link(paciente.avaliacoes_audit.all(), request, "audit_publico"),
        "avaliacoes_bis11": build_lista_com_link(paciente.avaliacoes_bis11.all(), request, "bis11_publico"),
        "avaliacoes_iar": build_lista_com_link(paciente.avaliacoes_iar.all(), request, "iar_publico"),
        "avaliacoes_pas": build_lista_com_link(paciente.avaliacoes_pas.all(), request, "pas_publico"),
        "avaliacoes_cdi": build_lista_com_link(paciente.avaliacoes_cdi.all(), request, "cdi_publico"),
        "avaliacoes_hama": build_lista_com_link(paciente.avaliacoes_hama.all(), request, "hama_publico"),
        "avaliacoes_lsas": build_lista_com_link(paciente.avaliacoes_lsas.all(), request, "lsas_publico"),
        "avaliacoes_risco_suicidio": build_lista_com_link(paciente.avaliacoes_risco_suicidio.all(), request, "risco_suicidio_publico"),
        "avaliacoes_agorafobia": build_lista_com_link(paciente.avaliacoes_agorafobia.all(), request, "agorafobia_publico"),
        "avaliacoes_panico": build_lista_com_link(paciente.avaliacoes_panico.all(), request, "panico_publico"),
        # Triagem geral
        "avaliacoes_phq9":  build_lista_com_link(paciente.avaliacoes_phq9.all(),  request, "phq9_publico"),
        "avaliacoes_gad7":  build_lista_com_link(paciente.avaliacoes_gad7.all(),  request, "gad7_publico"),
        "avaliacoes_epds":  build_lista_com_link(paciente.avaliacoes_epds.all(),  request, "epds_publico"),
        "avaliacoes_pcl5":  build_lista_com_link(paciente.avaliacoes_pcl5.all(),  request, "pcl5_publico"),
        "avaliacoes_ghq12": build_lista_com_link(paciente.avaliacoes_ghq12.all(), request, "ghq12_publico"),
        # Módulos de psicologia
        "avaliacoes_bdi": build_lista_com_link(paciente.avaliacoes_bdi.all(), request, "bdi_publico"),
        "avaliacoes_bai": build_lista_com_link(paciente.avaliacoes_bai.all(), request, "bai_publico"),
        "avaliacoes_dass21": build_lista_com_link(paciente.avaliacoes_dass21.all(), request, "dass21_publico"),
        "avaliacoes_had": build_lista_com_link(paciente.avaliacoes_had.all(), request, "had_publico"),
        "avaliacoes_bsl23": build_lista_com_link(paciente.avaliacoes_bsl23.all(), request, "bsl23_publico"),
        "avaliacoes_aq10_adulto": build_lista_com_link(paciente.avaliacoes_aq10_adulto.all(), request, "aq10_adulto_publico"),
        "avaliacoes_aq10_child": build_lista_com_link(paciente.avaliacoes_aq10_child.all(), request, "aq10_child_publico"),
        "avaliacoes_dep_emocional": build_lista_com_link(paciente.avaliacoes_dep_emocional.all(), request, "dep_emocional_publico"),
        "avaliacoes_scq": build_lista_com_link(paciente.avaliacoes_scq.all(), request, "scq_publico"),
        # Lote 2
        "avaliacoes_conners_pais": build_lista_com_link(paciente.avaliacoes_conners.filter(respondente="pais").all(), request, "conners_pais_publico"),
        "avaliacoes_conners_prof": build_lista_com_link(paciente.avaliacoes_conners.filter(respondente="professor").all(), request, "conners_prof_publico"),
        "avaliacoes_etdah_pais": build_lista_com_link(paciente.avaliacoes_etdah.filter(respondente="pais").all(), request, "etdah_pais_publico"),
        "avaliacoes_etdah_prof": build_lista_com_link(paciente.avaliacoes_etdah.filter(respondente="professor").all(), request, "etdah_prof_publico"),
        "avaliacoes_auqei": build_lista_com_link(paciente.avaliacoes_auqei.all(), request, "auqei_publico"),
        "avaliacoes_scared": build_lista_com_link(paciente.avaliacoes_scared.all(), request, "scared_publico"),
        "avaliacoes_masc": build_lista_com_link(paciente.avaliacoes_masc.all(), request, "masc_publico"),
        "avaliacoes_bpq": build_lista_com_link(paciente.avaliacoes_bpq.all(), request, "bpq_publico"),
        # Lote 3: Denver, QMPI, Dislexia
        "avaliacoes_denver": build_lista_com_link(paciente.avaliacoes_denver.all(), request, "denver_publico"),
        "avaliacoes_qmpi": build_lista_com_link(paciente.avaliacoes_qmpi.all(), request, "qmpi_publico"),
        "avaliacoes_quest_dislexia": build_lista_com_link(paciente.avaliacoes_quest_dislexia.all(), request, "quest_dislexia_publico"),
        "avaliacoes_checklist_dislexia": build_lista_com_link(paciente.avaliacoes_checklist_dislexia.all(), request, "checklist_dislexia_publico"),
        "avaliacoes_prot_dislexia_prof": build_lista_com_link(paciente.avaliacoes_prot_dislexia_prof.all(), request, "prot_dislexia_prof_publico"),
        "avaliacoes_inventario_dislexia": paciente.avaliacoes_inventario_dislexia.all(),
        # Escalas de Alimentação Infantil
        "avaliacoes_ebai": build_lista_com_link(paciente.avaliacoes_ebai.all(), request, "ebai_publico"),
        "avaliacoes_seps": build_lista_com_link(paciente.avaliacoes_seps.all(), request, "seps_publico"),
        "avaliacoes_eca":  build_lista_com_link(paciente.avaliacoes_eca.all(),  request, "eca_publico"),
        "avaliacoes_tod":  build_lista_com_link(paciente.avaliacoes_tod.all(),  request, "tod_publico"),
        # PS2 Bebê/CP e Adulto Sensorial
        "avaliacoes_ps2_bebe": build_lista_com_link(paciente.avaliacoes_ps2_bebe.all().order_by("-data"), request, "ps2_bebe_wd_publico"),
        "avaliacoes_adulto_sensorial": build_lista_com_link(paciente.avaliacoes_adulto_sensorial.all().order_by("-data"), request, "adulto_sensorial_publico"),
        # Documentos do prontuário (anamnese, evoluções, fichas escolares, atestados, etc.)
        # — um grupo por tipo de documento, só os tipos com pelo menos um registro.
        "procedimentos_por_tipo": _procedimentos_por_tipo(paciente),
        "avaliacoes_vbmapp": paciente.avaliacoes_vbmapp.all(),
        "avaliacoes_vbmapp_barreiras": paciente.avaliacoes_vbmapp_barreiras.all(),
        "avaliacoes_vbmapp_transicao": paciente.avaliacoes_vbmapp_transicao.all(),
        "avaliacoes_vbmapp_task_analysis": paciente.avaliacoes_vbmapp_task_analysis.all(),
    })


def _procedimentos_por_tipo(paciente):
    from procedimentos.models import ProcedimentoDocumento
    grupos = []
    for tipo, label in ProcedimentoDocumento.TIPO_CHOICES:
        docs = paciente.procedimentos.filter(tipo=tipo)
        if docs.exists():
            grupos.append({"tipo": tipo, "label": label, "documentos": docs})
    return grupos


# Exceções ao padrão "<slug>_resultado" usado pela maioria dos instrumentos
# (nome da URL de resultado não corresponde diretamente ao slug do instrumento).
RESULTADO_URL_OVERRIDES = {
    "sensorial": "dashboard",
    "habitos_orais": "habitos_resultado",
    "voz_infantil": "voz_resultado",
    "proc_auditivo": "auditivo_resultado",
    "idv10": "idv_resultado",
}


def _resultado_url(slug, av):
    """Resolve a URL do resultado de uma avaliação concluída a partir do slug do instrumento."""
    if slug in ("conners", "etdah"):
        sufixo = "prof" if getattr(av, "respondente", "") == "professor" else "pais"
        nome_url = f"{slug}_{sufixo}_resultado"
    else:
        nome_url = RESULTADO_URL_OVERRIDES.get(slug, f"{slug}_resultado")
    try:
        return reverse(nome_url, kwargs={"avaliacao_id": av.uuid})
    except Exception:
        return None


# Tipos de ProcedimentoDocumento que compõem o prontuário longitudinal (fora dos
# instrumentos avaliativos já cobertos por MODELOS_AVALIACAO): anamnese — ponto de
# entrada do cadastro —, evoluções de atendimento e fichas de visita escolar.
REGISTROS_PRONTUARIO = [
    ("anamnese",          "Anamnese",               "anamnese"),
    ("anamnese_adulto",   "Anamnese (Adulto)",      "anamnese"),
    ("anamnese_infantil", "Anamnese (Infantil)",    "anamnese"),
    ("anamnese_tea",      "Anamnese (TEA)",         "anamnese"),
    ("anamnese_tdah",     "Anamnese (TDAH)",        "anamnese"),
    ("anamnese_casal",    "Anamnese (Casal)",       "anamnese"),
    ("evolucao_semanal",     "Evolução de Atendimento", "evolucao"),
    ("ficha_visita_escolar", "Ficha de Visita Escolar", "ficha_escolar"),
]


@login_required
def evolucao_paciente(request, paciente_id):
    import json
    from ..data.data import QUADRANTES_CONFIG, SECOES_CONFIG
    from procedimentos.models import ProcedimentoDocumento

    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)

    # Linha do tempo: todas as avaliações concluídas, anamneses, evoluções de
    # atendimento e fichas de visita escolar do paciente, em ordem cronológica
    # decrescente — link direto para o registro de cada uma.
    eventos = []
    for Model, label, slug in MODELOS_AVALIACAO:
        for av in Model.objects.filter(paciente=paciente, status="concluida").order_by("-data"):
            eventos.append({
                "tipo": label, "tipo_slug": slug, "categoria": "avaliacao", "data": av.data,
                "uuid": av.uuid, "link": _resultado_url(slug, av),
            })
    for tipo, label, categoria in REGISTROS_PRONTUARIO:
        for doc in ProcedimentoDocumento.objects.filter(paciente=paciente, tipo=tipo).order_by("-data"):
            eventos.append({
                "tipo": doc.titulo_display if doc.titulo else label,
                "tipo_slug": tipo, "categoria": categoria, "data": doc.data,
                "uuid": doc.uuid,
                "link": reverse("abrir_procedimento", kwargs={
                    "paciente_id": paciente.uuid, "tipo": tipo, "doc_id": doc.uuid,
                }),
            })
    eventos.sort(key=lambda x: x["data"], reverse=True)

    # Evolução do Perfil Sensorial: único instrumento com pontuação estruturada por
    # quadrante (EX/EV/SN/OB) e seção, reaproveitando a lógica do gráfico comparativo
    # já existente no dashboard de uma avaliação isolada — aqui consolidado por paciente.
    sensoriais = list(paciente.avaliacoes.filter(status="concluida").order_by("data"))
    cores = ["#2E7D6B", "#3E73D1", "#E8793A", "#9B59B6", "#E8B84B", "#C0392B", "#16A085", "#1ABC9C", "#7DB87D"]
    evolucao_labels = json.dumps([av.data.strftime("%d/%m/%Y") for av in sensoriais])

    def _datasets(config_map, paleta):
        datasets = []
        for i, (chave, config) in enumerate(config_map.items()):
            campo = f"pont_{chave.lower()}"
            cor = config.get("cor", paleta[i % len(paleta)])
            valores = [
                round(getattr(av, campo) / config["max"] * 100) if getattr(av, campo) is not None else 0
                for av in sensoriais
            ]
            datasets.append({"label": config["nome"], "data": valores, "borderColor": cor,
                             "backgroundColor": cor + "33", "tension": 0.3})
        return datasets

    return render(request, "questionario/pacientes/evolucao.html", {
        "paciente": paciente,
        "eventos": eventos,
        "tem_evolucao_sensorial": len(sensoriais) > 1,
        "evolucao_labels": evolucao_labels,
        "quad_datasets": json.dumps(_datasets(QUADRANTES_CONFIG, cores)),
        "secao_datasets": json.dumps(_datasets(SECOES_CONFIG, cores)),
    })


@login_required
def prontuario_resumo(request, paciente_id):
    """Reúne, numa única página de impressão, os registros do prontuário
    selecionados na timeline (avaliações, anamnese, evoluções, fichas escolares)."""
    from django.utils import timezone as tz
    from procedimentos.models import ProcedimentoDocumento

    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)

    modelos_por_slug = {slug: Model for Model, _, slug in MODELOS_AVALIACAO}
    labels_avaliacao = {slug: label for _, label, slug in MODELOS_AVALIACAO}
    labels_procedimento = {tipo: label for tipo, label, _ in REGISTROS_PRONTUARIO}

    registros = []
    for token in request.GET.get("registros", "").split(","):
        partes = token.split(":", 2)
        if len(partes) != 3:
            continue
        categoria, slug, reg_uuid = partes

        if categoria == "avaliacao":
            Model = modelos_por_slug.get(slug)
            if not Model:
                continue
            av = Model.objects.filter(uuid=reg_uuid, paciente=paciente).first()
            if not av:
                continue
            campos = []
            for f in av._meta.get_fields():
                nome = getattr(f, "name", "")
                if nome.startswith(("pont_", "escore", "score", "media_")) or nome == "classificacao":
                    valor = getattr(av, nome, None)
                    if valor not in (None, ""):
                        campos.append((getattr(f, "verbose_name", nome), valor))
            registros.append({
                "titulo": labels_avaliacao.get(slug, slug), "data": av.data, "categoria": "avaliacao",
                "campos": campos, "observacoes": getattr(av, "observacoes", ""),
            })
        else:
            doc = ProcedimentoDocumento.objects.filter(uuid=reg_uuid, paciente=paciente, tipo=slug).first()
            if not doc:
                continue
            registros.append({
                "titulo": doc.titulo_display or labels_procedimento.get(slug, slug),
                "data": doc.data, "categoria": categoria,
                "conteudo_html": "".join(v for v in doc.conteudo.values() if isinstance(v, str)),
            })

    registros.sort(key=lambda r: r["data"], reverse=True)

    return render(request, "questionario/pacientes/prontuario_resumo.html", {
        "paciente": paciente,
        "registros": registros,
        "data_hoje": tz.now().date(),
    })


@login_required
def enviar_email_modulo(request, modulo, avaliacao_id):
    from django.http import JsonResponse
    from django.utils import timezone as tz

    MODULO_MAP = {
        'linguagem':               (AvaliacaoLinguagem,                 'linguagem_publico',   'Avaliação de Linguagem'),
        'alimentacao':             (AvaliacaoAlimentacao,               'alimentacao_publico', 'Triagem de Alimentação Seletiva'),
        'habitos_orais':           (AvaliacaoHabitosOrais,              'habitos_publico',     'Hábitos Orais Deletérios'),
        'voz_infantil':            (AvaliacaoVozInfantil,               'voz_publico',         'Triagem de Voz Infantil'),
        'processamento_auditivo':  (AvaliacaoProcessamentoAuditivo,     'auditivo_publico',    'Triagem de Processamento Auditivo'),
        'idv10':                   (AvaliacaoIDV10,                     'idv_publico',         'IDV-10 — Desvantagem Vocal'),
        'desenvolvimento': (AvaliacaoDesenvolvimento,        'desenvolvimento_publico', 'Marcos de Desenvolvimento'),
        'sono':            (AvaliacaoSono,                   'sono_publico',            'Avaliação de Sono Infantil'),
        'habilidades':     (AvaliacaoHabilidadesAdaptativas, 'habilidades_publico',     'Habilidades Adaptativas'),
        'comportamento':   (AvaliacaoComportamentoFuncional, 'comportamento_publico',   'Comportamento Funcional'),
        'cognitivo':       (AvaliacaoRastreioCognitivo,      'cognitivo_publico',       'Rastreio Cognitivo'),
        'psicopedagogica': (AvaliacaoPsicopedagogica,        'psicopedagogica_publico', 'Avaliação Psicopedagógica'),
        'portage':         (AvaliacaoPortage,                'portage_publico',         'Guia Portage'),
    }
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if modulo not in MODULO_MAP:
        return JsonResponse({"ok": False, "message": "Módulo inválido."}, status=400)

    Model, url_name, label = MODULO_MAP[modulo]
    avaliacao = get_object_or_404(Model, uuid=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    email_dest = paciente.email_responsavel

    if not email_dest:
        if is_ajax:
            return JsonResponse({"ok": False, "message": "Nenhum e-mail cadastrado para o responsável."})
        messages.error(request, "Nenhum e-mail cadastrado para o responsável.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)

    from django.template.loader import render_to_string
    from django.templatetags.static import static
    link = request.build_absolute_uri(reverse(url_name, kwargs={"token": avaliacao.token}))
    html = render_to_string("questionario/emails/email_link_avaliacao.html", {"paciente": paciente, "link": link})
    try:
        enviar_email.delay(
            subject=f"{label} — IntegraMente",
            message=f"Olá, {paciente.responsavel}!\n\nResponda o questionário no link: {link}",
            recipient_list=[email_dest],
            html_message=html,
            fail_silently=False,
        )
    except Exception as exc:
        if is_ajax:
            return JsonResponse({"ok": False, "message": f"Falha ao enviar e-mail: {exc}"})
        messages.error(request, f"Falha ao enviar e-mail: {exc}")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    avaliacao.email_enviado_em = tz.now()
    avaliacao.save(update_fields=["email_enviado_em"])
    if is_ajax:
        return JsonResponse({"ok": True, "message": f"E-mail enviado para {email_dest}."})
    messages.success(request, f"E-mail enviado para {email_dest}.")
    return redirect("detalhe_paciente", paciente_id=paciente.uuid)


@login_required
def deletar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if request.method == "POST":
        logger.info("PACIENTE_EXCLUIDO user=%s paciente_uuid=%s", request.user.username, paciente_id)
        paciente.delete()
        messages.success(request, "Paciente excluído com sucesso.")
        return redirect("lista_pacientes")
    return redirect("detalhe_paciente", paciente_id=paciente_id)


@login_required
def nova_avaliacao(request, paciente_id):
    from django.http import JsonResponse
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if not hasattr(request.user, 'perfil') or not request.user.perfil.tem_acesso('sensorial'):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "Módulo não disponível no seu plano."}, status=403)
        messages.error(request, "Você não tem acesso ao módulo Perfil Sensorial.")
        return redirect('detalhe_paciente', paciente_id=paciente_id)
    avaliacao = Avaliacao.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "uuid": str(avaliacao.uuid)})
    return redirect("questionario", avaliacao_id=avaliacao.uuid, pagina=1)


@login_required
def deletar_avaliacao(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(Avaliacao, uuid=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação excluída com sucesso."})
        messages.success(request, "Avaliação excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)
