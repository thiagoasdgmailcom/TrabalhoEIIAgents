import pytest
from pydantic import ValidationError

from magalu_analysis.models import (
    ComparacaoItem,
    Documento,
    Indicador,
    PaginaTexto,
    Pendencia,
    ResultadoAuditoria,
    RunManifest,
)


def test_documento_valido_e_aceito_com_todos_os_campos():
    documento = Documento(
        documento_id="magalu-2024-q3",
        nome_arquivo="release_3T24.pdf",
        url_origem="https://ri.magazineluiza.com.br/release_3T24.pdf",
        ano=2024,
        trimestre=3,
        data_download="2026-09-17",
        num_paginas=20,
        sha256="a" * 64,
    )

    assert documento.documento_id == "magalu-2024-q3"
    assert documento.ano == 2024
    assert documento.trimestre == 3


def test_indicador_aceita_valor_ausente_como_null():
    indicador = Indicador(
        documento_id="magalu-2024-q3",
        indicador="EBITDA Ajustado",
        categoria="financeiro",
        segmento=None,
        tipo_periodo="trimestre",
        ajustado_ou_reportado="ajustado",
        unidade=None,
        valor_original=None,
        valor_normalizado=None,
        pagina=5,
        trecho_fonte="não encontrado neste documento",
        confianca="baixa",
    )

    assert indicador.valor_original is None
    assert indicador.valor_normalizado is None


def test_indicador_rejeita_categoria_fora_do_vocabulario_controlado():
    with pytest.raises(ValidationError):
        Indicador(
            documento_id="magalu-2024-q3",
            indicador="Receita Líquida",
            categoria="receita",
            tipo_periodo="trimestre",
            pagina=5,
            trecho_fonte="Receita Líquida de R$ 1.000 milhões",
            confianca="alta",
        )


def test_indicador_rejeita_confianca_fora_do_vocabulario_controlado():
    with pytest.raises(ValidationError):
        Indicador(
            documento_id="magalu-2024-q3",
            indicador="Receita Líquida",
            categoria="financeiro",
            tipo_periodo="trimestre",
            pagina=5,
            trecho_fonte="Receita Líquida de R$ 1.000 milhões",
            confianca="altíssima",
        )


def test_documento_rejeita_trimestre_fora_de_1_a_4():
    with pytest.raises(ValidationError):
        Documento(
            documento_id="magalu-2024-q5",
            nome_arquivo="release.pdf",
            url_origem="https://ri.magazineluiza.com.br/release.pdf",
            ano=2024,
            trimestre=5,
        )


def test_pagina_texto_valida_e_aceita():
    pagina = PaginaTexto(documento_id="magalu-2024-q3", numero_pagina=1, texto="conteúdo da página")

    assert pagina.numero_pagina == 1
    assert pagina.texto == "conteúdo da página"


def test_pendencia_rejeita_tipo_gatilho_fora_da_lista_da_skill():
    with pytest.raises(ValidationError):
        Pendencia(
            tipo_gatilho="motivo_inventado",
            descricao="algo não previsto pela skill",
            acao_sugerida="revisar manualmente",
        )


def test_pendencia_valida_aceita_gatilho_da_lista_da_skill():
    pendencia = Pendencia(
        tipo_gatilho="confianca_baixa",
        descricao="valor de EBITDA ajustado ilegível na tabela",
        documento_id="magalu-2024-q3",
        pagina=5,
        indicador_relacionado="EBITDA Ajustado",
        trecho_fonte="tabela com células mescladas",
        acao_sugerida="conferir manualmente contra o PDF original",
    )

    assert pendencia.tipo_gatilho == "confianca_baixa"


def test_comparacao_item_aceita_periodo_ausente_como_null():
    item = ComparacaoItem(
        indicador="Receita Líquida",
        categoria="financeiro",
        tipo_periodo="trimestre",
        valores_por_periodo={"2023-Q3": 1000.0, "2024-Q3": None},
        variacao_absoluta={"2023-Q3_para_2024-Q3": None},
        variacao_percentual_ou_pp={"2023-Q3_para_2024-Q3": None},
    )

    assert item.valores_por_periodo["2024-Q3"] is None


def test_run_manifest_aceita_lista_vazia_de_documentos():
    manifest = RunManifest(
        run_id="run-0001",
        empresa="Magazine Luiza",
        n_releases=3,
        periodos_selecionados=[],
        data_execucao="2026-09-17T10:00:00",
        documentos=[],
    )

    assert manifest.documentos == []


def test_resultado_auditoria_aceita_valores_do_vocabulario_controlado():
    resultado = ResultadoAuditoria(
        item_verificado="todo valor do Comparativo tem evidência",
        resultado="ok",
        detalhe="todas as 12 linhas do Comparativo têm evidência correspondente",
        regra_aplicada="planilha-excel.md#auditoria",
        timestamp="2026-09-17T10:00:00",
    )

    assert resultado.resultado == "ok"


def test_resultado_auditoria_rejeita_resultado_fora_do_vocabulario_controlado():
    with pytest.raises(ValidationError):
        ResultadoAuditoria(
            item_verificado="todo valor do Comparativo tem evidência",
            resultado="parcial",
            detalhe="algumas linhas sem evidência",
            regra_aplicada="planilha-excel.md#auditoria",
            timestamp="2026-09-17T10:00:00",
        )
