import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import (
    Paciente, Avaliacao, AvaliacaoVineland, AvaliacaoEscolar, AvaliacaoBebe,
    AvaliacaoSPM, AvaliacaoEDM, AvaliacaoMABC2, AvaliacaoBeery, AvaliacaoPEDI,
)
from ..services import build_lista_com_link


@login_required
def index(request):
    from django.db.models import Count, Q, Avg
    from django.utils import timezone as tz
    pacientes = (
        Paciente.objects.filter(medico=request.user)
        .annotate(
            total_avals=(
                Count("avaliacoes", distinct=True)
                + Count("avaliacoes_vineland", distinct=True)
                + Count("avaliacoes_escolar", distinct=True)
                + Count("avaliacoes_bebe", distinct=True)
                + Count("avaliacoes_spm", distinct=True)
                + Count("avaliacoes_edm", distinct=True)
                + Count("avaliacoes_mabc2", distinct=True)
                + Count("avaliacoes_beery", distinct=True)
                + Count("avaliacoes_pedi", distinct=True)
            )
        )
        .order_by("nome")
    )
    total_pacientes = pacientes.count()
    total_sens = Avaliacao.objects.filter(paciente__medico=request.user).count()
    total_vinel = AvaliacaoVineland.objects.filter(paciente__medico=request.user).count()
    total_escolar = AvaliacaoEscolar.objects.filter(paciente__medico=request.user).count()
    total_bebe = AvaliacaoBebe.objects.filter(paciente__medico=request.user).count()
    total_spm = AvaliacaoSPM.objects.filter(paciente__medico=request.user).count()
    total_edm = AvaliacaoEDM.objects.filter(paciente__medico=request.user).count()
    total_mabc2 = AvaliacaoMABC2.objects.filter(paciente__medico=request.user).count()
    total_beery = AvaliacaoBeery.objects.filter(paciente__medico=request.user).count()
    total_pedi = AvaliacaoPEDI.objects.filter(paciente__medico=request.user).count()
    total_avaliacoes = total_sens + total_vinel + total_escolar + total_bebe + total_spm + total_edm + total_mabc2 + total_beery + total_pedi

    concluidas_sens = Avaliacao.objects.filter(paciente__medico=request.user, status="concluida").count()
    concluidas_vinel = AvaliacaoVineland.objects.filter(paciente__medico=request.user, status="concluida").count()
    concluidas_escolar = AvaliacaoEscolar.objects.filter(paciente__medico=request.user, status="concluida").count()
    concluidas_bebe = AvaliacaoBebe.objects.filter(paciente__medico=request.user, status="concluida").count()
    concluidas_spm = AvaliacaoSPM.objects.filter(paciente__medico=request.user, status="concluida").count()
    concluidas = (concluidas_sens + concluidas_vinel + concluidas_escolar + concluidas_bebe + concluidas_spm
                  + total_edm + total_mabc2 + total_beery + total_pedi)
    em_andamento = total_avaliacoes - concluidas

    hoje = tz.now().date()
    inicio_mes = hoje.replace(day=1)
    novas_mes = (
        Avaliacao.objects.filter(paciente__medico=request.user, criado_em__date__gte=inicio_mes).count()
        + AvaliacaoVineland.objects.filter(paciente__medico=request.user, criado_em__date__gte=inicio_mes).count()
        + AvaliacaoEscolar.objects.filter(paciente__medico=request.user, criado_em__date__gte=inicio_mes).count()
        + AvaliacaoBebe.objects.filter(paciente__medico=request.user, criado_em__date__gte=inicio_mes).count()
        + AvaliacaoSPM.objects.filter(paciente__medico=request.user, criado_em__date__gte=inicio_mes).count()
        + AvaliacaoEDM.objects.filter(paciente__medico=request.user, criado_em__date__gte=inicio_mes).count()
        + AvaliacaoMABC2.objects.filter(paciente__medico=request.user, criado_em__date__gte=inicio_mes).count()
        + AvaliacaoBeery.objects.filter(paciente__medico=request.user, criado_em__date__gte=inicio_mes).count()
        + AvaliacaoPEDI.objects.filter(paciente__medico=request.user, criado_em__date__gte=inicio_mes).count()
    )

    ultimas_avaliacoes = list(
        Avaliacao.objects.filter(paciente__medico=request.user, status="concluida")
        .select_related("paciente").order_by("-data")[:5]
    )

    return render(request, "questionario/index.html", {
        "pacientes": pacientes,
        "total_pacientes": total_pacientes,
        "total_avaliacoes": total_avaliacoes,
        "concluidas": concluidas,
        "em_andamento": em_andamento,
        "novas_mes": novas_mes,
        "total_sens": total_sens,
        "total_vinel": total_vinel,
        "ultimas_avaliacoes": ultimas_avaliacoes,
    })


@login_required
def lista_pacientes(request):
    from django.core.paginator import Paginator
    from django.db.models import Count, Q
    q = request.GET.get("q", "").strip()
    qs = (
        Paciente.objects.filter(medico=request.user)
        .annotate(
            sens_total=Count("avaliacoes", distinct=True),
            vinel_total=Count("avaliacoes_vineland", distinct=True),
            escolar_total=Count("avaliacoes_escolar", distinct=True),
            bebe_total=Count("avaliacoes_bebe", distinct=True),
            spm_total=Count("avaliacoes_spm", distinct=True),
            edm_total=Count("avaliacoes_edm", distinct=True),
            mabc2_total=Count("avaliacoes_mabc2", distinct=True),
            beery_total=Count("avaliacoes_beery", distinct=True),
            pedi_total=Count("avaliacoes_pedi", distinct=True),
            sens_conc=Count("avaliacoes", filter=Q(avaliacoes__status="concluida"), distinct=True),
            vinel_conc=Count("avaliacoes_vineland", filter=Q(avaliacoes_vineland__status="concluida"), distinct=True),
            escolar_conc=Count("avaliacoes_escolar", filter=Q(avaliacoes_escolar__status="concluida"), distinct=True),
            bebe_conc=Count("avaliacoes_bebe", filter=Q(avaliacoes_bebe__status="concluida"), distinct=True),
            spm_conc=Count("avaliacoes_spm", filter=Q(avaliacoes_spm__status="concluida"), distinct=True),
        )
        .order_by("nome")
    )
    if q:
        qs = qs.filter(nome__icontains=q)
    paginator = Paginator(qs, 10)
    page = paginator.get_page(request.GET.get("page"))
    for p in page.object_list:
        p.total_avals = (p.sens_total + p.vinel_total + p.escolar_total + p.bebe_total
                         + p.spm_total + p.edm_total + p.mabc2_total + p.beery_total + p.pedi_total)
        p.total_concs = (p.sens_conc + p.vinel_conc + p.escolar_conc + p.bebe_conc + p.spm_conc
                         + p.edm_total + p.mabc2_total + p.beery_total + p.pedi_total)
    return render(request, "questionario/lista_pacientes.html", {"pacientes": page, "q": q, "paginator": paginator})


@login_required
def novo_paciente(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        data_nascimento = request.POST.get("data_nascimento", "")
        responsavel = request.POST.get("responsavel", "").strip()
        email = request.POST.get("email_responsavel", "").strip()
        telefone = request.POST.get("telefone", "").strip()

        if not nome or not data_nascimento or not responsavel:
            messages.error(request, "Preencha os campos obrigatórios.")
            return render(request, "questionario/novo_paciente.html", {"post": request.POST})

        paciente = Paciente.objects.create(
            medico=request.user,
            nome=nome, data_nascimento=data_nascimento,
            responsavel=responsavel, email_responsavel=email, telefone=telefone,
        )
        messages.success(request, "Paciente cadastrado com sucesso.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)

    return render(request, "questionario/novo_paciente.html")


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
            return render(request, "questionario/editar_paciente.html", {"paciente": paciente, "post": request.POST})
        paciente.nome = nome
        paciente.data_nascimento = data_nascimento
        paciente.responsavel = responsavel
        paciente.email_responsavel = email
        paciente.telefone = telefone
        paciente.save()
        messages.success(request, "Dados do paciente atualizados com sucesso.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    return render(request, "questionario/editar_paciente.html", {"paciente": paciente})


@login_required
def detalhe_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
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
    return render(request, "questionario/detalhe_paciente.html", {
        "paciente": paciente,
        "avaliacoes": avaliacoes,
        "avaliacoes_vineland": avaliacoes_vineland,
        "avaliacoes_escolar": build_lista_com_link(paciente.avaliacoes_escolar.all(), request, "escolar_publico"),
        "avaliacoes_bebe": build_lista_com_link(paciente.avaliacoes_bebe.all(), request, "bebe_publico"),
        "avaliacoes_spm": build_lista_com_link(paciente.avaliacoes_spm.all(), request, "spm_publico"),
        "avaliacoes_edm": paciente.avaliacoes_edm.all(),
        "avaliacoes_mabc2": paciente.avaliacoes_mabc2.all(),
        "avaliacoes_beery": paciente.avaliacoes_beery.all(),
        "avaliacoes_pedi": paciente.avaliacoes_pedi.all(),
    })


@login_required
def deletar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    if request.method == "POST":
        paciente.delete()
        messages.success(request, "Paciente excluído com sucesso.")
        return redirect("lista_pacientes")
    return redirect("detalhe_paciente", paciente_id=paciente_id)


@login_required
def nova_avaliacao(request, paciente_id):
    from django.http import JsonResponse
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    avaliacao = Avaliacao.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "id": avaliacao.id})
    return redirect("questionario", avaliacao_id=avaliacao.id, pagina=1)


@login_required
def deletar_avaliacao(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação excluída com sucesso."})
        messages.success(request, "Avaliação excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)
