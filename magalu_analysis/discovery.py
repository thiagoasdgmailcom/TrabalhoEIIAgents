import re
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from . import config
from .period_parsing import interpretar_periodo

PADRAO_LINHA_RESULTADO = re.compile(r"rptResultados_ResultadoArq\dTri_\d+")

TIPOS_POR_PREFIXO_ID = {
    "linkArq_Release": "release",
    "linkArq_ITR": "itr_dfp",
    "linkArq_Apresentacao": "apresentacao",
    "linkArq_Audio": "audio",
    "linkArq_Transcricao": "transcricao",
}


@dataclass
class DocumentoBruto:
    tipo_documento: str
    ano: int
    trimestre: int
    url_download: str


def buscar_html_central_resultados(url: str = config.URL_CENTRAL_RESULTADOS) -> str:
    resposta = requests.get(url, headers={"User-Agent": config.USER_AGENT}, timeout=30)
    resposta.raise_for_status()
    return resposta.text


def _identificar_tipo(id_link: str) -> str | None:
    for prefixo, tipo in TIPOS_POR_PREFIXO_ID.items():
        if prefixo in id_link:
            return tipo
    return None


def listar_documentos(html: str) -> list[DocumentoBruto]:
    soup = BeautifulSoup(html, "html.parser")
    documentos: list[DocumentoBruto] = []

    for linha in soup.find_all("tr", id=PADRAO_LINHA_RESULTADO):
        primeira_celula = linha.find("td")
        rotulo = primeira_celula.get_text(strip=True) if primeira_celula else ""
        periodo = interpretar_periodo(rotulo)
        if periodo is None:
            continue
        ano, trimestre = periodo

        for link in linha.find_all("a", id=True):
            href = link.get("href", "")
            if not href or href == "#":
                continue
            tipo = _identificar_tipo(link["id"])
            if tipo is None:
                continue
            documentos.append(
                DocumentoBruto(
                    tipo_documento=tipo,
                    ano=ano,
                    trimestre=trimestre,
                    url_download=urljoin(config.URL_BASE_RI, href),
                )
            )

    return documentos
