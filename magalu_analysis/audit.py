import random
from datetime import datetime, timezone

from .models import ComparacaoItem, Indicador, ResultadoAuditoria, ResultadoCheck
from .summary_schema import ResumoInvalidoError, validar_linguagem_resumo


def auditar(
    indicadores: list[Indicador],
    comparativo: list[ComparacaoItem],
    resumo_executivo: str,
) -> list[ResultadoAuditoria]:
    agora = datetime.now(timezone.utc)
    resultados = []

    nomes_com_evidencia = {i.indicador for i in indicadores}
    nomes_sem_evidencia = sorted({c.indicador for c in comparativo if c.indicador not in nomes_com_evidencia})
    resultados.append(
        ResultadoAuditoria(
            item_verificado="Todo indicador do Comparativo possui evidência correspondente",
            resultado=ResultadoCheck.OK if not nomes_sem_evidencia else ResultadoCheck.FALHA,
            detalhe="OK" if not nomes_sem_evidencia else f"Sem evidência: {nomes_sem_evidencia}",
            regra_aplicada="planilha-excel.md#auditoria",
            timestamp=agora,
        )
    )

    problemas_base_zero = []
    for item in comparativo:
        periodos = list(item.valores_por_periodo.items())
        for (label_anterior, valor_anterior), (label_atual, _) in zip(periodos, periodos[1:]):
            chave = f"{label_anterior}_para_{label_atual}"
            if valor_anterior == 0 and item.variacao_percentual_ou_pp.get(chave) is not None:
                problemas_base_zero.append(f"{item.indicador}:{chave}")
    resultados.append(
        ResultadoAuditoria(
            item_verificado="Nenhuma variação percentual calculada com valor anterior igual a zero",
            resultado=ResultadoCheck.OK if not problemas_base_zero else ResultadoCheck.FALHA,
            detalhe="OK" if not problemas_base_zero else str(problemas_base_zero),
            regra_aplicada="comparacao.md",
            timestamp=agora,
        )
    )

    try:
        validar_linguagem_resumo(resumo_executivo)
    except ResumoInvalidoError as erro:
        resultado_linguagem, detalhe_linguagem = ResultadoCheck.FALHA, str(erro)
    else:
        resultado_linguagem, detalhe_linguagem = ResultadoCheck.OK, "Nenhum termo proibido encontrado"
    resultados.append(
        ResultadoAuditoria(
            item_verificado="Resumo executivo não contém linguagem de recomendação de investimento",
            resultado=resultado_linguagem,
            detalhe=detalhe_linguagem,
            regra_aplicada="SKILL.md#resumo-executivo",
            timestamp=agora,
        )
    )

    return resultados


def amostrar_para_revisao_manual(
    indicadores: list[Indicador], tamanho: int = 5, semente: int | None = None
) -> list[Indicador]:
    if len(indicadores) <= tamanho:
        return list(indicadores)
    return random.Random(semente).sample(indicadores, tamanho)
