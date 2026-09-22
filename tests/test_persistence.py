import json

import pytest

from magalu_analysis.persistence import IndicadoresAusentesError, consolidar_indicadores_do_run

INDICADOR = {
    "documento_id": "magalu-2026-q1",
    "indicador": "Receita Líquida",
    "categoria": "financeiro",
    "segmento": "consolidado",
    "tipo_periodo": "trimestre",
    "ajustado_ou_reportado": None,
    "unidade": "R$ bilhões",
    "valor_original": "R$15,2 bilhões",
    "valor_normalizado": 15.2,
    "pagina": 1,
    "trecho_fonte": "totalizaram R$15,2 bilhões",
    "confianca": "alta",
}


def _criar_run(tmp_path, documento_ids):
    diretorio_run = tmp_path / "run-teste"
    diretorio_documentos = diretorio_run / "documents"
    diretorio_documentos.mkdir(parents=True)

    documentos = [
        {
            "documento_id": doc_id,
            "nome_arquivo": f"{doc_id}.pdf",
            "url_origem": "https://x/1.pdf",
            "ano": 2026,
            "trimestre": 1,
            "data_download": "2026-09-17",
            "num_paginas": 2,
            "sha256": "a" * 64,
        }
        for doc_id in documento_ids
    ]
    manifest = {
        "run_id": "run-teste",
        "empresa": "Magazine Luiza",
        "n_releases": len(documento_ids),
        "periodos_selecionados": [[2026, 1]],
        "data_execucao": "2026-09-17T10:00:00Z",
        "documentos": documentos,
    }
    (diretorio_run / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    for doc_id in documento_ids:
        (diretorio_documentos / f"{doc_id}.indicators.json").write_text(
            json.dumps([{**INDICADOR, "documento_id": doc_id}]), encoding="utf-8"
        )

    return diretorio_run


def test_consolida_indicadores_de_todos_os_documentos_do_run(tmp_path):
    diretorio_run = _criar_run(tmp_path, ["magalu-2026-q1", "magalu-2025-q4"])

    indicadores = consolidar_indicadores_do_run(diretorio_run)

    assert len(indicadores) == 2
    assert {i.documento_id for i in indicadores} == {"magalu-2026-q1", "magalu-2025-q4"}


def test_levanta_erro_quando_falta_indicators_json_de_um_documento(tmp_path):
    diretorio_run = _criar_run(tmp_path, ["magalu-2026-q1"])
    (diretorio_run / "documents" / "magalu-2026-q1.indicators.json").unlink()

    with pytest.raises(IndicadoresAusentesError, match="magalu-2026-q1"):
        consolidar_indicadores_do_run(diretorio_run)
