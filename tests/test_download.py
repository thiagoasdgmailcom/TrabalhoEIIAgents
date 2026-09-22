from pathlib import Path

import pytest
import requests
import requests_mock

from magalu_analysis import config
from magalu_analysis.discovery import DocumentoBruto
from magalu_analysis.download import (
    PdfCorrompidoError,
    PdfNaoTextualError,
    baixar_e_validar_documento,
    baixar_pdf,
    calcular_sha256,
    validar_pdf_textual,
)

FIXTURES = Path(__file__).parent / "fixtures"
PDF_TEXTUAL = (FIXTURES / "sample_release.pdf").read_bytes()
PDF_SEM_TEXTO = (FIXTURES / "sample_release_sem_texto.pdf").read_bytes()


def test_calcula_sha256_do_conteudo():
    assert calcular_sha256(b"abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert len(calcular_sha256(b"abc")) == 64
    assert calcular_sha256(b"abc") != calcular_sha256(b"abd")


def test_baixar_pdf_usa_user_agent_e_retorna_conteudo():
    with requests_mock.Mocker() as mock:
        mock.get("https://x/1.pdf", content=PDF_TEXTUAL)

        conteudo = baixar_pdf("https://x/1.pdf")

        assert conteudo == PDF_TEXTUAL
        assert mock.last_request.headers["User-Agent"] == config.USER_AGENT


def test_baixar_pdf_propaga_erro_http():
    with requests_mock.Mocker() as mock:
        mock.get("https://x/1.pdf", status_code=404)

        with pytest.raises(requests.HTTPError):
            baixar_pdf("https://x/1.pdf")


def test_validar_pdf_textual_retorna_numero_de_paginas():
    assert validar_pdf_textual(PDF_TEXTUAL) == 2


def test_validar_pdf_textual_rejeita_pdf_sem_texto():
    with pytest.raises(PdfNaoTextualError):
        validar_pdf_textual(PDF_SEM_TEXTO)


def test_validar_pdf_textual_rejeita_conteudo_corrompido():
    with pytest.raises(PdfCorrompidoError):
        validar_pdf_textual(b"isto nao e um pdf")


def test_baixar_e_validar_documento_salva_arquivo_e_retorna_documento(tmp_path):
    doc_bruto = DocumentoBruto(tipo_documento="release", ano=2026, trimestre=1, url_download="https://x/1.pdf")

    with requests_mock.Mocker() as mock:
        mock.get("https://x/1.pdf", content=PDF_TEXTUAL)

        documento = baixar_e_validar_documento(doc_bruto, diretorio_destino=tmp_path)

    assert documento.ano == 2026
    assert documento.trimestre == 1
    assert documento.num_paginas == 2
    assert documento.sha256 == calcular_sha256(PDF_TEXTUAL)
    assert Path(documento.nome_arquivo).suffix == ".pdf"
    assert (tmp_path / documento.nome_arquivo).exists()
