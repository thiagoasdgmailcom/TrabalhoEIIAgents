import re

PADRAO_TRIMESTRE_ANO_CURTO = re.compile(r"^([1-4])T(\d{2})$")


def interpretar_periodo(rotulo: str) -> tuple[int, int] | None:
    match = PADRAO_TRIMESTRE_ANO_CURTO.match(rotulo.strip())
    if not match:
        return None
    trimestre = int(match.group(1))
    ano = 2000 + int(match.group(2))
    return (ano, trimestre)
