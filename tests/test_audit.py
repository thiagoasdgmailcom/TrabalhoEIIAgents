from magalu_analysis.audit import amostrar_para_revisao_manual, auditar
from magalu_analysis.models import ComparacaoItem, Indicador, ResultadoCheck


def _indicador(nome="Receita Líquida", confianca="alta"):
    return Indicador(
        documento_id="doc-1",
        indicador=nome,
        categoria="financeiro",
        segmento="consolidado",
        tipo_periodo="trimestre",
        unidade="R$ milhões",
        valor_original="1.000,0",
        valor_normalizado=1000.0,
        pagina=1,
        trecho_fonte="trecho",
        confianca=confianca,
    )


def _comparacao_item(nome="Receita Líquida"):
    return ComparacaoItem(
        indicador=nome,
        categoria="financeiro",
        segmento="consolidado",
        tipo_periodo="trimestre",
        unidade="R$ milhões",
        valores_por_periodo={"1T26": 1000.0, "2T26": 900.0},
        variacao_absoluta={"1T26_para_2T26": -100.0},
        variacao_percentual_ou_pp={"1T26_para_2T26": -10.0},
    )


def _resultado(resultados, item_verificado):
    return next(r for r in resultados if r.item_verificado == item_verificado)


def test_auditoria_ok_quando_todo_indicador_do_comparativo_tem_evidencia():
    resultados = auditar(
        indicadores=[_indicador("Receita Líquida")],
        comparativo=[_comparacao_item("Receita Líquida")],
        resumo_executivo="A Receita Líquida caiu 10% no trimestre.",
    )

    resultado = _resultado(resultados, "Todo indicador do Comparativo possui evidência correspondente")
    assert resultado.resultado == ResultadoCheck.OK


def test_auditoria_falha_quando_falta_evidencia_para_indicador_do_comparativo():
    resultados = auditar(
        indicadores=[_indicador("EBITDA")],
        comparativo=[_comparacao_item("Receita Líquida")],
        resumo_executivo="Texto qualquer.",
    )

    resultado = _resultado(resultados, "Todo indicador do Comparativo possui evidência correspondente")
    assert resultado.resultado == ResultadoCheck.FALHA
    assert "Receita Líquida" in resultado.detalhe


def test_auditoria_falha_quando_resumo_contem_linguagem_de_recomendacao():
    resultados = auditar(
        indicadores=[_indicador("Receita Líquida")],
        comparativo=[_comparacao_item("Receita Líquida")],
        resumo_executivo="Recomendamos a compra das ações da Companhia.",
    )

    resultado = _resultado(resultados, "Resumo executivo não contém linguagem de recomendação de investimento")
    assert resultado.resultado == ResultadoCheck.FALHA


def test_amostrar_retorna_tamanho_solicitado_quando_ha_mais_indicadores():
    indicadores = [_indicador(f"Indicador {i}") for i in range(10)]

    amostra = amostrar_para_revisao_manual(indicadores, tamanho=3, semente=42)

    assert len(amostra) == 3


def test_amostrar_retorna_todos_quando_ha_menos_indicadores_que_o_tamanho():
    indicadores = [_indicador(f"Indicador {i}") for i in range(2)]

    amostra = amostrar_para_revisao_manual(indicadores, tamanho=5, semente=42)

    assert len(amostra) == 2


def test_amostrar_e_deterministico_com_a_mesma_semente():
    indicadores = [_indicador(f"Indicador {i}") for i in range(10)]

    amostra1 = amostrar_para_revisao_manual(indicadores, tamanho=3, semente=42)
    amostra2 = amostrar_para_revisao_manual(indicadores, tamanho=3, semente=42)

    assert [i.indicador for i in amostra1] == [i.indicador for i in amostra2]
