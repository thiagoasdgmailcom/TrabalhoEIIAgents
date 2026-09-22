from datetime import datetime, timezone

from magalu_analysis.excel_builder import construir_workbook
from magalu_analysis.models import (
    ComparacaoItem,
    Documento,
    Indicador,
    Pendencia,
    ResultadoAuditoria,
)

DOCUMENTO = Documento(
    documento_id="magalu-2026-q2",
    nome_arquivo="release_2T26.pdf",
    url_origem="https://x/1.pdf",
    ano=2026,
    trimestre=2,
    data_download="2026-09-18",
    num_paginas=28,
    sha256="a" * 64,
)

INDICADOR = Indicador(
    documento_id="magalu-2026-q2",
    indicador="Receita Líquida",
    categoria="financeiro",
    segmento="consolidado",
    tipo_periodo="trimestre",
    unidade="R$ milhões",
    valor_original="8.898,7",
    valor_normalizado=8898.7,
    pagina=5,
    trecho_fonte="Receita Líquida 8.898,7",
    confianca="alta",
)

COMPARACAO_ITEM = ComparacaoItem(
    indicador="Receita Líquida",
    categoria="financeiro",
    segmento="consolidado",
    tipo_periodo="trimestre",
    unidade="R$ milhões",
    valores_por_periodo={"1T26": 9205.7, "2T26": 8898.7},
    variacao_absoluta={"1T26_para_2T26": -307.0},
    variacao_percentual_ou_pp={"1T26_para_2T26": -3.3349},
)

PENDENCIA = Pendencia(
    tipo_gatilho="narrativa_vs_tabela",
    descricao="Divergência entre destaque e tabela",
    documento_id="magalu-2026-q2",
    pagina=1,
    indicador_relacionado="Fluxo de Caixa Operacional",
    trecho_fonte="trecho",
    acao_sugerida="Confirmar valor oficial",
)

AUDITORIA_ITEM = ResultadoAuditoria(
    item_verificado="Todo indicador do Comparativo possui evidência correspondente",
    resultado="ok",
    detalhe="OK",
    regra_aplicada="planilha-excel.md#auditoria",
    timestamp=datetime.now(timezone.utc),
)


def _construir():
    return construir_workbook(
        empresa="Magazine Luiza",
        periodos_selecionados=["1T26", "2T26"],
        documentos=[DOCUMENTO],
        indicadores=[INDICADOR],
        comparativo=[COMPARACAO_ITEM],
        resumo_executivo="A Receita Líquida caiu 3,3% no trimestre.",
        pendencias=[PENDENCIA],
        auditoria=[AUDITORIA_ITEM],
    )


def test_workbook_tem_as_seis_abas_na_ordem_esperada():
    wb = _construir()

    assert wb.sheetnames == ["Resumo", "Comparativo", "Evidências", "Documentos", "Pendências", "Auditoria"]


def test_aba_resumo_contem_empresa_periodos_e_texto_do_resumo():
    wb = _construir()
    resumo = wb["Resumo"]
    textos = [str(c.value) for row in resumo.iter_rows() for c in row if c.value is not None]

    assert any("Magazine Luiza" in t for t in textos)
    assert any("1T26" in t and "2T26" in t for t in textos)
    assert any("caiu 3,3%" in t for t in textos)


def test_aba_comparativo_tem_cabecalho_e_uma_linha_por_item():
    wb = _construir()
    comparativo = wb["Comparativo"]

    cabecalho = [c.value for c in comparativo[1]]
    assert "Indicador" in cabecalho
    assert "1T26" in cabecalho
    assert "2T26" in cabecalho

    assert comparativo.max_row == 2
    assert comparativo.cell(row=2, column=cabecalho.index("Indicador") + 1).value == "Receita Líquida"


def test_aba_evidencias_tem_uma_linha_por_indicador():
    wb = _construir()
    evidencias = wb["Evidências"]

    assert evidencias.max_row == 2
    cabecalho = [c.value for c in evidencias[1]]
    assert "Documento" in cabecalho
    assert "Trecho-fonte" in cabecalho


def test_aba_documentos_tem_uma_linha_por_documento():
    wb = _construir()
    documentos = wb["Documentos"]

    assert documentos.max_row == 2
    cabecalho = [c.value for c in documentos[1]]
    assert "Nome do documento" in cabecalho


def test_aba_pendencias_tem_uma_linha_por_pendencia():
    wb = _construir()
    pendencias = wb["Pendências"]

    assert pendencias.max_row == 2
    cabecalho = [c.value for c in pendencias[1]]
    assert "Tipo de gatilho" in cabecalho


def test_aba_auditoria_tem_uma_linha_por_item_verificado():
    wb = _construir()
    auditoria = wb["Auditoria"]

    assert auditoria.max_row == 2
    cabecalho = [c.value for c in auditoria[1]]
    assert "Resultado" in cabecalho
