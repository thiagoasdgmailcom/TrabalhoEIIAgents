---
name: magalu-release-analysis
description: Conhecimento de domínio e procedimento operacional para analisar releases de resultados trimestrais da Magazine Luiza obtidos na Central de Resultados oficial — identificação e ordenação por período fiscal, extração de indicadores financeiros e operacionais com evidência rastreável (documento, página, trecho-fonte), comparação entre N períodos e geração de resumo executivo e planilha Excel. Use esta skill sempre que a tarefa envolver analisar, comparar ou resumir releases/resultados trimestrais da Magalu ou Magazine Luiza — mesmo que o pedido seja apenas "analise os N releases mais recentes", sem citar indicadores, Excel ou evidências explicitamente.
---

# Análise de Releases de Resultados da Magazine Luiza

## Quando usar esta skill

Use sempre que a tarefa for analisar, comparar ou resumir releases de resultados trimestrais da Magazine Luiza vindos da Central de Resultados oficial — inclusive quando o pedido for apenas "analise os N releases mais recentes", sem detalhar indicadores, evidências ou formato de saída. Esta skill é a referência obrigatória para qualquer tarefa do projeto relacionada a essa análise (ver CLAUDE.md do repositório).

Esta skill contém conhecimento de domínio e o procedimento operacional da análise. Ela não implementa o pipeline em Python — a implementação determinística (download, parsing de PDF, geração do Excel etc.) vive no código do projeto e deve seguir as regras descritas aqui.

## Por que a disciplina de evidências importa

Um release de resultados mistura números tabulados, texto narrativo, valores ajustados e reportados, e variações entre trimestre isolado e acumulado. É fácil confundir essas coisas — e um número financeiro sem evidência anexada não é verificável nem confiável. Por isso, cada valor extraído carrega sua origem exata, e cada dúvida vira uma pendência explícita em vez de ser resolvida por adivinhação.

## Procedimento operacional

1. **Confirmar a fonte.** Use somente documentos já baixados ou baixados da Central de Resultados oficial da Magazine Luiza. Nunca complemente com conhecimento externo (memória do modelo, notícias, relatórios de terceiros).
2. **Filtrar apenas releases de resultados.** A Central de Resultados lista tipos variados de documento (apresentações, formulários, atas). Mantenha somente os releases de resultados trimestrais.
3. **Interpretar ano e trimestre.** Releases nomeiam o período de formas diferentes ("3T24", "Terceiro Trimestre de 2024", "Resultados do 3º trimestre de 2024"). Normalize para (ano, trimestre) antes de ordenar.
4. **Ordenar cronologicamente e selecionar os N mais recentes.** A ordenação é sempre por período fiscal (ano, trimestre), nunca pela data de publicação do arquivo, que pode divergir.
5. **Extrair o texto preservando documento e página.** Todo trecho ou tabela usado depois precisa apontar de volta para o documento e a página exatos.
6. **Identificar indicadores.** Use `references/indicadores.md` como ponto de partida — é um conjunto inicial, não uma lista fechada. Registre indicadores relevantes fora da lista como pendência em vez de descartá-los.
7. **Aplicar as regras de interpretação e os gatilhos de revisão humana.** Descritos em `references/regras-interpretacao.md`. Nenhum valor é inventado, estimado ou completado por inferência.
8. **Comparar os períodos.** Regras completas em `references/comparacao.md` — cobre variação absoluta/percentual, pontos percentuais, e quando não calcular uma variação.
9. **Redigir o resumo executivo.** Ver seção abaixo.
10. **Montar a planilha Excel.** Estrutura das 6 abas em `references/planilha-excel.md`. Construa e valide o arquivo usando a skill de planilhas do ambiente (`document-skills:xlsx`) — não escreva scripts de geração de Excel dentro desta skill.
11. **Registrar pendências.** Todo item que caiu em um gatilho de revisão humana vai para a aba "Pendências", com contexto suficiente para um humano decidir sem reabrir o PDF.
12. **Auditar antes de concluir.** Antes de entregar o resultado, revise: todo valor na aba "Comparativo"/"Resumo" tem uma linha correspondente em "Evidências"? Alguma comparação mistura métricas incompatíveis? O resumo executivo contém, mesmo indiretamente, linguagem de recomendação de investimento? Registre o resultado dessa checagem na aba "Auditoria".

## Regras inegociáveis (resumo)

- Use somente os documentos fornecidos ou baixados da fonte oficial — nunca conhecimento externo.
- Nunca invente, estime ou complete valores ausentes por inferência.
- Use `null` para informação não encontrada.
- Preserve o valor exatamente como aparece no documento; gere o valor normalizado apenas quando a unidade for inequívoca.
- Mantenha métricas diferentes em séries separadas; nunca force comparação entre conceitos incompatíveis.
- Nunca use linguagem que soe como recomendação de compra, venda ou manutenção de ações — nem no resumo executivo, nem nas observações da planilha.

Detalhamento completo dessas regras e dos gatilhos de revisão humana: `references/regras-interpretacao.md`.

## Resumo executivo

O resumo deve ser factual, comparativo e ancorado nas evidências extraídas — cada afirmação deve ser rastreável até um valor com evidência, não uma impressão geral. Evite adjetivação promocional ("resultado espetacular", "crescimento robusto") e qualquer formulação que possa ser lida como recomendação sobre comprar, vender ou manter ações, mesmo de forma indireta (ex.: "isso sinaliza um bom momento para investir").

## Referências

- `references/indicadores.md` — conjunto inicial de indicadores financeiros e operacionais, com sinônimos comuns encontrados nos releases e unidades esperadas.
- `references/regras-interpretacao.md` — regras de interpretação, distinções obrigatórias (ajustado/reportado, trimestre/acumulado/anual, absoluto/percentual/variação, consolidado/lojas físicas/e-commerce/marketplace/1P/3P) e gatilhos de revisão humana.
- `references/comparacao.md` — regras de comparação entre N períodos.
- `references/planilha-excel.md` — estrutura das 6 abas do Excel final.
