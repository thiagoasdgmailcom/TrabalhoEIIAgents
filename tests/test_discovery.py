from pathlib import Path

import requests_mock

from magalu_analysis import config
from magalu_analysis.discovery import buscar_html_central_resultados, listar_documentos

FIXTURE_HTML = (Path(__file__).parent / "fixtures" / "central_resultados.html").read_text(
    encoding="utf-8"
)


def test_lista_apenas_trimestres_com_release_publicado():
    documentos = listar_documentos(FIXTURE_HTML)

    releases_1t26 = [d for d in documentos if d.tipo_documento == "release" and d.trimestre == 1 and d.ano == 2026]
    assert len(releases_1t26) == 1


def test_nao_lista_trimestre_ainda_nao_divulgado():
    documentos = listar_documentos(FIXTURE_HTML)

    releases_3t26 = [d for d in documentos if d.tipo_documento == "release" and d.trimestre == 3 and d.ano == 2026]
    assert releases_3t26 == []


def test_lista_tambem_outros_tipos_de_documento_para_classificacao_posterior():
    documentos = listar_documentos(FIXTURE_HTML)

    tipos_encontrados = {d.tipo_documento for d in documentos}
    assert "itr_dfp" in tipos_encontrados
    assert "apresentacao" in tipos_encontrados


def test_url_download_e_absoluta():
    documentos = listar_documentos(FIXTURE_HTML)

    release_1t26 = next(d for d in documentos if d.tipo_documento == "release" and d.trimestre == 1 and d.ano == 2026)
    assert release_1t26.url_download.startswith("https://ri.magazineluiza.com.br/Download.aspx")


def test_buscar_html_envia_user_agent_de_navegador():
    with requests_mock.Mocker() as mock:
        mock.get(config.URL_CENTRAL_RESULTADOS, text="<html>ok</html>")

        html = buscar_html_central_resultados()

        assert html == "<html>ok</html>"
        assert mock.last_request.headers["User-Agent"] == config.USER_AGENT
