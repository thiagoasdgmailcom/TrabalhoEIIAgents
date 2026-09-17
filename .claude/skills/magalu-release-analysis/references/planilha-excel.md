# Estrutura da Planilha Excel

Construa e valide o arquivo final usando a skill de planilhas do ambiente (`document-skills:xlsx`) — esta skill não contém scripts de geração de Excel; ela define o que cada aba deve conter.

## 1. Resumo

- Cabeçalho: empresa, períodos analisados (lista), data de geração.
- Tabela dos indicadores-chave por período (uma linha por indicador, uma coluna por período).
- Destaques factuais em bullets, cada um rastreável a uma linha da aba "Evidências" — sem linguagem promocional ou de recomendação.

## 2. Comparativo

Uma linha por combinação (indicador, segmento, tipo de período, ajustado/reportado):

`Indicador | Categoria (financeiro/operacional) | Segmento | Tipo de período | Ajustado/Reportado | Unidade | Valor período 1 ... Valor período N | Variação absoluta | Variação (% ou p.p., conforme o caso) | Observações`

## 3. Evidências

Uma linha por valor extraído:

`Documento | Página | Indicador | Valor original | Valor normalizado | Unidade | Trecho-fonte | Confiança | Ajustado/Reportado | Tipo de período | Segmento`

## 4. Documentos

Uma linha por release usado:

`Nome do documento | Ano | Trimestre | URL de origem | Data de download | Número de páginas`

## 5. Pendências

Uma linha por item sinalizado (ver gatilhos em `regras-interpretacao.md`):

`Descrição do problema | Tipo de gatilho | Documento | Página | Indicador relacionado | Trecho-fonte | Ação sugerida`

## 6. Auditoria

Uma linha por item verificado na checagem final:

`Item verificado | Resultado (OK/Falha/Alerta) | Detalhe | Regra aplicada | Data/hora`

Itens mínimos a auditar antes de concluir: todo valor da aba "Comparativo" tem evidência correspondente; nenhuma comparação mistura métricas incompatíveis; nenhuma variação percentual foi calculada com base zero; nenhuma variação foi calculada sobre um valor de baixa confiança; o resumo executivo não contém linguagem de recomendação de investimento.
