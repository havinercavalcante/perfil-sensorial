import uuid
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.template.loader import render_to_string

logger = logging.getLogger("auditoria")

from ..models import (
    Paciente, Avaliacao, AvaliacaoVineland, AvaliacaoEscolar,
    AvaliacaoBebe, AvaliacaoSPM, AvaliacaoVineland3, AvaliacaoPEDI, AvaliacaoPortage, LinkConvite,
    AvaliacaoSDQ, AvaliacaoSNAPIV, AvaliacaoMCHAT,
    AvaliacaoLinguagem, AvaliacaoAlimentacao,
    AvaliacaoHabitosOrais, AvaliacaoVozInfantil, AvaliacaoProcessamentoAuditivo, AvaliacaoIDV10,
    AvaliacaoDesenvolvimento, AvaliacaoSono,
    AvaliacaoHabilidadesAdaptativas, AvaliacaoComportamentoFuncional,
    AvaliacaoRastreioCognitivo, AvaliacaoPsicopedagogica,
)
from ..services import TIPO_INFO


@login_required
def gerar_link(request):
    from django.http import JsonResponse

    # Mapeamento tipo → codigo do módulo
    TIPO_PARA_MODULO = {
        "sensorial": "sensorial",
        "vineland": "vineland",
        "vineland3": "vineland3",
        "escolar": "escolar",
        "bebe": "bebe",
        "crianca_pequena": "bebe",
        "spm_p": "spm",
        "spm_casa": "spm",
        "edm": "edm",
        "mabc2": "mabc2",
        "beery": "beery",
        "pedi": "pedi",
        "portage": "portage",
        "sdq": "sdq",
        "snap_iv": "snap_iv",
        "mchat": "mchat",
        "cars": "cars",
        "linguagem": "linguagem",
        "alimentacao_seletiva": "alimentacao_seletiva",
        "habitos_orais": "habitos_orais",
        "voz_infantil": "voz_infantil",
        "processamento_auditivo": "processamento_auditivo",
        "idv10": "idv10",
        "desenvolvimento": "desenvolvimento",
        "sono_infantil": "sono_infantil",
        "habilidades_adaptativas": "habilidades_adaptativas",
        "comportamento_funcional": "comportamento_funcional",
        "rastreio_cognitivo": "rastreio_cognitivo",
        "psicopedagogica": "psicopedagogica",
    }

    modulos_liberados = set()
    if hasattr(request.user, 'perfil'):
        modulos_liberados = set(
            request.user.perfil.modulos_liberados.values_list("codigo", flat=True)
        )

    if request.method == "POST":
        tipo = request.POST.get("tipo", "")
        tipos_validos = [t[0] for t in LinkConvite.TIPO_CHOICES]
        if tipo not in tipos_validos:
            return JsonResponse({"ok": False, "message": "Tipo inválido."})
        modulo_necessario = TIPO_PARA_MODULO.get(tipo)
        if modulo_necessario and modulo_necessario not in modulos_liberados:
            return JsonResponse({"ok": False, "message": "Módulo não disponível no seu plano."})
        convite = LinkConvite.objects.create(medico=request.user, tipo=tipo)
        link = request.build_absolute_uri(f"/iniciar/{convite.token}/")
        nome_medico = request.user.get_full_name() or request.user.username
        return JsonResponse({
            "ok": True,
            "link": link,
            "tipo_display": convite.get_tipo_display(),
            "nome_medico": nome_medico,
        })

    return render(request, "questionario/dashboard/gerar_link.html", {
        "modulos_liberados": modulos_liberados,
    })


@login_required
def enviar_email_convite(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "message": "Método não permitido."}, status=405)

    email_dest = request.POST.get("email", "").strip()
    link = request.POST.get("link", "").strip()
    tipo_display = request.POST.get("tipo_display", "Avaliação").strip()

    if not email_dest or not link:
        return JsonResponse({"ok": False, "message": "E-mail e link são obrigatórios."})

    try:
        validate_email(email_dest)
    except ValidationError:
        return JsonResponse({"ok": False, "message": "E-mail inválido."})

    nome_medico = request.user.get_full_name() or request.user.username
    html = render_to_string("questionario/emails/email_convite.html", {
        "link": link,
        "tipo_display": tipo_display,
        "nome_medico": nome_medico,
    })
    send_mail(
        subject=f"IntegraMente — {tipo_display}",
        message=f"Acesse o link para responder o questionário:\n\n{link}",
        from_email=None,
        recipient_list=[email_dest],
        html_message=html,
        fail_silently=False,
    )
    return JsonResponse({"ok": True, "message": f"E-mail enviado para {email_dest}."})


def iniciar_avaliacao(request, token):
    from django.utils import timezone as tz
    convite = get_object_or_404(LinkConvite, token=token)

    if convite.usado_em:
        return render(request, "questionario/dashboard/iniciar_avaliacao.html", {
            "convite": convite,
            "ja_utilizado": True,
        })

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        data_nascimento = request.POST.get("data_nascimento", "")
        responsavel = request.POST.get("responsavel", "").strip()
        email = request.POST.get("email_responsavel", "").strip()
        telefone = request.POST.get("telefone", "").strip()
        consentimento = request.POST.get("consentimento", "")

        if not nome or not data_nascimento or not responsavel:
            return render(request, "questionario/dashboard/iniciar_avaliacao.html", {
                "convite": convite,
                "post": request.POST,
                "erro": "Preencha os campos obrigatórios (nome, data de nascimento e responsável).",
            })

        if not consentimento:
            return render(request, "questionario/dashboard/iniciar_avaliacao.html", {
                "convite": convite,
                "post": request.POST,
                "erro": "Você deve aceitar a Política de Privacidade para continuar.",
            })

        paciente = Paciente.objects.create(
            medico=convite.medico,
            nome=nome,
            data_nascimento=data_nascimento,
            responsavel=responsavel,
            email_responsavel=email,
            telefone=telefone,
        )
        logger.info(
            "CONSENTIMENTO_OBTIDO paciente_uuid=%s responsavel=%s ip=%s tipo=%s",
            paciente.uuid, responsavel,
            request.META.get("REMOTE_ADDR", "desconhecido"),
            convite.tipo,
        )
        convite.usado_em = tz.now()
        convite.save()

        t = str(uuid.uuid4())
        tipo = convite.tipo

        if tipo == "sensorial":
            Avaliacao.objects.create(paciente=paciente, token=t)
            return redirect("questionario_publico", token=t, pagina=1)
        elif tipo == "vineland":
            AvaliacaoVineland.objects.create(paciente=paciente, token=t)
            return redirect("vineland_publico", token=t, pagina=1)
        elif tipo == "escolar":
            AvaliacaoEscolar.objects.create(paciente=paciente, token=t)
            return redirect("escolar_publico", token=t, pagina=1)
        elif tipo == "bebe":
            AvaliacaoBebe.objects.create(paciente=paciente, token=t, faixa="bebe")
            return redirect("bebe_publico", token=t, pagina=1)
        elif tipo == "crianca_pequena":
            AvaliacaoBebe.objects.create(paciente=paciente, token=t, faixa="crianca_pequena")
            return redirect("bebe_publico", token=t, pagina=1)
        elif tipo in ("spm_p", "spm_casa"):
            AvaliacaoSPM.objects.create(paciente=paciente, token=t, faixa=tipo)
            return redirect("spm_publico", token=t, pagina=1)
        elif tipo == "vineland3":
            AvaliacaoVineland3.objects.create(paciente=paciente, token=t)
            return redirect("vineland3_publico", token=t, pagina=1)
        elif tipo == "pedi":
            AvaliacaoPEDI.objects.create(paciente=paciente, token=t)
            return redirect("pedi_publico", token=t, pagina=1)
        elif tipo == "portage":
            AvaliacaoPortage.objects.create(paciente=paciente, token=t)
            return redirect("portage_publico", token=t, pagina=1)
        elif tipo == "sdq":
            AvaliacaoSDQ.objects.create(paciente=paciente, token=t, respondente="pais")
            return redirect("sdq_publico", token=t, pagina=1)
        elif tipo == "snap_iv":
            AvaliacaoSNAPIV.objects.create(paciente=paciente, token=t, respondente="pais")
            return redirect("snap_iv_publico", token=t, pagina=1)
        elif tipo == "mchat":
            AvaliacaoMCHAT.objects.create(paciente=paciente, token=t)
            return redirect("mchat_publico", token=t)
        elif tipo == "linguagem":
            AvaliacaoLinguagem.objects.create(paciente=paciente, token=t)
            return redirect("linguagem_publico", token=t, pagina=1)
        elif tipo == "alimentacao_seletiva":
            AvaliacaoAlimentacao.objects.create(paciente=paciente, token=t)
            return redirect("alimentacao_publico", token=t, pagina=1)
        elif tipo == "habitos_orais":
            AvaliacaoHabitosOrais.objects.create(paciente=paciente, token=t)
            return redirect("habitos_publico", token=t, pagina=1)
        elif tipo == "voz_infantil":
            AvaliacaoVozInfantil.objects.create(paciente=paciente, token=t)
            return redirect("voz_publico", token=t, pagina=1)
        elif tipo == "processamento_auditivo":
            AvaliacaoProcessamentoAuditivo.objects.create(paciente=paciente, token=t)
            return redirect("auditivo_publico", token=t, pagina=1)
        elif tipo == "idv10":
            AvaliacaoIDV10.objects.create(paciente=paciente, token=t)
            return redirect("idv_publico", token=t, pagina=1)
        elif tipo == "desenvolvimento":
            AvaliacaoDesenvolvimento.objects.create(paciente=paciente, token=t)
            return redirect("desenvolvimento_publico", token=t, pagina=1)
        elif tipo == "sono_infantil":
            AvaliacaoSono.objects.create(paciente=paciente, token=t)
            return redirect("sono_publico", token=t, pagina=1)
        elif tipo == "habilidades_adaptativas":
            AvaliacaoHabilidadesAdaptativas.objects.create(paciente=paciente, token=t)
            return redirect("habilidades_publico", token=t, pagina=1)
        elif tipo == "comportamento_funcional":
            AvaliacaoComportamentoFuncional.objects.create(paciente=paciente, token=t)
            return redirect("comportamento_publico", token=t, pagina=1)
        elif tipo == "rastreio_cognitivo":
            AvaliacaoRastreioCognitivo.objects.create(paciente=paciente, token=t)
            return redirect("cognitivo_publico", token=t, pagina=1)
        elif tipo == "psicopedagogica":
            AvaliacaoPsicopedagogica.objects.create(paciente=paciente, token=t)
            return redirect("psicopedagogica_publico", token=t, pagina=1)
        else:
            # CARS-2, EDM, MABC-2, Beery — presencial, só cadastra o paciente
            return render(request, "questionario/dashboard/iniciar_avaliacao.html", {
                "convite": convite,
                "cadastrado": True,
            })

    label, icon = TIPO_INFO.get(convite.tipo, (convite.get_tipo_display(), ""))
    return render(request, "questionario/dashboard/iniciar_avaliacao.html", {
        "convite": convite,
        "tipo_label": label,
        "tipo_icon": icon,
    })
