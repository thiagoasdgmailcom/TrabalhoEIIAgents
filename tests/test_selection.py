from magalu_analysis.discovery import DocumentoBruto
from magalu_analysis.selection import ordenar_por_periodo_fiscal, selecionar_mais_recentes


def _doc(ano, trimestre):
    return DocumentoBruto(tipo_documento="release", ano=ano, trimestre=trimestre, url_download=f"https://x/{ano}-{trimestre}")


def test_ordena_do_periodo_mais_recente_para_o_mais_antigo():
    documentos = [_doc(2024, 3), _doc(2026, 1), _doc(2025, 4)]

    ordenados = ordenar_por_periodo_fiscal(documentos)

    assert [(d.ano, d.trimestre) for d in ordenados] == [(2026, 1), (2025, 4), (2024, 3)]


def test_ordena_por_periodo_fiscal_nao_por_ordem_de_insercao():
    documentos = [_doc(2025, 1), _doc(2025, 4), _doc(2025, 2), _doc(2025, 3)]

    ordenados = ordenar_por_periodo_fiscal(documentos)

    assert [d.trimestre for d in ordenados] == [4, 3, 2, 1]


def test_seleciona_exatamente_os_n_mais_recentes():
    documentos = [_doc(2024, 3), _doc(2026, 1), _doc(2025, 4), _doc(2025, 2)]

    selecionados = selecionar_mais_recentes(documentos, 2)

    assert [(d.ano, d.trimestre) for d in selecionados] == [(2026, 1), (2025, 4)]


def test_seleciona_todos_disponiveis_quando_n_maior_que_o_disponivel():
    documentos = [_doc(2026, 1), _doc(2025, 4)]

    selecionados = selecionar_mais_recentes(documentos, 5)

    assert len(selecionados) == 2
