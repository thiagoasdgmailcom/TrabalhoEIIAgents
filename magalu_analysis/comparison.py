from .models import ComparacaoItem, Confianca, Indicador


def construir_periodo_label(ano: int, trimestre: int) -> str:
    return f"{trimestre}T{ano % 100:02d}"


def comparar_indicadores(
    indicadores: list[Indicador], periodos_por_documento: dict[str, tuple[int, int]]
) -> list[ComparacaoItem]:
    periodos_ordenados = sorted(set(periodos_por_documento.values()))
    labels_ordenados = [construir_periodo_label(ano, trimestre) for ano, trimestre in periodos_ordenados]

    chaves_ordenadas: list[tuple] = []
    valor_por_chave_periodo: dict[tuple, float | None] = {}
    confianca_por_chave_periodo: dict[tuple, Confianca] = {}

    for indicador in indicadores:
        chave = (
            indicador.indicador,
            indicador.categoria,
            indicador.segmento,
            indicador.tipo_periodo,
            indicador.ajustado_ou_reportado,
            indicador.unidade,
        )
        if chave not in chaves_ordenadas:
            chaves_ordenadas.append(chave)

        ano, trimestre = periodos_por_documento[indicador.documento_id]
        label = construir_periodo_label(ano, trimestre)
        valor_por_chave_periodo[(chave, label)] = indicador.valor_normalizado
        confianca_por_chave_periodo[(chave, label)] = indicador.confianca

    itens = []
    for chave in chaves_ordenadas:
        nome, categoria, segmento, tipo_periodo, ajustado_ou_reportado, unidade = chave

        valores_por_periodo = {
            label: valor_por_chave_periodo.get((chave, label)) for label in labels_ordenados
        }
        confiancas_por_periodo = {
            label: confianca_por_chave_periodo.get((chave, label)) for label in labels_ordenados
        }

        variacao_absoluta: dict[str, float | None] = {}
        variacao_percentual_ou_pp: dict[str, float | None] = {}

        for anterior, atual in zip(labels_ordenados, labels_ordenados[1:]):
            chave_variacao = f"{anterior}_para_{atual}"
            valor_anterior = valores_por_periodo[anterior]
            valor_atual = valores_por_periodo[atual]
            confianca_baixa = Confianca.BAIXA in (
                confiancas_por_periodo[anterior],
                confiancas_por_periodo[atual],
            )

            if valor_anterior is None or valor_atual is None or confianca_baixa:
                variacao_absoluta[chave_variacao] = None
                variacao_percentual_ou_pp[chave_variacao] = None
                continue

            variacao_absoluta[chave_variacao] = round(valor_atual - valor_anterior, 6)

            if unidade == "%":
                variacao_percentual_ou_pp[chave_variacao] = round(valor_atual - valor_anterior, 6)
            elif valor_anterior == 0:
                variacao_percentual_ou_pp[chave_variacao] = None
            else:
                variacao_percentual_ou_pp[chave_variacao] = round(
                    (valor_atual - valor_anterior) / abs(valor_anterior) * 100, 4
                )

        itens.append(
            ComparacaoItem(
                indicador=nome,
                categoria=categoria,
                segmento=segmento,
                tipo_periodo=tipo_periodo,
                ajustado_ou_reportado=ajustado_ou_reportado,
                unidade=unidade,
                valores_por_periodo=valores_por_periodo,
                variacao_absoluta=variacao_absoluta,
                variacao_percentual_ou_pp=variacao_percentual_ou_pp,
            )
        )

    return itens
