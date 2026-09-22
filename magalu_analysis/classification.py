from .discovery import DocumentoBruto


def filtrar_releases_resultados(documentos: list[DocumentoBruto]) -> list[DocumentoBruto]:
    return [d for d in documentos if d.tipo_documento == "release"]
