"""Páginas públicas de SEO — uma página por instrumento, para captação orgânica."""
from django.shortcuts import render
from django.http import Http404

from ..data.seo_instrumentos import get_instrumento_seo, listar_instrumentos_seo


def instrumentos_lista(request):
    return render(request, "questionario/seo/lista.html", {
        "instrumentos": listar_instrumentos_seo(),
    })


def instrumento_detalhe(request, slug):
    dados = get_instrumento_seo(slug)
    if dados is None:
        raise Http404("Instrumento não encontrado")
    return render(request, "questionario/seo/instrumento.html", {
        "slug": slug,
        "i": dados,
        "outros": [x for x in listar_instrumentos_seo() if x["slug"] != slug][:6],
    })
