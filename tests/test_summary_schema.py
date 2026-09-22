import pytest

from magalu_analysis.summary_schema import ResumoInvalidoError, validar_linguagem_resumo


def test_aceita_resumo_factual_sem_linguagem_de_recomendacao():
    texto = (
        "A Receita Líquida caiu de R$11.153,1 milhões no 4T25 para R$8.898,7 milhões no 2T26, "
        "uma redução de 20,2%. O EBITDA Ajustado passou de R$867,3 milhões para R$708,8 milhões no mesmo período."
    )

    validar_linguagem_resumo(texto)


@pytest.mark.parametrize(
    "trecho",
    [
        "recomendamos a compra das ações",
        "é um bom momento para investir no papel",
        "sugerimos manter a posição na ação MGLU3",
        "recomendação de venda para os próximos meses",
    ],
)
def test_rejeita_linguagem_de_recomendacao_de_investimento(trecho):
    with pytest.raises(ResumoInvalidoError):
        validar_linguagem_resumo(f"Prefácio. {trecho}. Conclusão.")
