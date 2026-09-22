from .discovery import DocumentoBruto


def ordenar_por_periodo_fiscal(documentos: list[DocumentoBruto]) -> list[DocumentoBruto]:
    return sorted(documentos, key=lambda d: (d.ano, d.trimestre), reverse=True)


def selecionar_mais_recentes(documentos: list[DocumentoBruto], n: int) -> list[DocumentoBruto]:
    return ordenar_por_periodo_fiscal(documentos)[:n]
