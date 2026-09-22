from pathlib import Path

EMPRESA = "Magazine Luiza"

URL_BASE_RI = "https://ri.magazineluiza.com.br/"
URL_CENTRAL_RESULTADOS = (
    "https://ri.magazineluiza.com.br/ListResultados/Central-de-Resultados"
    "?=0WX0bwP76pYcZvx+vXUnvg=="
)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
)

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
DIRETORIO_RUNS = RAIZ_PROJETO / "data" / "runs"
DIRETORIO_OUTPUT = RAIZ_PROJETO / "output"
