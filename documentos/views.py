import os
import mimetypes
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.db.models import Q
from .models import CategoriaDocumento, Documento, DownloadDocumento, PLANO_ORDEM


@login_required
def biblioteca(request):
    perfil = request.user.perfil

    if not perfil.plano_ativo:
        return render(request, "documentos/biblioteca.html", {
            "sem_plano": True,
            "categorias": [],
            "documentos": [],
        })

    categoria_slug = request.GET.get("categoria", "")
    busca          = request.GET.get("q", "").strip()

    categorias = CategoriaDocumento.objects.filter(
        documentos__ativo=True
    ).distinct().order_by("ordem", "nome")

    docs_qs = Documento.objects.filter(ativo=True).select_related("categoria").prefetch_related("especialidades")

    if categoria_slug:
        docs_qs = docs_qs.filter(categoria__codigo=categoria_slug)

    if busca:
        docs_qs = docs_qs.filter(
            Q(titulo__icontains=busca) | Q(descricao__icontains=busca)
        )

    # Filtro por especialidade do profissional
    especialidades_usuario = list(perfil.especialidades.values_list("codigo", flat=True))
    if especialidades_usuario:
        docs_qs = docs_qs.filter(
            Q(especialidades__isnull=True) |
            Q(especialidades__codigo__in=especialidades_usuario)
        ).distinct()

    plano_usuario = PLANO_ORDEM.get(perfil.plano, 0)

    documentos_lista = []
    for doc in docs_qs:
        plano_doc = PLANO_ORDEM.get(doc.plano_minimo, 1)
        documentos_lista.append({
            "doc":           doc,
            "acesso":        plano_usuario >= plano_doc,
            "bloqueado_por": doc.plano_minimo if plano_usuario < plano_doc else None,
        })

    paginator = Paginator(documentos_lista, 24)
    page_obj  = paginator.get_page(request.GET.get("page"))

    return render(request, "documentos/biblioteca.html", {
        "categorias":      categorias,
        "documentos":      page_obj,
        "page_obj":        page_obj,
        "categoria_ativa": categoria_slug,
        "busca":           busca,
        "total":           len(documentos_lista),
        "sem_plano":       False,
    })


@login_required
def download_documento(request, token):
    doc    = get_object_or_404(Documento, token=token, ativo=True)
    perfil = request.user.perfil

    if not doc.usuario_tem_acesso(perfil):
        return HttpResponseForbidden(
            "Seu plano não permite o acesso a este documento."
        )

    if not doc.arquivo or not doc.arquivo.storage.exists(doc.arquivo.name):
        raise Http404("Arquivo não encontrado no servidor.")

    DownloadDocumento.objects.create(documento=doc, user=request.user)

    file_path = doc.arquivo.path
    content_type, _ = mimetypes.guess_type(file_path)
    content_type = content_type or "application/octet-stream"

    response = FileResponse(
        open(file_path, "rb"),
        content_type=content_type,
        as_attachment=True,
        filename=os.path.basename(file_path),
    )
    return response


@login_required
def preview_documento(request, token):
    """Serve PDF inline para visualização no browser."""
    doc    = get_object_or_404(Documento, token=token, ativo=True)
    perfil = request.user.perfil

    if not doc.usuario_tem_acesso(perfil):
        return HttpResponseForbidden("Seu plano não permite o acesso a este documento.")

    if not doc.eh_pdf:
        raise Http404("Preview disponível apenas para arquivos PDF.")

    if not doc.arquivo.storage.exists(doc.arquivo.name):
        raise Http404("Arquivo não encontrado no servidor.")

    return FileResponse(
        open(doc.arquivo.path, "rb"),
        content_type="application/pdf",
        as_attachment=False,
    )
