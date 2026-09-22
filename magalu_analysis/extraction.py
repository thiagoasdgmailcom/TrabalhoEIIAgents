import json
from pathlib import Path

import pdfplumber

from .models import PaginaTexto


def extrair_paginas(caminho_pdf: Path, documento_id: str) -> list[PaginaTexto]:
    paginas = []
    with pdfplumber.open(caminho_pdf) as pdf:
        for numero, pagina in enumerate(pdf.pages, start=1):
            texto = pagina.extract_text() or ""
            paginas.append(PaginaTexto(documento_id=documento_id, numero_pagina=numero, texto=texto))
    return paginas


def salvar_paginas_json(paginas: list[PaginaTexto], caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    dados = [pagina.model_dump() for pagina in paginas]
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
