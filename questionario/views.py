
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

    from .data import PERGUNTAS, OPCOES, QUADRANTE

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
                avaliacao.status = "concluida"
                avaliacao.save()
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
from .models import Paciente, Avaliacao, Resposta, PerfilMedico, AvaliacaoVineland
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
        crm = request.POST.get("crm", "").strip()
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
        PerfilMedico.objects.create(user=user, crm=crm, especialidade=especialidade, telefone=telefone)
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
        perfil.crm = request.POST.get("crm", "").strip()
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
    pacientes = Paciente.objects.filter(medico=request.user).order_by("nome")
    total_avaliacoes = (
        Avaliacao.objects.filter(paciente__medico=request.user).count()
        + AvaliacaoVineland.objects.filter(paciente__medico=request.user).count()
    )
    concluidas = (
        Avaliacao.objects.filter(paciente__medico=request.user, status="concluida").count()
        + AvaliacaoVineland.objects.filter(paciente__medico=request.user, status="concluida").count()
    )
    return render(request, "questionario/index.html", {
        "pacientes": pacientes,
        "total_avaliacoes": total_avaliacoes,
        "concluidas": concluidas,
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

        import uuid
        paciente = Paciente.objects.create(
            medico=request.user,
            nome=nome, data_nascimento=data_nascimento,
            responsavel=responsavel, email_responsavel=email, telefone=telefone,
        )
        token = uuid.uuid4().hex
        Avaliacao.objects.create(paciente=paciente, token=token)
        messages.success(request, "Paciente cadastrado com sucesso.")
        return redirect("detalhe_paciente", paciente_id=paciente.id)

    return render(request, "questionario/novo_paciente.html")


@login_required
def nova_avaliacao(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id, medico=request.user)
    avaliacao = Avaliacao.objects.create(paciente=paciente, token=uuid.uuid4().hex)
    return redirect("questionario", avaliacao_id=avaliacao.id, pagina=1)


@login_required
def deletar_avaliacao(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id, paciente__medico=request.user)
    paciente_id = avaliacao.paciente_id
    if request.method == "POST":
        avaliacao.delete()
        messages.success(request, "Avaliação excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_id)


@login_required
def enviar_email_link(request, avaliacao_id):
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    email_dest = paciente.email_responsavel
    if not email_dest:
        messages.error(request, "Nenhum e-mail cadastrado para o responsável.")
        return redirect("detalhe_paciente", paciente_id=paciente.id)
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
    messages.success(request, f"E-mail enviado para {email_dest}.")
    return redirect("detalhe_paciente", paciente_id=paciente.id)


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
    paciente = get_object_or_404(Paciente, id=paciente_id, medico=request.user)
    avaliacoes = []
    for av in paciente.avaliacoes.all():
        if not av.token and av.status != "concluida":
            av.token = uuid.uuid4().hex
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
        "paciente": paciente, "avaliacoes": avaliacoes,
        "avaliacoes_vineland": avaliacoes_vineland,
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

    outras = paciente.avaliacoes.filter(status="concluida").exclude(id=avaliacao_id)
    return render(request, "questionario/dashboard.html", {
        "avaliacao": avaliacao, "paciente": paciente,
        "secoes": secoes_dados, "quadrantes": quadrantes_dados, "outras_avaliacoes": outras,
        "radar_labels": json.dumps([s["nome"] for s in secoes_dados]),
        "radar_valores": json.dumps([s["pct"] for s in secoes_dados]),
        "quad_labels": json.dumps([q["nome"] for q in quadrantes_dados]),
        "quad_valores": json.dumps([q["pct"] for q in quadrantes_dados]),
        "quad_cores": json.dumps([q["cor"] for q in quadrantes_dados]),
    })


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
    paciente = get_object_or_404(Paciente, id=paciente_id, medico=request.user)
    av = AvaliacaoVineland.objects.create(paciente=paciente, token=uuid.uuid4().hex)
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
    avaliacao = get_object_or_404(AvaliacaoVineland, id=avaliacao_id, paciente__medico=request.user)
    paciente_id = avaliacao.paciente_id
    if request.method == "POST":
        avaliacao.delete()
        messages.success(request, "Avaliação Vineland excluída com sucesso.")
    return redirect("detalhe_paciente", paciente_id=paciente_id)


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
    avaliacao = get_object_or_404(AvaliacaoVineland, id=avaliacao_id, paciente__medico=request.user)
    paciente = avaliacao.paciente
    email_dest = paciente.email_responsavel
    if not email_dest:
        messages.error(request, "Nenhum e-mail cadastrado para o responsável.")
        return redirect("detalhe_paciente", paciente_id=paciente.id)
    link = request.build_absolute_uri(f"/vineland/publico/{avaliacao.token}/1/")
    send_mail(
        subject="Escala Vineland — CeciSys",
        message=f"Olá, {paciente.responsavel}!\n\nResponda a Escala Vineland no link: {link}",
        from_email=None,
        recipient_list=[email_dest],
        fail_silently=False,
    )
    messages.success(request, f"E-mail enviado para {email_dest}.")
    return redirect("detalhe_paciente", paciente_id=paciente.id)
