
def questionario_publico_view(request, token, pagina):
    from django.http import Http404
    avaliacao = get_object_or_404(Avaliacao, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/concluido.html")
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        pagina = 1
    secao_atual = SECOES[pagina - 1]
    itens_secao = secao_atual["itens"]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=itens_secao)}

    from .data import PERGUNTAS, OPCOES, QUADRANTE, calcular_pontuacao

    def _build_perguntas(itens, respostas):
        return [
            {"numero": item, "texto": PERGUNTAS.get(item, ""),
             "resposta_salva": respostas.get(item), "quadrante": QUADRANTE.get(item)}
            for item in itens
        ]

    perguntas_pagina = _build_perguntas(itens_secao, respostas_salvas)

    if request.method == "POST":
        erros = []
        respostas_novas = {}
        for item in itens_secao:
            val = request.POST.get(f"item_{item}")
            if val is None:
                erros.append(item)
            else:
                try:
                    v = int(val)
                    if 0 <= v <= 5:
                        respostas_novas[item] = v
                    else:
                        erros.append(item)
                except (ValueError, TypeError):
                    erros.append(item)

        if erros:
            messages.error(request, "Por favor, responda todas as perguntas antes de continuar.")
        else:
            for item, valor in respostas_novas.items():
                Resposta.objects.update_or_create(avaliacao=avaliacao, numero_item=item, defaults={"valor": valor})
            if pagina < TOTAL_PAGINAS:
                return redirect("questionario_publico", token=token, pagina=pagina+1)
            else:
                respostas_finais = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
                p = calcular_pontuacao(respostas_finais)
                avaliacao.pont_auditiva = p.get("auditiva", 0)
                avaliacao.pont_visual = p.get("visual", 0)
                avaliacao.pont_tato = p.get("tato", 0)
                avaliacao.pont_movimento = p.get("movimento", 0)
                avaliacao.pont_posicao = p.get("posicao", 0)
                avaliacao.pont_oral = p.get("oral", 0)
                avaliacao.pont_conduta = p.get("conduta", 0)
                avaliacao.pont_socioemocional = p.get("socioemocional", 0)
                avaliacao.pont_atencao = p.get("atencao", 0)
                avaliacao.pont_ex = p.get("EX", 0)
                avaliacao.pont_ev = p.get("EV", 0)
                avaliacao.pont_sn = p.get("SN", 0)
                avaliacao.pont_ob = p.get("OB", 0)
                avaliacao.status = "concluida"
                avaliacao.save()
                try:
                    _notificar_terapeuta(avaliacao.paciente, "sensorial", request)
                except Exception:
                    pass
                return render(request, "questionario/concluido.html")
        respostas_salvas.update(respostas_novas)
        perguntas_pagina = _build_perguntas(itens_secao, respostas_salvas)

    return render(request, "questionario/questionario.html", {
        "avaliacao": avaliacao,
        "secao": secao_atual,
        "perguntas": perguntas_pagina,
        "opcoes": OPCOES,
        "pagina": pagina,
        "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_secoes": [(i + 1, SECOES[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "publico": True,
    })
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import (Paciente, Avaliacao, Resposta, PerfilMedico, AvaliacaoVineland,
                     AvaliacaoEscolar, RespostaEscolar, AvaliacaoBebe, RespostaBebe,
                     AvaliacaoEDM, AvaliacaoMABC2, AvaliacaoBeery, AvaliacaoPEDI)
from .data import (SECOES, PERGUNTAS, OPCOES, QUADRANTE, QUADRANTES_CONFIG, SECOES_CONFIG,
                   calcular_pontuacao, classificar)
import json
import uuid

TOTAL_PAGINAS = len(SECOES)


# ─── AUTH ────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get("next", "index"))
        messages.error(request, "Usuário ou senha incorretos.")
    return render(request, "questionario/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


def registrar_view(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        registro_profissional = request.POST.get("registro_profissional", "").strip()
        especialidade = request.POST.get("especialidade", "").strip()
        telefone = request.POST.get("telefone", "").strip()

        erros = []
        if not nome or not username or not password:
            erros.append("Preencha todos os campos obrigatórios.")
        if password != password2:
            erros.append("As senhas não coincidem.")
        if len(password) < 6:
            erros.append("A senha deve ter pelo menos 6 caracteres.")
        if User.objects.filter(username=username).exists():
            erros.append("Este nome de usuário já está em uso.")
        if email and User.objects.filter(email=email).exists():
            erros.append("Este e-mail já está cadastrado.")

        if erros:
            for e in erros:
                messages.error(request, e)
            return render(request, "questionario/registrar.html", {"post": request.POST})

        partes = nome.strip().split(" ", 1)
        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=partes[0], last_name=partes[1] if len(partes) > 1 else ""
        )
        PerfilMedico.objects.create(user=user, registro_profissional=registro_profissional, especialidade=especialidade, telefone=telefone)
        login(request, user)
        messages.success(request, f"Bem-vindo(a), {user.first_name}! Conta criada com sucesso.")
        return redirect("index")

    return render(request, "questionario/registrar.html")


@login_required
def meu_perfil(request):
    perfil, _ = PerfilMedico.objects.get_or_create(user=request.user)
    if request.method == "POST":
        u = request.user
        nome = request.POST.get("nome", "").strip().split(" ", 1)
        u.first_name = nome[0]
        u.last_name = nome[1] if len(nome) > 1 else ""
        u.email = request.POST.get("email", "").strip()
        u.save()
        perfil.registro_profissional = request.POST.get("registro_profissional", "").strip()
        perfil.especialidade = request.POST.get("especialidade", "").strip()
        perfil.telefone = request.POST.get("telefone", "").strip()
        perfil.save()

        # Trocar senha, se preenchida
        nova_senha = request.POST.get("nova_senha", "")
        if nova_senha:
            if nova_senha == request.POST.get("nova_senha2", ""):
                if len(nova_senha) >= 6:
                    u.set_password(nova_senha)
                    u.save()
                    update_session_auth_hash(request, u)
                    messages.success(request, "Senha alterada com sucesso.")
                else:
                    messages.error(request, "A nova senha deve ter pelo menos 6 caracteres.")
            else:
                messages.error(request, "As novas senhas não coincidem.")

        messages.success(request, "Perfil atualizado com sucesso.")
        return redirect("meu_perfil")

    return render(request, "questionario/meu_perfil.html", {"perfil": perfil})


# ─── DASHBOARD / PACIENTES ───────────────────────────────────────────────────

@login_required
def index(request):
    from django.db.models import Count, Q, Avg
    from django.utils import timezone as tz
    pacientes = Paciente.objects.filter(medico=request.user).order_by("nome")
    total_pacientes = pacientes.count()
    total_sens = Avaliacao.objects.filter(paciente__medico=request.user).count()
    total_vinel = AvaliacaoVineland.objects.filter(paciente__medico=request.user).count()
    total_avaliacoes = total_sens + total_vinel
    concluidas_sens = Avaliacao.objects.filter(paciente__medico=request.user, status="concluida").count()
    concluidas_vinel = AvaliacaoVineland.objects.filter(paciente__medico=request.user, status="concluida").count()
    concluidas = concluidas_sens + concluidas_vinel
    em_andamento = total_avaliacoes - concluidas

    hoje = tz.now().date()
    inicio_mes = hoje.replace(day=1)
    novas_mes = (
        Avaliacao.objects.filter(paciente__medico=request.user, criado_em__date__gte=inicio_mes).count()
        + AvaliacaoVineland.objects.filter(paciente__medico=request.user, criado_em__date__gte=inicio_mes).count()
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


@login_required
def enviar_email_link(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    email_dest = paciente.email_responsavel
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if not email_dest:
        if is_ajax:
            from django.http import JsonResponse
            return JsonResponse({"ok": False, "message": "Nenhum e-mail cadastrado para o responsável."})
        messages.error(request, "Nenhum e-mail cadastrado para o responsável.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    link = request.build_absolute_uri(f"/questionario/publico/{avaliacao.token}/1/")
    html = render_to_string("questionario/email_link_avaliacao.html", {
        "paciente": paciente, "link": link,
    })
    send_mail(
        subject="Questionário CeciSys",
        message=f"Olá, {paciente.responsavel}!\n\nResponda o questionário no link: {link}",
        from_email=None,
        recipient_list=[email_dest],
        html_message=html,
        fail_silently=False,
    )
    avaliacao.email_enviado_em = tz.now()
    avaliacao.save(update_fields=["email_enviado_em"])
    if is_ajax:
        from django.http import JsonResponse
        return JsonResponse({"ok": True, "message": f"E-mail enviado para {email_dest}."})
    messages.success(request, f"E-mail enviado para {email_dest}.")
    return redirect("detalhe_paciente", paciente_id=paciente.uuid)


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
def lista_pacientes(request):
    from django.core.paginator import Paginator
    from django.db.models import Count, Q
    q = request.GET.get("q", "").strip()
    qs = (
        Paciente.objects.filter(medico=request.user)
        .annotate(
            sens_total=Count("avaliacoes", distinct=True),
            vinel_total=Count("avaliacoes_vineland", distinct=True),
            sens_conc=Count("avaliacoes", filter=Q(avaliacoes__status="concluida"), distinct=True),
            vinel_conc=Count("avaliacoes_vineland", filter=Q(avaliacoes_vineland__status="concluida"), distinct=True),
        )
        .order_by("nome")
    )
    if q:
        qs = qs.filter(nome__icontains=q)
    paginator = Paginator(qs, 10)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "questionario/lista_pacientes.html", {"pacientes": page, "q": q, "paginator": paginator})


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
        "avaliacoes_escolar": _build_lista_com_link(paciente.avaliacoes_escolar.all(), request, "escolar_publico"),
        "avaliacoes_bebe": _build_lista_com_link(paciente.avaliacoes_bebe.all(), request, "bebe_publico"),
        "avaliacoes_edm": paciente.avaliacoes_edm.all(),
        "avaliacoes_mabc2": paciente.avaliacoes_mabc2.all(),
        "avaliacoes_beery": paciente.avaliacoes_beery.all(),
        "avaliacoes_pedi": paciente.avaliacoes_pedi.all(),
    })


# ─── QUESTIONÁRIO ────────────────────────────────────────────────────────────

@login_required
def questionario_view(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("dashboard", avaliacao_id=avaliacao_id)
    if pagina < 1 or pagina > TOTAL_PAGINAS:
        return redirect("questionario", avaliacao_id=avaliacao_id, pagina=1)

    secao_atual = SECOES[pagina - 1]
    itens_secao = secao_atual["itens"]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=itens_secao)}

    if request.method == "POST":
        erros = []
        respostas_novas = {}
        for item in itens_secao:
            val = request.POST.get(f"item_{item}")
            if val is None:
                erros.append(item)
            else:
                try:
                    v = int(val)
                    if 0 <= v <= 5:
                        respostas_novas[item] = v
                    else:
                        erros.append(item)
                except (ValueError, TypeError):
                    erros.append(item)

        if erros:
            messages.error(request, "Por favor, responda todas as perguntas antes de continuar.")
        else:
            for item, valor in respostas_novas.items():
                Resposta.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=item, defaults={"valor": valor})
            proxima = pagina + 1
            avaliacao.pagina_atual = min(proxima, TOTAL_PAGINAS)
            avaliacao.save()
            if proxima > TOTAL_PAGINAS:
                return redirect("concluir", avaliacao_id=avaliacao_id)
            return redirect("questionario", avaliacao_id=avaliacao_id, pagina=proxima)
        respostas_salvas.update(respostas_novas)

    perguntas_pagina = [
        {"numero": item, "texto": PERGUNTAS.get(item, ""), "resposta_salva": respostas_salvas.get(item),
         "quadrante": QUADRANTE.get(item)}
        for item in itens_secao
    ]
    return render(request, "questionario/questionario.html", {
        "avaliacao": avaliacao, "secao": secao_atual, "perguntas": perguntas_pagina,
        "opcoes": OPCOES, "pagina": pagina, "total": TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / TOTAL_PAGINAS * 100),
        "paginas_secoes": [(i + 1, SECOES[i]["nome"]) for i in range(TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
    })


@login_required
def concluir(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id, paciente__medico=request.user)
    respostas_qs = avaliacao.respostas.all()
    if respostas_qs.count() < 86:
        messages.warning(request, "Ainda há perguntas sem resposta.")
        return redirect("questionario", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)

    respostas = {r.numero_item: r.valor for r in respostas_qs}
    p = calcular_pontuacao(respostas)
    avaliacao.pont_auditiva = p.get("auditiva", 0)
    avaliacao.pont_visual = p.get("visual", 0)
    avaliacao.pont_tato = p.get("tato", 0)
    avaliacao.pont_movimento = p.get("movimento", 0)
    avaliacao.pont_posicao = p.get("posicao", 0)
    avaliacao.pont_oral = p.get("oral", 0)
    avaliacao.pont_conduta = p.get("conduta", 0)
    avaliacao.pont_socioemocional = p.get("socioemocional", 0)
    avaliacao.pont_atencao = p.get("atencao", 0)
    avaliacao.pont_ex = p.get("EX", 0)
    avaliacao.pont_ev = p.get("EV", 0)
    avaliacao.pont_sn = p.get("SN", 0)
    avaliacao.pont_ob = p.get("OB", 0)
    avaliacao.status = "concluida"
    avaliacao.save()
    return redirect("dashboard", avaliacao_id=avaliacao_id)


@login_required
def salvar_observacoes(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("dashboard", avaliacao_id=avaliacao_id)
    return redirect("dashboard", avaliacao_id=avaliacao_id)


@login_required
def dashboard(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    if avaliacao.status != "concluida":
        return redirect("questionario", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)

    secao_map = {
        "auditiva": avaliacao.pont_auditiva, "visual": avaliacao.pont_visual,
        "tato": avaliacao.pont_tato, "movimento": avaliacao.pont_movimento,
        "posicao": avaliacao.pont_posicao, "oral": avaliacao.pont_oral,
        "conduta": avaliacao.pont_conduta, "socioemocional": avaliacao.pont_socioemocional,
        "atencao": avaliacao.pont_atencao,
    }
    secoes_dados = []
    for sid, config in SECOES_CONFIG.items():
        valor = secao_map.get(sid, 0) or 0
        maximo = config["max"]
        classificacao = classificar(valor, config["faixas"])
        secoes_dados.append({
            "id": sid, "nome": config["nome"], "valor": valor, "maximo": maximo,
            "pct": int(valor / maximo * 100) if maximo else 0,
            "classificacao": classificacao, "classe_css": _classe_css(classificacao),
        })

    quad_map = {"EX": avaliacao.pont_ex or 0, "EV": avaliacao.pont_ev or 0,
                "SN": avaliacao.pont_sn or 0, "OB": avaliacao.pont_ob or 0}
    quadrantes_dados = []
    for qid, config in QUADRANTES_CONFIG.items():
        valor = quad_map.get(qid, 0)
        maximo = config["max"]
        classificacao = classificar(valor, config["faixas"])
        quadrantes_dados.append({
            "id": qid, "nome": config["nome"], "subtitulo": config["subtitulo"],
            "valor": valor, "maximo": maximo,
            "pct": int(valor / maximo * 100) if maximo else 0,
            "classificacao": classificacao, "cor": config["cor"],
            "classe_css": _classe_css(classificacao),
        })

    todas_avaliacoes = list(paciente.avaliacoes.filter(status="concluida").order_by("data"))
    outras = [av for av in todas_avaliacoes if av.id != avaliacao_id]

    comparativo_labels = json.dumps([av.data.strftime("%d/%m/%Y") for av in todas_avaliacoes])
    dominios_comparativo = [
        {"key": "auditiva", "nome": "Auditiva", "campo": "pont_auditiva", "max": SECOES_CONFIG["auditiva"]["max"]},
        {"key": "visual", "nome": "Visual", "campo": "pont_visual", "max": SECOES_CONFIG["visual"]["max"]},
        {"key": "tato", "nome": "Tato", "campo": "pont_tato", "max": SECOES_CONFIG["tato"]["max"]},
        {"key": "movimento", "nome": "Movimento", "campo": "pont_movimento", "max": SECOES_CONFIG["movimento"]["max"]},
        {"key": "posicao", "nome": "Posição", "campo": "pont_posicao", "max": SECOES_CONFIG["posicao"]["max"]},
        {"key": "oral", "nome": "Oral", "campo": "pont_oral", "max": SECOES_CONFIG["oral"]["max"]},
        {"key": "conduta", "nome": "Conduta", "campo": "pont_conduta", "max": SECOES_CONFIG["conduta"]["max"]},
        {"key": "socioemocional", "nome": "Socioemocional", "campo": "pont_socioemocional", "max": SECOES_CONFIG["socioemocional"]["max"]},
        {"key": "atencao", "nome": "Atenção", "campo": "pont_atencao", "max": SECOES_CONFIG["atencao"]["max"]},
    ]
    cores_linha = ["#2E7D6B","#3E73D1","#E8793A","#9B59B6","#E8B84B","#C0392B","#16A085","#1ABC9C","#7DB87D"]
    comparativo_datasets = []
    for i, dom in enumerate(dominios_comparativo):
        valores = [round(getattr(av, dom["campo"]) / dom["max"] * 100) if getattr(av, dom["campo"]) is not None else 0 for av in todas_avaliacoes]
        comparativo_datasets.append({"label": dom["nome"], "data": valores, "borderColor": cores_linha[i], "backgroundColor": cores_linha[i] + "33", "tension": 0.3})

    return render(request, "questionario/dashboard.html", {
        "avaliacao": avaliacao, "paciente": paciente,
        "secoes": secoes_dados, "quadrantes": quadrantes_dados, "outras_avaliacoes": outras,
        "radar_labels": json.dumps([s["nome"] for s in secoes_dados]),
        "radar_valores": json.dumps([s["pct"] for s in secoes_dados]),
        "quad_labels": json.dumps([q["nome"] for q in quadrantes_dados]),
        "quad_valores": json.dumps([q["pct"] for q in quadrantes_dados]),
        "quad_cores": json.dumps([q["cor"] for q in quadrantes_dados]),
        "comparativo_labels": comparativo_labels,
        "comparativo_datasets": json.dumps(comparativo_datasets),
        "tem_comparativo": len(todas_avaliacoes) > 1,
    })


def _build_lista_com_link(queryset, request, publico_url_name):
    from django.urls import reverse
    result = []
    for av in queryset:
        if not av.token and av.status != "concluida":
            av.token = str(uuid.uuid4())
            av.save(update_fields=["token"])
        link_publico = None
        if av.token and av.status != "concluida":
            path = reverse(publico_url_name, kwargs={"token": av.token, "pagina": 1})
            link_publico = request.build_absolute_uri(path)
        result.append({"obj": av, "link_publico": link_publico})
    return result


def _notificar_terapeuta(paciente, tipo, request):
    from django.core.mail import send_mail
    terapeuta = paciente.medico
    if not terapeuta.email:
        return
    nome_tipo = "Perfil Sensorial" if tipo == "sensorial" else "Escala Vineland"
    send_mail(
        subject=f"CeciSys — Avaliação concluída: {paciente.nome}",
        message=(
            f"Olá, {terapeuta.get_full_name() or terapeuta.username}!\n\n"
            f"O responsável de {paciente.nome} concluiu o questionário de {nome_tipo}.\n"
            f"Acesse o sistema para visualizar os resultados."
        ),
        from_email=None,
        recipient_list=[terapeuta.email],
        fail_silently=True,
    )


def _classe_css(classificacao):
    return {"Muito menos": "muito-menos", "Menos": "menos", "Típico": "tipico",
            "Mais": "mais", "Muito mais": "muito-mais"}.get(classificacao, "")


# ─── VINELAND ─────────────────────────────────────────────────────────────────

from .models import RespostaVineland
from .vineland_data import (
    VINELAND_GRUPOS, VINELAND_PERGUNTAS, VINELAND_CATEGORIA,
    VINELAND_OPCOES, VINELAND_CATEGORIAS_CONFIG,
    calcular_pontuacao_vineland, classificar_qs,
)

VINELAND_TOTAL_PAGINAS = len(VINELAND_GRUPOS)


@login_required
def nova_avaliacao_vineland(request, paciente_id):
    from django.http import JsonResponse
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    av = AvaliacaoVineland.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "id": av.id})
    return redirect("vineland_form", avaliacao_id=av.id, pagina=1)


@login_required
def vineland_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoVineland, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("vineland_resultado", avaliacao_id=avaliacao_id)

    if pagina < 1 or pagina > VINELAND_TOTAL_PAGINAS:
        return redirect("vineland_form", avaliacao_id=avaliacao_id, pagina=1)

    grupo = VINELAND_GRUPOS[pagina - 1]
    itens = grupo["itens"]
    respostas_salvas = {
        r.numero_item: r.resposta
        for r in avaliacao.respostas.filter(numero_item__in=itens)
    }

    if request.method == "POST":
        erros = []
        novas = {}
        for item in itens:
            val = request.POST.get(f"item_{item}")
            opcoes_validas = [o[0] for o in VINELAND_OPCOES]
            if val not in opcoes_validas:
                erros.append(item)
            else:
                novas[item] = val

        if erros:
            messages.error(request, "Por favor, responda todos os itens antes de continuar.")
            respostas_salvas.update(novas)
        else:
            for item, valor in novas.items():
                RespostaVineland.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=item, defaults={"resposta": valor}
                )
            proxima = pagina + 1
            avaliacao.pagina_atual = min(proxima, VINELAND_TOTAL_PAGINAS)
            avaliacao.save(update_fields=["pagina_atual"])
            if proxima > VINELAND_TOTAL_PAGINAS:
                return redirect("vineland_concluir", avaliacao_id=avaliacao_id)
            return redirect("vineland_form", avaliacao_id=avaliacao_id, pagina=proxima)

    perguntas = [
        {
            "numero": item,
            "texto": VINELAND_PERGUNTAS.get(item, ""),
            "categoria": VINELAND_CATEGORIA.get(item, ""),
            "resposta_salva": respostas_salvas.get(item),
        }
        for item in itens
    ]

    return render(request, "questionario/vineland_form.html", {
        "avaliacao": avaliacao,
        "grupo": grupo,
        "perguntas": perguntas,
        "opcoes": VINELAND_OPCOES,
        "pagina": pagina,
        "total": VINELAND_TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / VINELAND_TOTAL_PAGINAS * 100),
        "paginas_grupos": [(i + 1, VINELAND_GRUPOS[i]["nome"]) for i in range(VINELAND_TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
    })


@login_required
def vineland_concluir(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoVineland, id=avaliacao_id, paciente__medico=request.user)
    total_itens = sum(len(g["itens"]) for g in VINELAND_GRUPOS)
    if avaliacao.respostas.count() < total_itens:
        messages.warning(request, "Ainda há itens sem resposta.")
        return redirect("vineland_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)

    respostas = {r.numero_item: r.resposta for r in avaliacao.respostas.all()}
    p = calcular_pontuacao_vineland(respostas)

    avaliacao.pont_total = p["total"]
    avaliacao.pont_comunicacao = p["C"]
    avaliacao.pont_locomocao = p["L"]
    avaliacao.pont_ocupacao = p["O"]
    avaliacao.pont_socializacao = p["S"]
    avaliacao.pont_autogoverno = p["AG"]
    avaliacao.pont_age = p["AGE"]
    avaliacao.pont_ac = p["AC"]
    avaliacao.pont_av = p["AV"]
    avaliacao.status = "concluida"
    avaliacao.save()
    return redirect("vineland_resultado", avaliacao_id=avaliacao_id)


@login_required
def salvar_observacoes_vineland(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoVineland, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("vineland_resultado", avaliacao_id=avaliacao_id)
    return redirect("vineland_resultado", avaliacao_id=avaliacao_id)


@login_required
def vineland_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoVineland, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    if avaliacao.status != "concluida":
        return redirect("vineland_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)

    if avaliacao.pont_total is None:
        respostas_dict = {r.numero_item: r.resposta for r in avaliacao.respostas.all()}
        p = calcular_pontuacao_vineland(respostas_dict)
        avaliacao.pont_total = p["total"]
        avaliacao.pont_comunicacao = p["C"]
        avaliacao.pont_locomocao = p["L"]
        avaliacao.pont_ocupacao = p["O"]
        avaliacao.pont_socializacao = p["S"]
        avaliacao.pont_autogoverno = p["AG"]
        avaliacao.pont_age = p["AGE"]
        avaliacao.pont_ac = p["AC"]
        avaliacao.pont_av = p["AV"]
        avaliacao.save(update_fields=[
            "pont_total", "pont_comunicacao", "pont_locomocao", "pont_ocupacao",
            "pont_socializacao", "pont_autogoverno", "pont_age", "pont_ac", "pont_av",
        ])

    if request.method == "POST":
        try:
            is_meses = int(request.POST.get("idade_social_meses", "").strip())
            if is_meses <= 0:
                raise ValueError
        except (ValueError, AttributeError):
            messages.error(request, "Digite um valor válido para a Idade Social (número inteiro de meses).")
            is_meses = None

        if is_meses:
            from django.utils import timezone as tz
            hoje = tz.now().date()
            b = paciente.data_nascimento
            ic_meses = (hoje.year - b.year) * 12 + (hoje.month - b.month)
            if ic_meses > 0:
                qs = round(is_meses / ic_meses * 100, 1)
            else:
                qs = None
            avaliacao.idade_social_meses = is_meses
            avaliacao.quociente_social = qs
            avaliacao.save(update_fields=["idade_social_meses", "quociente_social"])
            messages.success(request, "Quociente Social calculado com sucesso.")
            return redirect("vineland_resultado", avaliacao_id=avaliacao_id)

    from django.utils import timezone as tz
    hoje = tz.now().date()
    b = paciente.data_nascimento
    ic_meses = (hoje.year - b.year) * 12 + (hoje.month - b.month)

    categorias = [
        {
            "cod": cod,
            "nome": cfg["nome"],
            "max": cfg["max"],
            "valor": getattr(avaliacao, {
                "C": "pont_comunicacao", "L": "pont_locomocao",
                "O": "pont_ocupacao", "S": "pont_socializacao",
                "AG": "pont_autogoverno", "AGE": "pont_age",
                "AC": "pont_ac", "AV": "pont_av",
            }[cod]) or 0,
        }
        for cod, cfg in VINELAND_CATEGORIAS_CONFIG.items()
    ]

    qs_class = classificar_qs(avaliacao.quociente_social) if avaliacao.quociente_social else None

    return render(request, "questionario/vineland_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "ic_meses": ic_meses,
        "categorias": categorias,
        "qs_classificacao": qs_class,
    })


@login_required
def vineland_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoVineland, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação Vineland excluída com sucesso."})
        messages.success(request, "Avaliação Vineland excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


def vineland_publico_view(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoVineland, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/concluido.html")

    if pagina < 1 or pagina > VINELAND_TOTAL_PAGINAS:
        pagina = 1

    grupo = VINELAND_GRUPOS[pagina - 1]
    itens = grupo["itens"]
    respostas_salvas = {
        r.numero_item: r.resposta
        for r in avaliacao.respostas.filter(numero_item__in=itens)
    }

    if request.method == "POST":
        erros = []
        novas = {}
        for item in itens:
            val = request.POST.get(f"item_{item}")
            opcoes_validas = [o[0] for o in VINELAND_OPCOES]
            if val not in opcoes_validas:
                erros.append(item)
            else:
                novas[item] = val

        if erros:
            messages.error(request, "Por favor, responda todos os itens antes de continuar.")
            respostas_salvas.update(novas)
        else:
            for item, valor in novas.items():
                RespostaVineland.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=item, defaults={"resposta": valor}
                )
            proxima = pagina + 1
            avaliacao.pagina_atual = min(proxima, VINELAND_TOTAL_PAGINAS)
            avaliacao.save(update_fields=["pagina_atual"])
            if proxima > VINELAND_TOTAL_PAGINAS:
                respostas_dict = {r.numero_item: r.resposta for r in avaliacao.respostas.all()}
                p = calcular_pontuacao_vineland(respostas_dict)
                avaliacao.pont_total = p["total"]
                avaliacao.pont_comunicacao = p["C"]
                avaliacao.pont_locomocao = p["L"]
                avaliacao.pont_ocupacao = p["O"]
                avaliacao.pont_socializacao = p["S"]
                avaliacao.pont_autogoverno = p["AG"]
                avaliacao.pont_age = p["AGE"]
                avaliacao.pont_ac = p["AC"]
                avaliacao.pont_av = p["AV"]
                avaliacao.status = "concluida"
                avaliacao.save()
                try:
                    _notificar_terapeuta(avaliacao.paciente, "vineland", request)
                except Exception:
                    pass
                return render(request, "questionario/concluido.html")
            return redirect("vineland_publico", token=token, pagina=proxima)

    perguntas = [
        {
            "numero": item,
            "texto": VINELAND_PERGUNTAS.get(item, ""),
            "categoria": VINELAND_CATEGORIA.get(item, ""),
            "resposta_salva": respostas_salvas.get(item),
        }
        for item in itens
    ]

    return render(request, "questionario/vineland_form.html", {
        "avaliacao": avaliacao,
        "grupo": grupo,
        "perguntas": perguntas,
        "opcoes": VINELAND_OPCOES,
        "pagina": pagina,
        "total": VINELAND_TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / VINELAND_TOTAL_PAGINAS * 100),
        "paginas_grupos": [(i + 1, VINELAND_GRUPOS[i]["nome"]) for i in range(VINELAND_TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "publico": True,
        "token": token,
    })


@login_required
def enviar_email_link_vineland(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoVineland, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    email_dest = paciente.email_responsavel
    from django.http import JsonResponse
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if not email_dest:
        if is_ajax:
            return JsonResponse({"ok": False, "message": "Nenhum e-mail cadastrado para o responsável."})
        messages.error(request, "Nenhum e-mail cadastrado para o responsável.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    link = request.build_absolute_uri(f"/vineland/publico/{avaliacao.token}/1/")
    send_mail(
        subject="Escala Vineland — CeciSys",
        message=f"Olá, {paciente.responsavel}!\n\nResponda a Escala Vineland no link: {link}",
        from_email=None,
        recipient_list=[email_dest],
        fail_silently=False,
    )
    avaliacao.email_enviado_em = tz.now()
    avaliacao.save(update_fields=["email_enviado_em"])
    if is_ajax:
        return JsonResponse({"ok": True, "message": f"E-mail enviado para {email_dest}."})
    messages.success(request, f"E-mail enviado para {email_dest}.")
    return redirect("detalhe_paciente", paciente_id=paciente.uuid)


# ═══════════════════════════════════════════════════════════════════════════════
# QUESTIONÁRIO SENSORIAL ESCOLAR
# ═══════════════════════════════════════════════════════════════════════════════

from .data_escolar import (
    SECOES as ESCOLAR_SECOES,
    PERGUNTAS as ESCOLAR_PERGUNTAS,
    OPCOES as ESCOLAR_OPCOES,
    DOMINIOS_CONFIG as ESCOLAR_DOMINIOS_CONFIG,
    calcular_pontuacao_escolar,
    classificar_escolar,
)

ESCOLAR_TOTAL_PAGINAS = len(ESCOLAR_SECOES)


@login_required
def nova_avaliacao_escolar(request, paciente_id):
    from django.http import JsonResponse
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    av = AvaliacaoEscolar.objects.create(paciente=paciente, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "id": av.id})
    return redirect("escolar_form", avaliacao_id=av.id, pagina=1)


@login_required
def escolar_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoEscolar, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("escolar_resultado", avaliacao_id=avaliacao_id)

    if pagina < 1 or pagina > ESCOLAR_TOTAL_PAGINAS:
        return redirect("escolar_form", avaliacao_id=avaliacao_id, pagina=1)

    secao_atual = ESCOLAR_SECOES[pagina - 1]
    itens = secao_atual["itens"]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=itens)}

    if request.method == "POST":
        erros = []
        novas = {}
        for item in itens:
            val = request.POST.get(f"item_{item}")
            if val is None:
                erros.append(item)
            else:
                try:
                    v = int(val)
                    if 0 <= v <= 4:
                        novas[item] = v
                    else:
                        erros.append(item)
                except (ValueError, TypeError):
                    erros.append(item)

        if erros:
            messages.error(request, "Por favor, responda todos os itens antes de continuar.")
            respostas_salvas.update(novas)
        else:
            for item, valor in novas.items():
                RespostaEscolar.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=item, defaults={"valor": valor}
                )
            proxima = pagina + 1
            avaliacao.pagina_atual = min(proxima, ESCOLAR_TOTAL_PAGINAS)
            avaliacao.save(update_fields=["pagina_atual"])
            if proxima > ESCOLAR_TOTAL_PAGINAS:
                return redirect("escolar_concluir", avaliacao_id=avaliacao_id)
            return redirect("escolar_form", avaliacao_id=avaliacao_id, pagina=proxima)

    perguntas = [
        {"numero": item, "texto": ESCOLAR_PERGUNTAS.get(item, ""), "resposta_salva": respostas_salvas.get(item)}
        for item in itens
    ]

    return render(request, "questionario/escolar_form.html", {
        "avaliacao": avaliacao,
        "secao": secao_atual,
        "perguntas": perguntas,
        "opcoes": ESCOLAR_OPCOES,
        "pagina": pagina,
        "total": ESCOLAR_TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / ESCOLAR_TOTAL_PAGINAS * 100),
        "paginas_secoes": [(i + 1, ESCOLAR_SECOES[i]["nome"]) for i in range(ESCOLAR_TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
    })


@login_required
def escolar_concluir(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoEscolar, id=avaliacao_id, paciente__medico=request.user)
    total_itens = sum(len(s["itens"]) for s in ESCOLAR_SECOES)
    if avaliacao.respostas.count() < total_itens:
        messages.warning(request, "Ainda há itens sem resposta.")
        return redirect("escolar_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)

    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    p = calcular_pontuacao_escolar(respostas)
    avaliacao.pont_auditivo = p.get("auditivo", 0)
    avaliacao.pont_visual = p.get("visual", 0)
    avaliacao.pont_tatil = p.get("tatil", 0)
    avaliacao.pont_vestibular = p.get("vestibular", 0)
    avaliacao.pont_social = p.get("social", 0)
    avaliacao.status = "concluida"
    avaliacao.save()
    return redirect("escolar_resultado", avaliacao_id=avaliacao_id)


@login_required
def escolar_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoEscolar, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    if avaliacao.status != "concluida":
        return redirect("escolar_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)

    if avaliacao.pont_auditivo is None:
        respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
        p = calcular_pontuacao_escolar(respostas)
        avaliacao.pont_auditivo = p.get("auditivo", 0)
        avaliacao.pont_visual = p.get("visual", 0)
        avaliacao.pont_tatil = p.get("tatil", 0)
        avaliacao.pont_vestibular = p.get("vestibular", 0)
        avaliacao.pont_social = p.get("social", 0)
        avaliacao.save(update_fields=["pont_auditivo", "pont_visual", "pont_tatil", "pont_vestibular", "pont_social"])

    campo_map = {
        "auditivo": avaliacao.pont_auditivo,
        "visual": avaliacao.pont_visual,
        "tatil": avaliacao.pont_tatil,
        "vestibular": avaliacao.pont_vestibular,
        "social": avaliacao.pont_social,
    }
    dominios = []
    for dom_id, config in ESCOLAR_DOMINIOS_CONFIG.items():
        valor = campo_map.get(dom_id) or 0
        maximo = config["max"]
        classificacao = classificar_escolar(valor, maximo)
        dominios.append({
            "id": dom_id,
            "nome": config["nome"],
            "valor": valor,
            "maximo": maximo,
            "pct": int(valor / maximo * 100) if maximo else 0,
            "classificacao": classificacao,
        })

    return render(request, "questionario/escolar_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "dominios": dominios,
        "dominios_json": json.dumps([{"nome": d["nome"], "pct": d["pct"]} for d in dominios]),
    })


@login_required
def escolar_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoEscolar, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação Escolar excluída com sucesso."})
        messages.success(request, "Avaliação Escolar excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_escolar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoEscolar, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("escolar_resultado", avaliacao_id=avaliacao_id)
    return redirect("escolar_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_escolar(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.http import JsonResponse
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoEscolar, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    email_dest = paciente.email_responsavel
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if not email_dest:
        if is_ajax:
            return JsonResponse({"ok": False, "message": "Nenhum e-mail cadastrado para o responsável."})
        messages.error(request, "Nenhum e-mail cadastrado para o responsável.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    link = request.build_absolute_uri(f"/escolar/publico/{avaliacao.token}/1/")
    send_mail(
        subject="Questionário Sensorial Escolar — CeciSys",
        message=f"Olá, {paciente.responsavel}!\n\nResponda o questionário no link: {link}",
        from_email=None,
        recipient_list=[email_dest],
        fail_silently=False,
    )
    avaliacao.email_enviado_em = tz.now()
    avaliacao.save(update_fields=["email_enviado_em"])
    if is_ajax:
        return JsonResponse({"ok": True, "message": f"E-mail enviado para {email_dest}."})
    messages.success(request, f"E-mail enviado para {email_dest}.")
    return redirect("detalhe_paciente", paciente_id=paciente.uuid)


def escolar_publico_view(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoEscolar, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/concluido.html")
    if pagina < 1 or pagina > ESCOLAR_TOTAL_PAGINAS:
        pagina = 1
    secao_atual = ESCOLAR_SECOES[pagina - 1]
    itens_secao = secao_atual["itens"]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=itens_secao)}

    if request.method == "POST":
        erros = []
        respostas_novas = {}
        for item in itens_secao:
            val = request.POST.get(f"item_{item}")
            if val is None:
                erros.append(item)
            else:
                try:
                    v = int(val)
                    if 0 <= v <= 4:
                        respostas_novas[item] = v
                    else:
                        erros.append(item)
                except (ValueError, TypeError):
                    erros.append(item)
        if erros:
            messages.error(request, "Por favor, responda todas as perguntas antes de continuar.")
        else:
            for item, valor in respostas_novas.items():
                RespostaEscolar.objects.update_or_create(avaliacao=avaliacao, numero_item=item, defaults={"valor": valor})
            if pagina < ESCOLAR_TOTAL_PAGINAS:
                avaliacao.pagina_atual = pagina + 1
                avaliacao.save(update_fields=["pagina_atual"])
                return redirect("escolar_publico", token=token, pagina=pagina + 1)
            else:
                respostas_finais = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
                p = calcular_pontuacao_escolar(respostas_finais)
                avaliacao.pont_auditivo = p.get("auditivo", 0)
                avaliacao.pont_visual = p.get("visual", 0)
                avaliacao.pont_tatil = p.get("tatil", 0)
                avaliacao.pont_vestibular = p.get("vestibular", 0)
                avaliacao.pont_social = p.get("social", 0)
                avaliacao.status = "concluida"
                avaliacao.save()
                try:
                    _notificar_terapeuta(avaliacao.paciente, "escolar", request)
                except Exception:
                    pass
                return render(request, "questionario/concluido.html")
        respostas_salvas.update(respostas_novas)

    perguntas = [
        {"numero": item, "texto": ESCOLAR_PERGUNTAS.get(item, ""), "resposta_salva": respostas_salvas.get(item)}
        for item in itens_secao
    ]
    return render(request, "questionario/escolar_form.html", {
        "avaliacao": avaliacao, "secao": secao_atual, "perguntas": perguntas,
        "opcoes": ESCOLAR_OPCOES, "pagina": pagina, "total": ESCOLAR_TOTAL_PAGINAS,
        "progresso": int((pagina - 1) / ESCOLAR_TOTAL_PAGINAS * 100),
        "paginas_secoes": [(i + 1, ESCOLAR_SECOES[i]["nome"]) for i in range(ESCOLAR_TOTAL_PAGINAS)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "publico": True,
    })


# ═══════════════════════════════════════════════════════════════════════════════
# PERFIL SENSORIAL BEBÊ / CRIANÇA PEQUENA
# ═══════════════════════════════════════════════════════════════════════════════

from .data_bebe import (
    SECOES_BEBE, SECOES_PEQUENA,
    PERGUNTAS_BEBE, PERGUNTAS_PEQUENA,
    OPCOES_BEBE,
    QUADRANTE_BEBE, QUADRANTE_PEQUENA,
    QUADRANTES_CONFIG as BEBE_QUADRANTES_CONFIG,
    calcular_pontuacao_bebe,
    classificar_bebe,
)


@login_required
def nova_avaliacao_bebe(request, paciente_id):
    from django.http import JsonResponse
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    faixa = request.GET.get("faixa", "bebe")
    if faixa not in ("bebe", "crianca_pequena"):
        faixa = "bebe"
    av = AvaliacaoBebe.objects.create(paciente=paciente, faixa=faixa, token=str(uuid.uuid4()))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "id": av.id})
    return redirect("bebe_form", avaliacao_id=av.id, pagina=1)


@login_required
def bebe_form(request, avaliacao_id, pagina):
    avaliacao = get_object_or_404(AvaliacaoBebe, id=avaliacao_id, paciente__medico=request.user)
    if avaliacao.status == "concluida":
        return redirect("bebe_resultado", avaliacao_id=avaliacao_id)

    if avaliacao.faixa == "bebe":
        secoes = SECOES_BEBE
        perguntas_data = PERGUNTAS_BEBE
    else:
        secoes = SECOES_PEQUENA
        perguntas_data = PERGUNTAS_PEQUENA

    total_paginas = len(secoes)
    if pagina < 1 or pagina > total_paginas:
        return redirect("bebe_form", avaliacao_id=avaliacao_id, pagina=1)

    secao_atual = secoes[pagina - 1]
    itens = secao_atual["itens"]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=itens)}

    if request.method == "POST":
        erros = []
        novas = {}
        for item in itens:
            val = request.POST.get(f"item_{item}")
            if val is None:
                erros.append(item)
            else:
                try:
                    v = int(val)
                    if 1 <= v <= 5:
                        novas[item] = v
                    else:
                        erros.append(item)
                except (ValueError, TypeError):
                    erros.append(item)

        if erros:
            messages.error(request, "Por favor, responda todos os itens antes de continuar.")
            respostas_salvas.update(novas)
        else:
            for item, valor in novas.items():
                RespostaBebe.objects.update_or_create(
                    avaliacao=avaliacao, numero_item=item, defaults={"valor": valor}
                )
            proxima = pagina + 1
            avaliacao.pagina_atual = min(proxima, total_paginas)
            avaliacao.save(update_fields=["pagina_atual"])
            if proxima > total_paginas:
                return redirect("bebe_concluir", avaliacao_id=avaliacao_id)
            return redirect("bebe_form", avaliacao_id=avaliacao_id, pagina=proxima)

    perguntas = [
        {"numero": item, "texto": perguntas_data.get(item, ""), "resposta_salva": respostas_salvas.get(item)}
        for item in itens
    ]

    return render(request, "questionario/bebe_form.html", {
        "avaliacao": avaliacao,
        "secao": secao_atual,
        "perguntas": perguntas,
        "opcoes": OPCOES_BEBE,
        "pagina": pagina,
        "total": total_paginas,
        "progresso": int((pagina - 1) / total_paginas * 100),
        "paginas_secoes": [(i + 1, secoes[i]["nome"]) for i in range(total_paginas)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
    })


@login_required
def bebe_concluir(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoBebe, id=avaliacao_id, paciente__medico=request.user)
    secoes = SECOES_BEBE if avaliacao.faixa == "bebe" else SECOES_PEQUENA
    total_itens = sum(len(s["itens"]) for s in secoes)
    if avaliacao.respostas.count() < total_itens:
        messages.warning(request, "Ainda há itens sem resposta.")
        return redirect("bebe_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)

    respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
    p = calcular_pontuacao_bebe(respostas, avaliacao.faixa)
    avaliacao.pont_busca = p.get("busca", 0)
    avaliacao.pont_evitamento = p.get("evitamento", 0)
    avaliacao.pont_sensibilidade = p.get("sensibilidade", 0)
    avaliacao.pont_registro = p.get("registro", 0)
    avaliacao.status = "concluida"
    avaliacao.save()
    return redirect("bebe_resultado", avaliacao_id=avaliacao_id)


@login_required
def bebe_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoBebe, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    if avaliacao.status != "concluida":
        return redirect("bebe_form", avaliacao_id=avaliacao_id, pagina=avaliacao.pagina_atual)

    if avaliacao.pont_busca is None:
        respostas = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
        p = calcular_pontuacao_bebe(respostas, avaliacao.faixa)
        avaliacao.pont_busca = p.get("busca", 0)
        avaliacao.pont_evitamento = p.get("evitamento", 0)
        avaliacao.pont_sensibilidade = p.get("sensibilidade", 0)
        avaliacao.pont_registro = p.get("registro", 0)
        avaliacao.save(update_fields=["pont_busca", "pont_evitamento", "pont_sensibilidade", "pont_registro"])

    faixa_key = "max_bebe" if avaliacao.faixa == "bebe" else "max_pequena"
    campo_map = {
        "busca": avaliacao.pont_busca,
        "evitamento": avaliacao.pont_evitamento,
        "sensibilidade": avaliacao.pont_sensibilidade,
        "registro": avaliacao.pont_registro,
    }
    quadrantes = []
    for quad_id, config in BEBE_QUADRANTES_CONFIG.items():
        valor = campo_map.get(quad_id) or 0
        maximo = config[faixa_key]
        classificacao = classificar_bebe(valor, maximo)
        quadrantes.append({
            "id": quad_id,
            "nome": config["nome"],
            "cor": config["cor"],
            "valor": valor,
            "maximo": maximo,
            "pct": int(valor / maximo * 100) if maximo else 0,
            "classificacao": classificacao,
        })

    return render(request, "questionario/bebe_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "quadrantes": quadrantes,
        "quadrantes_json": json.dumps([{"nome": q["nome"], "pct": q["pct"], "cor": q["cor"]} for q in quadrantes]),
    })


@login_required
def bebe_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoBebe, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação Bebê excluída com sucesso."})
        messages.success(request, "Avaliação Bebê excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_bebe(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoBebe, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("bebe_resultado", avaliacao_id=avaliacao_id)
    return redirect("bebe_resultado", avaliacao_id=avaliacao_id)


@login_required
def enviar_email_bebe(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.http import JsonResponse
    from django.utils import timezone as tz
    avaliacao = get_object_or_404(AvaliacaoBebe, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    email_dest = paciente.email_responsavel
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if not email_dest:
        if is_ajax:
            return JsonResponse({"ok": False, "message": "Nenhum e-mail cadastrado para o responsável."})
        messages.error(request, "Nenhum e-mail cadastrado para o responsável.")
        return redirect("detalhe_paciente", paciente_id=paciente.uuid)
    link = request.build_absolute_uri(f"/bebe/publico/{avaliacao.token}/1/")
    send_mail(
        subject="Perfil Sensorial Bebê — CeciSys",
        message=f"Olá, {paciente.responsavel}!\n\nResponda o questionário no link: {link}",
        from_email=None,
        recipient_list=[email_dest],
        fail_silently=False,
    )
    avaliacao.email_enviado_em = tz.now()
    avaliacao.save(update_fields=["email_enviado_em"])
    if is_ajax:
        return JsonResponse({"ok": True, "message": f"E-mail enviado para {email_dest}."})
    messages.success(request, f"E-mail enviado para {email_dest}.")
    return redirect("detalhe_paciente", paciente_id=paciente.uuid)


def bebe_publico_view(request, token, pagina):
    avaliacao = get_object_or_404(AvaliacaoBebe, token=token)
    if avaliacao.status == "concluida":
        return render(request, "questionario/concluido.html")
    faixa = avaliacao.faixa
    secoes = SECOES_BEBE if faixa == "bebe" else SECOES_PEQUENA
    perguntas_dict = PERGUNTAS_BEBE if faixa == "bebe" else PERGUNTAS_PEQUENA
    total = len(secoes)
    if pagina < 1 or pagina > total:
        pagina = 1
    secao_atual = secoes[pagina - 1]
    itens_secao = secao_atual["itens"]
    respostas_salvas = {r.numero_item: r.valor for r in avaliacao.respostas.filter(numero_item__in=itens_secao)}

    if request.method == "POST":
        erros = []
        respostas_novas = {}
        for item in itens_secao:
            val = request.POST.get(f"item_{item}")
            if val is None:
                erros.append(item)
            else:
                try:
                    v = int(val)
                    if 1 <= v <= 5:
                        respostas_novas[item] = v
                    else:
                        erros.append(item)
                except (ValueError, TypeError):
                    erros.append(item)
        if erros:
            messages.error(request, "Por favor, responda todas as perguntas antes de continuar.")
        else:
            for item, valor in respostas_novas.items():
                RespostaBebe.objects.update_or_create(avaliacao=avaliacao, numero_item=item, defaults={"valor": valor})
            if pagina < total:
                avaliacao.pagina_atual = pagina + 1
                avaliacao.save(update_fields=["pagina_atual"])
                return redirect("bebe_publico", token=token, pagina=pagina + 1)
            else:
                respostas_finais = {r.numero_item: r.valor for r in avaliacao.respostas.all()}
                p = calcular_pontuacao_bebe(respostas_finais, faixa)
                avaliacao.pont_busca = p.get("busca", 0)
                avaliacao.pont_evitamento = p.get("evitamento", 0)
                avaliacao.pont_sensibilidade = p.get("sensibilidade", 0)
                avaliacao.pont_registro = p.get("registro", 0)
                avaliacao.status = "concluida"
                avaliacao.save()
                try:
                    _notificar_terapeuta(avaliacao.paciente, "bebe", request)
                except Exception:
                    pass
                return render(request, "questionario/concluido.html")
        respostas_salvas.update(respostas_novas)

    perguntas = [
        {"numero": item, "texto": perguntas_dict.get(item, ""), "resposta_salva": respostas_salvas.get(item)}
        for item in itens_secao
    ]
    return render(request, "questionario/bebe_form.html", {
        "avaliacao": avaliacao, "secao": secao_atual, "perguntas": perguntas,
        "opcoes": OPCOES_BEBE, "pagina": pagina, "total": total,
        "progresso": int((pagina - 1) / total * 100),
        "paginas_secoes": [(i + 1, secoes[i]["nome"]) for i in range(total)],
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "publico": True,
    })


# ═══════════════════════════════════════════════════════════════════════════════
# EDM — ESCALA DE DESENVOLVIMENTO MOTOR
# ═══════════════════════════════════════════════════════════════════════════════

def _classificar_qm(qm):
    if qm is None:
        return "—"
    if qm >= 130:
        return "Superior"
    elif qm >= 110:
        return "Normal Alto"
    elif qm >= 90:
        return "Normal Médio"
    elif qm >= 70:
        return "Normal Baixo"
    elif qm >= 50:
        return "Inferior"
    else:
        return "Muito Inferior"


@login_required
def nova_avaliacao_edm(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    av = AvaliacaoEDM.objects.create(paciente=paciente)
    return redirect("edm_form", avaliacao_id=av.id)


@login_required
def edm_form(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoEDM, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    if request.method == "POST":
        def _get_int(name):
            try:
                v = int(request.POST.get(name, "").strip())
                return v if v >= 0 else None
            except (ValueError, AttributeError):
                return None

        mf = _get_int("motricidade_fina")
        ma = _get_int("motricidade_ampla")
        eq = _get_int("equilibrio")
        ec = _get_int("esquema_corporal")
        oe = _get_int("organizacao_espacial")
        ot = _get_int("organizacao_temporal")
        lat = request.POST.get("lateralidade", "").strip() or None

        avaliacao.idade_motricidade_fina = mf
        avaliacao.idade_motricidade_ampla = ma
        avaliacao.idade_equilibrio = eq
        avaliacao.idade_esquema_corporal = ec
        avaliacao.idade_organizacao_espacial = oe
        avaliacao.idade_organizacao_temporal = ot
        avaliacao.lateralidade = lat

        idades = [v for v in [mf, ma, eq, ec, oe, ot] if v is not None]
        if idades:
            img = sum(idades) / len(idades)
            avaliacao.idade_motora_geral = round(img, 1)
            hoje = __import__('django.utils.timezone', fromlist=['now']).now().date()
            b = paciente.data_nascimento
            ic = (hoje.year - b.year) * 12 + (hoje.month - b.month)
            if ic > 0:
                avaliacao.quociente_motor = round(img / ic * 100, 1)
            else:
                avaliacao.quociente_motor = None
        else:
            avaliacao.idade_motora_geral = None
            avaliacao.quociente_motor = None

        avaliacao.save()
        messages.success(request, "EDM salvo com sucesso.")
        return redirect("edm_resultado", avaliacao_id=avaliacao_id)

    return render(request, "questionario/edm_form.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
    })


@login_required
def edm_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoEDM, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    dominios = [
        {"nome": "Motricidade Fina",       "valor": avaliacao.idade_motricidade_fina},
        {"nome": "Motricidade Ampla",       "valor": avaliacao.idade_motricidade_ampla},
        {"nome": "Equilíbrio",              "valor": avaliacao.idade_equilibrio},
        {"nome": "Esquema Corporal",        "valor": avaliacao.idade_esquema_corporal},
        {"nome": "Organização Espacial",    "valor": avaliacao.idade_organizacao_espacial},
        {"nome": "Organização Temporal",    "valor": avaliacao.idade_organizacao_temporal},
    ]

    lat_label = dict(AvaliacaoEDM.LATERALIDADE_CHOICES).get(avaliacao.lateralidade, "—") if avaliacao.lateralidade else "—"

    return render(request, "questionario/edm_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "dominios": dominios,
        "lat_label": lat_label,
        "qm_classificacao": _classificar_qm(avaliacao.quociente_motor),
        "dominios_json": json.dumps([{"nome": d["nome"], "valor": d["valor"] or 0} for d in dominios]),
    })


@login_required
def edm_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoEDM, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação EDM excluída com sucesso."})
        messages.success(request, "Avaliação EDM excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_edm(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoEDM, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("edm_resultado", avaliacao_id=avaliacao_id)
    return redirect("edm_resultado", avaliacao_id=avaliacao_id)


# ═══════════════════════════════════════════════════════════════════════════════
# MABC-2
# ═══════════════════════════════════════════════════════════════════════════════

def _mabc2_escore_para_percentil(escore_total):
    """Conversão aproximada escore total (3-57) → percentil."""
    tabela = [
        (3, 0), (6, 0), (9, 1), (12, 2), (15, 5), (18, 9),
        (21, 16), (24, 25), (27, 37), (30, 50), (33, 63),
        (36, 75), (39, 84), (42, 91), (45, 95), (48, 98),
        (51, 99), (57, 99),
    ]
    if escore_total is None:
        return None
    for escore, perc in tabela:
        if escore_total <= escore:
            return perc
    return 99


def _classificar_mabc2(percentil):
    if percentil is None:
        return "—"
    if percentil <= 5:
        return "Dificuldade significativa"
    elif percentil <= 15:
        return "Risco"
    else:
        return "Típico"


@login_required
def nova_avaliacao_mabc2(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    av = AvaliacaoMABC2.objects.create(paciente=paciente, faixa_etaria="3_6")
    return redirect("mabc2_form", avaliacao_id=av.id)


@login_required
def mabc2_form(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoMABC2, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    if request.method == "POST":
        def _get_float(name):
            try:
                return float(request.POST.get(name, "").strip())
            except (ValueError, AttributeError):
                return None

        def _get_int(name):
            try:
                return int(request.POST.get(name, "").strip())
            except (ValueError, AttributeError):
                return None

        avaliacao.faixa_etaria = request.POST.get("faixa_etaria", "3_6")
        avaliacao.md1_raw = _get_float("md1_raw")
        avaliacao.md2_raw = _get_float("md2_raw")
        avaliacao.md3_raw = _get_float("md3_raw")
        avaliacao.ac1_raw = _get_float("ac1_raw")
        avaliacao.ac2_raw = _get_float("ac2_raw")
        avaliacao.eq1_raw = _get_float("eq1_raw")
        avaliacao.eq2_raw = _get_float("eq2_raw")
        avaliacao.eq3_raw = _get_float("eq3_raw")
        avaliacao.md_escore = _get_int("md_escore")
        avaliacao.ac_escore = _get_int("ac_escore")
        avaliacao.eq_escore = _get_int("eq_escore")

        scores = [avaliacao.md_escore, avaliacao.ac_escore, avaliacao.eq_escore]
        if all(s is not None for s in scores):
            avaliacao.escore_total = sum(scores)
            avaliacao.percentil = _mabc2_escore_para_percentil(avaliacao.escore_total)
        avaliacao.save()
        messages.success(request, "MABC-2 salvo com sucesso.")
        return redirect("mabc2_resultado", avaliacao_id=avaliacao_id)

    return render(request, "questionario/mabc2_form.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "faixa_choices": AvaliacaoMABC2.FAIXA_CHOICES,
    })


@login_required
def mabc2_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoMABC2, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    classificacao = _classificar_mabc2(avaliacao.percentil)
    faixa_label = dict(AvaliacaoMABC2.FAIXA_CHOICES).get(avaliacao.faixa_etaria, "—")

    componentes = [
        {"nome": "Destreza Manual", "escore": avaliacao.md_escore},
        {"nome": "Arremesso/Recepção", "escore": avaliacao.ac_escore},
        {"nome": "Equilíbrio", "escore": avaliacao.eq_escore},
    ]

    return render(request, "questionario/mabc2_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "componentes": componentes,
        "classificacao": classificacao,
        "faixa_label": faixa_label,
        "componentes_json": json.dumps([{"nome": c["nome"], "escore": c["escore"] or 0} for c in componentes]),
    })


@login_required
def mabc2_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoMABC2, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação MABC-2 excluída com sucesso."})
        messages.success(request, "Avaliação MABC-2 excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_mabc2(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoMABC2, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("mabc2_resultado", avaliacao_id=avaliacao_id)
    return redirect("mabc2_resultado", avaliacao_id=avaliacao_id)


# ═══════════════════════════════════════════════════════════════════════════════
# BEERY VMI
# ═══════════════════════════════════════════════════════════════════════════════

_BEERY_ESCORE_PERCENTIL = {
    55: 0, 60: 0, 65: 1, 70: 2, 75: 5, 80: 9, 85: 16,
    90: 25, 95: 37, 100: 50, 105: 63, 110: 75, 115: 84,
    120: 91, 125: 95, 130: 98, 135: 99, 140: 99,
}


def _beery_escore_para_percentil(escore):
    if escore is None:
        return None
    # Encontra a entrada mais próxima
    chaves = sorted(_BEERY_ESCORE_PERCENTIL.keys())
    if escore <= chaves[0]:
        return _BEERY_ESCORE_PERCENTIL[chaves[0]]
    if escore >= chaves[-1]:
        return _BEERY_ESCORE_PERCENTIL[chaves[-1]]
    for i in range(len(chaves) - 1):
        if chaves[i] <= escore < chaves[i + 1]:
            return _BEERY_ESCORE_PERCENTIL[chaves[i]]
    return None


def _classificar_beery(escore):
    if escore is None:
        return "—"
    if escore < 70:
        return "Dificuldade significativa"
    elif escore < 85:
        return "Abaixo da média"
    elif escore <= 115:
        return "Médio"
    elif escore <= 130:
        return "Acima da média"
    else:
        return "Superior"


@login_required
def nova_avaliacao_beery(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    av = AvaliacaoBeery.objects.create(paciente=paciente)
    return redirect("beery_form", avaliacao_id=av.id)


@login_required
def beery_form(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoBeery, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    if request.method == "POST":
        def _get_int(name):
            try:
                return int(request.POST.get(name, "").strip())
            except (ValueError, AttributeError):
                return None

        avaliacao.idade_anos = _get_int("idade_anos")
        avaliacao.idade_meses = _get_int("idade_meses")
        avaliacao.vmi_raw = _get_int("vmi_raw")
        avaliacao.vp_raw = _get_int("vp_raw")
        avaliacao.mc_raw = _get_int("mc_raw")
        avaliacao.vmi_escore = _get_int("vmi_escore")
        avaliacao.vp_escore = _get_int("vp_escore")
        avaliacao.mc_escore = _get_int("mc_escore")
        avaliacao.vmi_percentil = _beery_escore_para_percentil(avaliacao.vmi_escore)
        avaliacao.vp_percentil = _beery_escore_para_percentil(avaliacao.vp_escore)
        avaliacao.mc_percentil = _beery_escore_para_percentil(avaliacao.mc_escore)
        avaliacao.save()
        messages.success(request, "Beery VMI salvo com sucesso.")
        return redirect("beery_resultado", avaliacao_id=avaliacao_id)

    return render(request, "questionario/beery_form.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
    })


@login_required
def beery_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoBeery, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    subtestes = [
        {
            "nome": "VMI (Integração Visuomotora)",
            "raw": avaliacao.vmi_raw,
            "escore": avaliacao.vmi_escore,
            "percentil": avaliacao.vmi_percentil,
            "classificacao": _classificar_beery(avaliacao.vmi_escore),
        },
        {
            "nome": "Percepção Visual",
            "raw": avaliacao.vp_raw,
            "escore": avaliacao.vp_escore,
            "percentil": avaliacao.vp_percentil,
            "classificacao": _classificar_beery(avaliacao.vp_escore),
        },
        {
            "nome": "Coordenação Motora",
            "raw": avaliacao.mc_raw,
            "escore": avaliacao.mc_escore,
            "percentil": avaliacao.mc_percentil,
            "classificacao": _classificar_beery(avaliacao.mc_escore),
        },
    ]

    return render(request, "questionario/beery_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "subtestes": subtestes,
        "subtestes_json": json.dumps([
            {"nome": s["nome"], "escore": s["escore"] or 0} for s in subtestes
        ]),
    })


@login_required
def beery_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoBeery, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação Beery excluída com sucesso."})
        messages.success(request, "Avaliação Beery excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_beery(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoBeery, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("beery_resultado", avaliacao_id=avaliacao_id)
    return redirect("beery_resultado", avaliacao_id=avaliacao_id)


# ═══════════════════════════════════════════════════════════════════════════════
# PEDI
# ═══════════════════════════════════════════════════════════════════════════════

_PEDI_FS_MAX = {"autocuidado": 73, "mobilidade": 59, "funcao_social": 65}
_PEDI_CA_MAX = {"autocuidado": 40, "mobilidade": 40, "funcao_social": 40}


@login_required
def nova_avaliacao_pedi(request, paciente_id):
    paciente = get_object_or_404(Paciente, uuid=paciente_id, medico=request.user)
    av = AvaliacaoPEDI.objects.create(paciente=paciente)
    return redirect("pedi_form", avaliacao_id=av.id)


@login_required
def pedi_form(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoPEDI, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    if request.method == "POST":
        def _get_int(name):
            try:
                return int(request.POST.get(name, "").strip())
            except (ValueError, AttributeError):
                return None

        avaliacao.fs_autocuidado = _get_int("fs_autocuidado")
        avaliacao.fs_mobilidade = _get_int("fs_mobilidade")
        avaliacao.fs_funcao_social = _get_int("fs_funcao_social")
        avaliacao.ca_autocuidado = _get_int("ca_autocuidado")
        avaliacao.ca_mobilidade = _get_int("ca_mobilidade")
        avaliacao.ca_funcao_social = _get_int("ca_funcao_social")

        # Escala 0-100 por aproximação (raw/max * 100)
        def _escala(raw, maximo):
            if raw is None or maximo == 0:
                return None
            return round(min(raw, maximo) / maximo * 100, 1)

        avaliacao.fs_autocuidado_escala = _escala(avaliacao.fs_autocuidado, _PEDI_FS_MAX["autocuidado"])
        avaliacao.fs_mobilidade_escala = _escala(avaliacao.fs_mobilidade, _PEDI_FS_MAX["mobilidade"])
        avaliacao.fs_funcao_social_escala = _escala(avaliacao.fs_funcao_social, _PEDI_FS_MAX["funcao_social"])
        avaliacao.ca_autocuidado_escala = _escala(avaliacao.ca_autocuidado, _PEDI_CA_MAX["autocuidado"])
        avaliacao.ca_mobilidade_escala = _escala(avaliacao.ca_mobilidade, _PEDI_CA_MAX["mobilidade"])
        avaliacao.ca_funcao_social_escala = _escala(avaliacao.ca_funcao_social, _PEDI_CA_MAX["funcao_social"])

        avaliacao.save()
        messages.success(request, "PEDI salvo com sucesso.")
        return redirect("pedi_resultado", avaliacao_id=avaliacao_id)

    return render(request, "questionario/pedi_form.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "fs_max": _PEDI_FS_MAX,
        "ca_max": _PEDI_CA_MAX,
    })


@login_required
def pedi_resultado(request, avaliacao_id):
    avaliacao = get_object_or_404(AvaliacaoPEDI, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente

    dominios_fs = [
        {"nome": "Autocuidado",    "raw": avaliacao.fs_autocuidado,    "max": _PEDI_FS_MAX["autocuidado"],   "escala": avaliacao.fs_autocuidado_escala},
        {"nome": "Mobilidade",     "raw": avaliacao.fs_mobilidade,     "max": _PEDI_FS_MAX["mobilidade"],    "escala": avaliacao.fs_mobilidade_escala},
        {"nome": "Função Social",  "raw": avaliacao.fs_funcao_social,  "max": _PEDI_FS_MAX["funcao_social"], "escala": avaliacao.fs_funcao_social_escala},
    ]
    dominios_ca = [
        {"nome": "Autocuidado",    "raw": avaliacao.ca_autocuidado,    "max": _PEDI_CA_MAX["autocuidado"],   "escala": avaliacao.ca_autocuidado_escala},
        {"nome": "Mobilidade",     "raw": avaliacao.ca_mobilidade,     "max": _PEDI_CA_MAX["mobilidade"],    "escala": avaliacao.ca_mobilidade_escala},
        {"nome": "Função Social",  "raw": avaliacao.ca_funcao_social,  "max": _PEDI_CA_MAX["funcao_social"], "escala": avaliacao.ca_funcao_social_escala},
    ]

    return render(request, "questionario/pedi_resultado.html", {
        "avaliacao": avaliacao,
        "paciente": paciente,
        "dominios_fs": dominios_fs,
        "dominios_ca": dominios_ca,
        "chart_json": json.dumps({
            "labels": ["Autocuidado", "Mobilidade", "Função Social"],
            "fs": [d["escala"] or 0 for d in dominios_fs],
            "ca": [d["escala"] or 0 for d in dominios_ca],
        }),
    })


@login_required
def pedi_deletar(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoPEDI, id=avaliacao_id, paciente__medico=request.user)
    paciente_uuid = avaliacao.paciente.uuid
    if request.method == "POST":
        avaliacao.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "message": "Avaliação PEDI excluída com sucesso."})
        messages.success(request, "Avaliação PEDI excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_uuid)


@login_required
def salvar_observacoes_pedi(request, avaliacao_id):
    from django.http import JsonResponse
    avaliacao = get_object_or_404(AvaliacaoPEDI, id=avaliacao_id, paciente__medico=request.user)
    if request.method == "POST":
        avaliacao.observacoes = request.POST.get("observacoes", "").strip()
        avaliacao.save(update_fields=["observacoes"])
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Observações salvas com sucesso.")
        return redirect("pedi_resultado", avaliacao_id=avaliacao_id)
    return redirect("pedi_resultado", avaliacao_id=avaliacao_id)
