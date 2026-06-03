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
    # Módulos de psicologia
    AvaliacaoBDI, AvaliacaoBAI, AvaliacaoDASS21, AvaliacaoHAD, AvaliacaoBSL23,
    AvaliacaoAQ10Adulto, AvaliacaoAQ10Child, AvaliacaoDepEmocional, AvaliacaoSCQ,
    # Lote 2
    AvaliacaoConners, AvaliacaoETDAH, AvaliacaoAUQEI, AvaliacaoSCARED,
    AvaliacaoMASC, AvaliacaoBPQ,
    # Triagem internacional
    AvaliacaoPHQ9, AvaliacaoGAD7, AvaliacaoEPDS, AvaliacaoPCL5, AvaliacaoGHQ12,
    # Novas escalas — adulto
    AvaliacaoK10, AvaliacaoUCLA, AvaliacaoMSI_BPD, AvaliacaoGDS15, AvaliacaoRosenberg,
    AvaliacaoAUDIT, AvaliacaoBIS11, AvaliacaoHAMA, AvaliacaoLSAS,
    AvaliacaoRiscoSuicidio, AvaliacaoAgorafobia, AvaliacaoPanico,
    # Novas escalas — infantil
    AvaliacaoIAR, AvaliacaoPAS, AvaliacaoCDI,
)
from ..services import TIPO_INFO

TIPOS_ADULTO = {
    "bdi", "bai", "dass21", "had", "bsl23", "aq10_adulto",
    "dep_emocional", "bpq",
    # triagem internacional
    "phq9", "gad7", "epds", "pcl5", "ghq12",
    # novas escalas adulto
    "k10", "ucla", "msi_bpd", "gds15", "rosenberg", "audit", "bis11",
    "hama", "lsas", "risco_suicidio", "agorafobia", "panico",
}


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
        # Novos módulos — psicologia infantil (pais)
        "conners_pais": "conners_pais",
        "etdah_pais": "etdah_pais",
        "auqei": "auqei",
        "aq10_child": "aq10_child",
        "scared": "scared",
        "masc": "masc",
        "scq": "scq",
        # Novos módulos — professor
        "conners_prof": "conners_prof",
        "etdah_prof": "etdah_prof",
        # Novos módulos — adulto
        "bdi": "bdi",
        "bai": "bai",
        "dass21": "dass21",
        "had": "had",
        "bsl23": "bsl23",
        "aq10_adulto": "aq10_adulto",
        "dep_emocional": "dep_emocional",
        "bpq": "bpq",
        # Novos módulos — pediatria / neuropsicologia / psicopedagogia
        "denver": "denver",
        "qmpi": "qmpi",
        "quest_dislexia": "quest_dislexia",
        "checklist_dislexia": "checklist_dislexia",
        "prot_dislexia_prof": "prot_dislexia_prof",
        "inventario_dislexia": "inventario_dislexia",
        # Triagem internacional
        "phq9": "phq9",
        "gad7": "gad7",
        "epds": "epds",
        "pcl5": "pcl5",
        "ghq12": "ghq12",
        # Novas escalas — adulto
        "k10": "k10",
        "ucla": "ucla",
        "msi_bpd": "msi_bpd",
        "gds15": "gds15",
        "rosenberg": "rosenberg",
        "audit": "audit",
        "bis11": "bis11",
        "hama": "hama",
        "lsas": "lsas",
        "risco_suicidio": "risco_suicidio",
        "agorafobia": "agorafobia",
        "panico": "panico",
        # Novas escalas — infantil
        "iar": "iar",
        "pas": "pas",
        "cdi": "cdi",
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

    is_adulto = convite.tipo in TIPOS_ADULTO

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        data_nascimento = request.POST.get("data_nascimento", "")
        responsavel = request.POST.get("responsavel", "").strip() if not is_adulto else nome
        email = request.POST.get("email_responsavel", "").strip()
        telefone = request.POST.get("telefone", "").strip()
        consentimento = request.POST.get("consentimento", "")

        campos_obrigatorios_faltando = not nome or not data_nascimento or (not is_adulto and not responsavel)
        if campos_obrigatorios_faltando:
            msg = "Preencha os campos obrigatórios (nome e data de nascimento)." if is_adulto else "Preencha os campos obrigatórios (nome, data de nascimento e responsável)."
            return render(request, "questionario/dashboard/iniciar_avaliacao.html", {
                "convite": convite,
                "post": request.POST,
                "erro": msg,
                "is_adulto": is_adulto,
            })

        if not consentimento:
            return render(request, "questionario/dashboard/iniciar_avaliacao.html", {
                "convite": convite,
                "post": request.POST,
                "erro": "Você deve aceitar a Política de Privacidade para continuar.",
                "is_adulto": is_adulto,
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
        elif tipo == "bdi":
            AvaliacaoBDI.objects.create(paciente=paciente, token=t)
            return redirect("bdi_publico", token=t, pagina=1)
        elif tipo == "bai":
            AvaliacaoBAI.objects.create(paciente=paciente, token=t)
            return redirect("bai_publico", token=t, pagina=1)
        elif tipo == "dass21":
            AvaliacaoDASS21.objects.create(paciente=paciente, token=t)
            return redirect("dass21_publico", token=t, pagina=1)
        elif tipo == "had":
            AvaliacaoHAD.objects.create(paciente=paciente, token=t)
            return redirect("had_publico", token=t, pagina=1)
        elif tipo == "bsl23":
            AvaliacaoBSL23.objects.create(paciente=paciente, token=t)
            return redirect("bsl23_publico", token=t, pagina=1)
        elif tipo == "aq10_adulto":
            AvaliacaoAQ10Adulto.objects.create(paciente=paciente, token=t)
            return redirect("aq10_adulto_publico", token=t, pagina=1)
        elif tipo == "aq10_child":
            AvaliacaoAQ10Child.objects.create(paciente=paciente, token=t)
            return redirect("aq10_child_publico", token=t, pagina=1)
        elif tipo == "dep_emocional":
            AvaliacaoDepEmocional.objects.create(paciente=paciente, token=t)
            return redirect("dep_emocional_publico", token=t, pagina=1)
        elif tipo == "scq":
            AvaliacaoSCQ.objects.create(paciente=paciente, token=t)
            return redirect("scq_publico", token=t, pagina=1)
        elif tipo == "conners_pais":
            AvaliacaoConners.objects.create(paciente=paciente, token=t, respondente="pais")
            return redirect("conners_pais_publico", token=t, pagina=1)
        elif tipo == "conners_prof":
            AvaliacaoConners.objects.create(paciente=paciente, token=t, respondente="professor")
            return redirect("conners_prof_publico", token=t, pagina=1)
        elif tipo == "etdah_pais":
            AvaliacaoETDAH.objects.create(paciente=paciente, token=t, respondente="pais")
            return redirect("etdah_pais_publico", token=t, pagina=1)
        elif tipo == "etdah_prof":
            AvaliacaoETDAH.objects.create(paciente=paciente, token=t, respondente="professor")
            return redirect("etdah_prof_publico", token=t, pagina=1)
        elif tipo == "auqei":
            AvaliacaoAUQEI.objects.create(paciente=paciente, token=t)
            return redirect("auqei_publico", token=t, pagina=1)
        elif tipo == "scared":
            AvaliacaoSCARED.objects.create(paciente=paciente, token=t)
            return redirect("scared_publico", token=t, pagina=1)
        elif tipo == "masc":
            AvaliacaoMASC.objects.create(paciente=paciente, token=t)
            return redirect("masc_publico", token=t, pagina=1)
        elif tipo == "bpq":
            AvaliacaoBPQ.objects.create(paciente=paciente, token=t)
            return redirect("bpq_publico", token=t, pagina=1)
        elif tipo == "phq9":
            AvaliacaoPHQ9.objects.create(paciente=paciente, token=t)
            return redirect("phq9_publico", token=t, pagina=1)
        elif tipo == "gad7":
            AvaliacaoGAD7.objects.create(paciente=paciente, token=t)
            return redirect("gad7_publico", token=t, pagina=1)
        elif tipo == "epds":
            AvaliacaoEPDS.objects.create(paciente=paciente, token=t)
            return redirect("epds_publico", token=t, pagina=1)
        elif tipo == "pcl5":
            AvaliacaoPCL5.objects.create(paciente=paciente, token=t)
            return redirect("pcl5_publico", token=t, pagina=1)
        elif tipo == "ghq12":
            AvaliacaoGHQ12.objects.create(paciente=paciente, token=t)
            return redirect("ghq12_publico", token=t, pagina=1)
        elif tipo == "k10":
            AvaliacaoK10.objects.create(paciente=paciente, token=t)
            return redirect("k10_publico", token=t, pagina=1)
        elif tipo == "ucla":
            AvaliacaoUCLA.objects.create(paciente=paciente, token=t)
            return redirect("ucla_publico", token=t, pagina=1)
        elif tipo == "msi_bpd":
            AvaliacaoMSI_BPD.objects.create(paciente=paciente, token=t)
            return redirect("msi_bpd_publico", token=t, pagina=1)
        elif tipo == "gds15":
            AvaliacaoGDS15.objects.create(paciente=paciente, token=t)
            return redirect("gds15_publico", token=t, pagina=1)
        elif tipo == "rosenberg":
            AvaliacaoRosenberg.objects.create(paciente=paciente, token=t)
            return redirect("rosenberg_publico", token=t, pagina=1)
        elif tipo == "audit":
            AvaliacaoAUDIT.objects.create(paciente=paciente, token=t)
            return redirect("audit_publico", token=t, pagina=1)
        elif tipo == "bis11":
            AvaliacaoBIS11.objects.create(paciente=paciente, token=t)
            return redirect("bis11_publico", token=t, pagina=1)
        elif tipo == "hama":
            AvaliacaoHAMA.objects.create(paciente=paciente, token=t)
            return redirect("hama_publico", token=t, pagina=1)
        elif tipo == "lsas":
            AvaliacaoLSAS.objects.create(paciente=paciente, token=t)
            return redirect("lsas_publico", token=t, pagina=1)
        elif tipo == "risco_suicidio":
            AvaliacaoRiscoSuicidio.objects.create(paciente=paciente, token=t)
            return redirect("risco_suicidio_publico", token=t, pagina=1)
        elif tipo == "agorafobia":
            AvaliacaoAgorafobia.objects.create(paciente=paciente, token=t)
            return redirect("agorafobia_publico", token=t, pagina=1)
        elif tipo == "panico":
            AvaliacaoPanico.objects.create(paciente=paciente, token=t)
            return redirect("panico_publico", token=t, pagina=1)
        elif tipo == "iar":
            AvaliacaoIAR.objects.create(paciente=paciente, token=t)
            return redirect("iar_publico", token=t, pagina=1)
        elif tipo == "pas":
            AvaliacaoPAS.objects.create(paciente=paciente, token=t)
            return redirect("pas_publico", token=t, pagina=1)
        elif tipo == "cdi":
            AvaliacaoCDI.objects.create(paciente=paciente, token=t)
            return redirect("cdi_publico", token=t, pagina=1)
        else:
            # Módulos presenciais: CARS-2, EDM, MABC-2, Beery, Denver, QMPI, dislexia etc.
            return render(request, "questionario/dashboard/iniciar_avaliacao.html", {
                "convite": convite,
                "cadastrado": True,
            })

    label, icon = TIPO_INFO.get(convite.tipo, (convite.get_tipo_display(), ""))
    return render(request, "questionario/dashboard/iniciar_avaliacao.html", {
        "convite": convite,
        "tipo_label": label,
        "tipo_icon": icon,
        "is_adulto": is_adulto,
    })
