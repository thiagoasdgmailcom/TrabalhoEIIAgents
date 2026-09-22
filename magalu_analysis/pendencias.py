import json
from pathlib import Path

from .models import Pendencia


def carregar_pendencias(caminho: Path) -> list[Pendencia]:
    if not caminho.exists():
        return []
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    return [Pendencia(**item) for item in dados]


def consolidar_pendencias(*listas: list[Pendencia]) -> list[Pendencia]:
    consolidado: list[Pendencia] = []
    for lista in listas:
        consolidado.extend(lista)
    return consolidado
