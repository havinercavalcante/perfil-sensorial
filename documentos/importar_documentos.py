"""
Script de importação em lote de documentos.

Como usar:
  1. Organize seus arquivos numa pasta (ex: /tmp/docs/)
  2. Crie um CSV com os metadados (veja o exemplo abaixo)
  3. Execute: python importar_documentos.py caminho/para/planilha.csv

Formato do CSV (separador: ponto e vírgula):
  titulo;categoria;plano_minimo;especialidades;arquivo
  "Anamnese Adulto";Anamnese;start;psicologo,neuropsicoplogo;/tmp/docs/anamnese_adulto.pdf
  "Laudo de Depressão";Laudos;plus;psicologo;/tmp/docs/laudo_depressao.docx
  "Contrato Terapêutico";Contratos;start;;/tmp/docs/contrato.docx

Colunas:
  titulo         - Nome do documento
  categoria      - Nome da categoria (será criada se não existir)
  plano_minimo   - start | plus | elite
  especialidades - codigos separados por vírgula (vazio = todas)
                   Códigos: terapeuta_ocupacional, psicologo, fonoaudiologo,
                            neuropsicoplogo, psicopedagogo, pediatra,
                            neuropediatra, analista_aba
  arquivo        - Caminho absoluto do arquivo PDF ou DOCX
"""

import os
import sys
import csv
import django
from pathlib import Path

# Configura o Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "perfil_sensorial.settings")
django.setup()

from django.core.files import File
from documentos.models import CategoriaDocumento, Documento
from questionario.models import Especialidade

PLANOS_VALIDOS = {"start", "plus", "elite"}

# Ícones padrão por categoria (pode editar no admin depois)
ICONES_CATEGORIA = {
    "anamnese":       "clipboard",
    "anamneses":      "clipboard",
    "laudo":          "file-check",
    "laudos":         "file-check",
    "contrato":       "file-signature",
    "contratos":      "file-signature",
    "atestado":       "shield-check",
    "atestados":      "shield-check",
    "relatório":      "bar-chart-2",
    "relatorio":      "bar-chart-2",
    "relatórios":     "bar-chart-2",
    "relatorios":     "bar-chart-2",
    "declaração":     "scroll",
    "declaracao":     "scroll",
    "declarações":    "scroll",
    "declaracoes":    "scroll",
    "instrumento":    "clipboard-list",
    "instrumentos":   "clipboard-list",
    "ficha":          "list",
    "fichas":         "list",
    "recibo":         "receipt",
    "recibos":        "receipt",
    "contrato":       "file-text",
    "kit":            "package",
    "avaliação":      "search",
    "avaliacao":      "search",
    "avaliações":     "search",
    "avaliacoes":     "search",
}


def get_ou_criar_categoria(nome):
    nome_limpo = nome.strip()
    slug = (nome_limpo.lower()
            .replace(" ", "-")
            .replace("ã", "a").replace("ç", "c").replace("é", "e")
            .replace("á", "a").replace("ó", "o").replace("ê", "e")
            .replace("í", "i").replace("ú", "u").replace("â", "a")
            .replace("ô", "o").replace("õ", "o"))

    icone = "file-text"
    for chave, valor in ICONES_CATEGORIA.items():
        if chave in nome_limpo.lower():
            icone = valor
            break

    cat, criado = CategoriaDocumento.objects.get_or_create(
        codigo=slug[:40],
        defaults={"nome": nome_limpo, "icone": icone, "ordem": 0}
    )
    if criado:
        print(f"  [+] Categoria criada: {nome_limpo} ({slug})")
    return cat


def importar(csv_path):
    csv_path = Path(csv_path)
    if not csv_path.exists():
        print(f"Erro: arquivo CSV não encontrado: {csv_path}")
        sys.exit(1)

    criados  = 0
    pulados  = 0
    erros    = 0

    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for i, row in enumerate(reader, start=2):
            titulo        = row.get("titulo", "").strip()
            cat_nome      = row.get("categoria", "").strip()
            plano_minimo  = row.get("plano_minimo", "start").strip().lower()
            espec_str     = row.get("especialidades", "").strip()
            arquivo_path  = row.get("arquivo", "").strip()

            if not titulo or not arquivo_path:
                print(f"Linha {i}: titulo ou arquivo vazio — pulado.")
                pulados += 1
                continue

            if plano_minimo not in PLANOS_VALIDOS:
                print(f"Linha {i}: plano_minimo inválido '{plano_minimo}' — usando 'start'.")
                plano_minimo = "start"

            arquivo = Path(arquivo_path)
            if not arquivo.exists():
                print(f"Linha {i}: arquivo não encontrado: {arquivo_path} — pulado.")
                pulados += 1
                continue

            if Documento.objects.filter(titulo=titulo).exists():
                print(f"Linha {i}: '{titulo}' já existe — pulado.")
                pulados += 1
                continue

            categoria = get_ou_criar_categoria(cat_nome or "Geral")

            try:
                with open(arquivo, "rb") as arq:
                    doc = Documento(
                        titulo=titulo,
                        categoria=categoria,
                        plano_minimo=plano_minimo,
                        ativo=True,
                    )
                    doc.arquivo.save(arquivo.name, File(arq), save=False)
                    doc.save()

                if espec_str:
                    codigos = [c.strip() for c in espec_str.split(",") if c.strip()]
                    espec_objs = Especialidade.objects.filter(codigo__in=codigos)
                    doc.especialidades.set(espec_objs)
                    nao_encontradas = set(codigos) - set(espec_objs.values_list("codigo", flat=True))
                    if nao_encontradas:
                        print(f"  [!] Especialidades não encontradas: {nao_encontradas}")

                print(f"Linha {i}: '{titulo}' importado.")
                criados += 1

            except Exception as e:
                print(f"Linha {i}: ERRO ao importar '{titulo}': {e}")
                erros += 1

    print(f"\nImportação concluída: {criados} criados | {pulados} pulados | {erros} erros")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python importar_documentos.py planilha.csv")
        print(__doc__)
        sys.exit(1)
    importar(sys.argv[1])
