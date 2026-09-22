TERMOS_PROIBIDOS = [
    "recomendamos a compra",
    "recomendamos a venda",
    "recomendação de compra",
    "recomendação de venda",
    "recomendamos manter",
    "bom momento para investir",
    "vale a pena investir",
    "oportunidade de compra",
    "manter a posição",
    "preço-alvo",
    "target price",
]


class ResumoInvalidoError(Exception):
    pass


def validar_linguagem_resumo(texto: str) -> None:
    texto_normalizado = texto.lower()
    for termo in TERMOS_PROIBIDOS:
        if termo in texto_normalizado:
            raise ResumoInvalidoError(
                f"Linguagem de recomendação de investimento detectada: '{termo}'"
            )
