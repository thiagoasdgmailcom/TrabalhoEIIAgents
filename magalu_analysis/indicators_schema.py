import json
from pathlib import Path

from pydantic import ValidationError

from .models import Indicador


class IndicadoresInvalidosError(Exception):
    pass


def carregar_indicadores(caminho: Path) -> list[Indicador]:
    dados_brutos = json.loads(caminho.read_text(encoding="utf-8"))
    indicadores = []
    for indice, item in enumerate(dados_brutos):
        try:
            indicadores.append(Indicador(**item))
        except ValidationError as erro:
            raise IndicadoresInvalidosError(f"{caminho.name}[{indice}]: {erro}") from erro
    return indicadores
