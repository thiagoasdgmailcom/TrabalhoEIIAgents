from pathlib import Path

from .indicators_schema import carregar_indicadores
from .models import Indicador, RunManifest


class IndicadoresAusentesError(Exception):
    pass


def carregar_manifest(caminho_run: Path) -> RunManifest:
    return RunManifest.model_validate_json((caminho_run / "manifest.json").read_text(encoding="utf-8"))


def consolidar_indicadores_do_run(caminho_run: Path) -> list[Indicador]:
    manifest = carregar_manifest(caminho_run)
    todos: list[Indicador] = []
    for documento in manifest.documentos:
        caminho_indicadores = caminho_run / "documents" / f"{documento.documento_id}.indicators.json"
        if not caminho_indicadores.exists():
            raise IndicadoresAusentesError(
                f"Faltam indicadores extraídos para {documento.documento_id} ({caminho_indicadores})"
            )
        todos.extend(carregar_indicadores(caminho_indicadores))
    return todos
