import json

import pytest

from magalu_analysis.indicators_schema import IndicadoresInvalidosError, carregar_indicadores

INDICADOR_VALIDO = {
    "documento_id": "magalu-2026-q1",
    "indicador": "EBITDA Ajustado",
    "categoria": "financeiro",
    "segmento": "consolidado",
    "tipo_periodo": "trimestre",
    "ajustado_ou_reportado": "ajustado",
    "unidade": "R$ milhões",
    "valor_original": "R$717,6 milhões",
    "valor_normalizado": 717.6,
    "pagina": 1,
    "trecho_fonte": "o EBITDA ajustado totalizou R$717,6 milhões, com uma margem de 7,8%",
    "confianca": "alta",
}


def test_carrega_lista_de_indicadores_validos(tmp_path):
    caminho = tmp_path / "magalu-2026-q1.indicators.json"
    caminho.write_text(json.dumps([INDICADOR_VALIDO]), encoding="utf-8")

    indicadores = carregar_indicadores(caminho)

    assert len(indicadores) == 1
    assert indicadores[0].indicador == "EBITDA Ajustado"
    assert indicadores[0].valor_normalizado == 717.6


def test_rejeita_indicador_com_categoria_invalida_apontando_o_indice(tmp_path):
    invalido = {**INDICADOR_VALIDO, "categoria": "receita"}
    caminho = tmp_path / "magalu-2026-q1.indicators.json"
    caminho.write_text(json.dumps([INDICADOR_VALIDO, invalido]), encoding="utf-8")

    with pytest.raises(IndicadoresInvalidosError, match=r"\[1\]"):
        carregar_indicadores(caminho)
