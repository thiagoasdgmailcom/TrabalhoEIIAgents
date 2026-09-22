from magalu_analysis.classification import filtrar_releases_resultados
from magalu_analysis.discovery import DocumentoBruto


def test_mantem_apenas_documentos_do_tipo_release():
    documentos = [
        DocumentoBruto(tipo_documento="release", ano=2026, trimestre=1, url_download="https://x/1"),
        DocumentoBruto(tipo_documento="itr_dfp", ano=2026, trimestre=1, url_download="https://x/2"),
        DocumentoBruto(tipo_documento="apresentacao", ano=2026, trimestre=1, url_download="https://x/3"),
        DocumentoBruto(tipo_documento="audio", ano=2026, trimestre=1, url_download="https://x/4"),
        DocumentoBruto(tipo_documento="transcricao", ano=2026, trimestre=1, url_download="https://x/5"),
    ]

    releases = filtrar_releases_resultados(documentos)

    assert len(releases) == 1
    assert releases[0].tipo_documento == "release"


def test_lista_vazia_quando_nao_ha_releases():
    documentos = [
        DocumentoBruto(tipo_documento="apresentacao", ano=2026, trimestre=1, url_download="https://x/3"),
    ]

    assert filtrar_releases_resultados(documentos) == []
