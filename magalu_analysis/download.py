import hashlib
import io
from datetime import datetime, timezone
from pathlib import Path

import pdfplumber
import requests
from pdfminer.pdfparser import PDFSyntaxError
from pdfplumber.utils.exceptions import PdfminerException

from . import config
from .discovery import DocumentoBruto
from .models import Documento


class PdfNaoTextualError(Exception):
    pass


class PdfCorrompidoError(Exception):
    pass


def baixar_pdf(url: str) -> bytes:
    resposta = requests.get(url, headers={"User-Agent": config.USER_AGENT}, timeout=60)
    resposta.raise_for_status()
    return resposta.content


def calcular_sha256(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


def validar_pdf_textual(conteudo: bytes) -> int:
    try:
        with pdfplumber.open(io.BytesIO(conteudo)) as pdf:
            num_paginas = len(pdf.pages)
            tem_texto = any((pagina.extract_text() or "").strip() for pagina in pdf.pages)
    except (PDFSyntaxError, PdfminerException, ValueError) as erro:
        raise PdfCorrompidoError(str(erro)) from erro

    if not tem_texto:
        raise PdfNaoTextualError("PDF não contém texto extraível em nenhuma página")

    return num_paginas


def baixar_e_validar_documento(doc_bruto: DocumentoBruto, diretorio_destino: Path) -> Documento:
    conteudo = baixar_pdf(doc_bruto.url_download)
    num_paginas = validar_pdf_textual(conteudo)
    sha256 = calcular_sha256(conteudo)

    nome_arquivo = f"release_{doc_bruto.trimestre}T{doc_bruto.ano % 100:02d}.pdf"
    diretorio_destino.mkdir(parents=True, exist_ok=True)
    (diretorio_destino / nome_arquivo).write_bytes(conteudo)

    return Documento(
        documento_id=f"magalu-{doc_bruto.ano}-q{doc_bruto.trimestre}",
        nome_arquivo=nome_arquivo,
        url_origem=doc_bruto.url_download,
        ano=doc_bruto.ano,
        trimestre=doc_bruto.trimestre,
        data_download=datetime.now(timezone.utc).date(),
        num_paginas=num_paginas,
        sha256=sha256,
    )
