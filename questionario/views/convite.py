import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.template.loader import render_to_string

from ..models import (
    Paciente, Avaliacao, AvaliacaoVineland, AvaliacaoEscolar,
    AvaliacaoBebe, AvaliacaoSPM, LinkConvite,
)
from ..services import TIPO_INFO


@login_required
def gerar_link(request):
    from django.http import JsonResponse
    if request.method == "POST":
        tipo = request.POST.get("tipo", "")
        tipos_validos = [t[0] for t in LinkConvite.TIPO_CHOICES]
        if tipo not in tipos_validos:
            return JsonResponse({"ok": False, "message": "Tipo inválido."})
        convite = LinkConvite.objects.create(medico=request.user, tipo=tipo)
        link = request.build_absolute_uri(f"/iniciar/{convite.token}/")
        nome_medico = request.user.get_full_name() or request.user.username
        return JsonResponse({
            "ok": True,
            "link": link,
            "tipo_display": convite.get_tipo_display(),
            "nome_medico": nome_medico,
        })

    return render(request, "questionario/gerar_link.html")


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
    html = render_to_string("questionario/email_convite.html", {
        "link": link,
        "tipo_display": tipo_display,
        "nome_medico": nome_medico,
    })
    send_mail(
        subject=f"CeciSys — {tipo_display}",
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
        return render(request, "questionario/iniciar_avaliacao.html", {
            "convite": convite,
            "ja_utilizado": True,
        })

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        data_nascimento = request.POST.get("data_nascimento", "")
        responsavel = request.POST.get("responsavel", "").strip()
        email = request.POST.get("email_responsavel", "").strip()
        telefone = request.POST.get("telefone", "").strip()

        if not nome or not data_nascimento or not responsavel:
            return render(request, "questionario/iniciar_avaliacao.html", {
                "convite": convite,
                "post": request.POST,
                "erro": "Preencha os campos obrigatórios (nome, data de nascimento e responsável).",
            })

        paciente = Paciente.objects.create(
            medico=convite.medico,
            nome=nome,
            data_nascimento=data_nascimento,
            responsavel=responsavel,
            email_responsavel=email,
            telefone=telefone,
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
        else:
            # EDM, MABC-2, Beery, PEDI — avaliação presencial, só cadastra o paciente
            return render(request, "questionario/iniciar_avaliacao.html", {
                "convite": convite,
                "cadastrado": True,
            })

    label, icon = TIPO_INFO.get(convite.tipo, (convite.get_tipo_display(), ""))
    return render(request, "questionario/iniciar_avaliacao.html", {
        "convite": convite,
        "tipo_label": label,
        "tipo_icon": icon,
    })
