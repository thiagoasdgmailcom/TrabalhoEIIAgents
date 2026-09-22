from magalu_analysis.comparison import comparar_indicadores
from magalu_analysis.models import Indicador


def _ind(documento_id, indicador, valor_normalizado, unidade="R$ milhões", confianca="alta", categoria="financeiro", tipo_periodo="trimestre", ajustado_ou_reportado=None, segmento="consolidado"):
    return Indicador(
        documento_id=documento_id,
        indicador=indicador,
        categoria=categoria,
        segmento=segmento,
        tipo_periodo=tipo_periodo,
        ajustado_ou_reportado=ajustado_ou_reportado,
        unidade=unidade,
        valor_original=str(valor_normalizado),
        valor_normalizado=valor_normalizado,
        pagina=1,
        trecho_fonte="trecho",
        confianca=confianca,
    )


PERIODOS = {"doc-2026-q2": (2026, 2), "doc-2026-q1": (2026, 1), "doc-2025-q4": (2025, 4)}


def _item(itens, indicador, tipo_periodo="trimestre", ajustado_ou_reportado=None):
    return next(
        i for i in itens
        if i.indicador == indicador and i.tipo_periodo == tipo_periodo and i.ajustado_ou_reportado == ajustado_ou_reportado
    )


def test_ordena_periodos_cronologicamente_e_calcula_variacao_absoluta_e_percentual():
    indicadores = [
        _ind("doc-2026-q2", "Receita Líquida", 8898.7),
        _ind("doc-2026-q1", "Receita Líquida", 9205.7),
        _ind("doc-2025-q4", "Receita Líquida", 11153.1),
    ]

    itens = comparar_indicadores(indicadores, PERIODOS)
    item = _item(itens, "Receita Líquida")

    assert list(item.valores_por_periodo.keys()) == ["4T25", "1T26", "2T26"]
    assert item.variacao_absoluta["1T26_para_2T26"] == round(8898.7 - 9205.7, 6)
    assert item.variacao_percentual_ou_pp["1T26_para_2T26"] == round((8898.7 - 9205.7) / 9205.7 * 100, 4)


def test_margem_usa_variacao_em_pontos_percentuais():
    indicadores = [
        _ind("doc-2026-q2", "Margem Bruta", 30.6, unidade="%"),
        _ind("doc-2026-q1", "Margem Bruta", 30.8, unidade="%"),
    ]

    itens = comparar_indicadores(indicadores, PERIODOS)
    item = _item(itens, "Margem Bruta")

    assert item.variacao_percentual_ou_pp["1T26_para_2T26"] == round(30.6 - 30.8, 4)


def test_periodo_ausente_e_representado_como_null():
    indicadores = [
        _ind("doc-2026-q2", "CAPEX", 155.1),
        _ind("doc-2025-q4", "CAPEX", 244.4),
    ]

    itens = comparar_indicadores(indicadores, PERIODOS)
    item = _item(itens, "CAPEX")

    assert item.valores_por_periodo["1T26"] is None


def test_nao_calcula_variacao_percentual_quando_valor_anterior_e_zero():
    indicadores = [
        _ind("doc-2026-q1", "Lucro Líquido Ajustado", 0.0),
        _ind("doc-2026-q2", "Lucro Líquido Ajustado", -50.4),
    ]

    itens = comparar_indicadores(indicadores, PERIODOS)
    item = _item(itens, "Lucro Líquido Ajustado")

    assert item.variacao_absoluta["1T26_para_2T26"] == round(-50.4 - 0.0, 6)
    assert item.variacao_percentual_ou_pp["1T26_para_2T26"] is None


def test_nao_calcula_variacao_quando_confianca_e_baixa():
    indicadores = [
        _ind("doc-2026-q1", "EBITDA", 685.4, confianca="baixa"),
        _ind("doc-2026-q2", "EBITDA", 675.3, confianca="alta"),
    ]

    itens = comparar_indicadores(indicadores, PERIODOS)
    item = _item(itens, "EBITDA")

    assert item.variacao_absoluta["1T26_para_2T26"] is None
    assert item.variacao_percentual_ou_pp["1T26_para_2T26"] is None


def test_nao_mistura_trimestre_e_acumulado_em_uma_mesma_serie():
    indicadores = [
        _ind("doc-2026-q1", "Receita Líquida", 9205.7, tipo_periodo="trimestre"),
        _ind("doc-2026-q2", "Receita Líquida", 18104.5, tipo_periodo="acumulado"),
    ]

    itens = comparar_indicadores(indicadores, PERIODOS)

    trimestre = _item(itens, "Receita Líquida", tipo_periodo="trimestre")
    acumulado = _item(itens, "Receita Líquida", tipo_periodo="acumulado")

    assert trimestre.valores_por_periodo["2T26"] is None
    assert acumulado.valores_por_periodo["1T26"] is None


def test_nao_mistura_segmentos_diferentes_em_uma_mesma_serie():
    indicadores = [
        _ind("doc-2026-q1", "Crescimento de Vendas", -8.8, unidade="%", segmento="1p"),
        _ind("doc-2026-q2", "Crescimento de Vendas", -12.6, unidade="%", segmento="3p"),
    ]

    itens = comparar_indicadores(indicadores, PERIODOS)

    serie_1p = next(i for i in itens if i.segmento == "1p")
    serie_3p = next(i for i in itens if i.segmento == "3p")

    assert serie_1p.valores_por_periodo["2T26"] is None
    assert serie_3p.valores_por_periodo["1T26"] is None


def test_nao_mistura_ajustado_e_reportado_em_uma_mesma_serie():
    indicadores = [
        _ind("doc-2026-q1", "EBITDA", 685.4, ajustado_ou_reportado="reportado"),
        _ind("doc-2026-q2", "EBITDA", 708.8, ajustado_ou_reportado="ajustado"),
    ]

    itens = comparar_indicadores(indicadores, PERIODOS)

    reportado = _item(itens, "EBITDA", ajustado_ou_reportado="reportado")
    ajustado = _item(itens, "EBITDA", ajustado_ou_reportado="ajustado")

    assert reportado.valores_por_periodo["2T26"] is None
    assert ajustado.valores_por_periodo["1T26"] is None
