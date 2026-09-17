# Regras de Interpretação e Revisão Humana

## Por que essas regras existem

Um release de resultados é redigido para contar uma história favorável à empresa. A tarefa aqui é extrair o que está escrito, não reconstruir o que "provavelmente" está por trás de uma lacuna. Qualquer valor inventado, estimado ou inferido — mesmo que pareça óbvio — compromete a confiabilidade de toda a análise.

## Regras de extração

- Use somente os documentos fornecidos ou baixados da fonte oficial. Nunca recorra a conhecimento externo (memória do modelo, notícias, consenso de mercado, relatórios de terceiros) para preencher ou corrigir um valor.
- Nunca invente, estime ou complete um valor ausente por inferência — mesmo quando o contexto sugere fortemente qual seria o número.
- Use `null` quando a informação não for encontrada no documento.
- Preserve o valor exatamente como aparece (mesma grafia, mesma casa decimal, mesmo sinal) antes de qualquer normalização.
- Gere o valor normalizado apenas quando a unidade estiver inequivocamente clara. Se houver dúvida sobre a unidade (ex.: milhares vs. milhões, R$ vs. %), preserve o valor original, deixe o normalizado como `null` e acione revisão humana.
- Mantenha métricas diferentes em séries separadas. Não junte, por exemplo, EBITDA ajustado e EBITDA reportado na mesma série só porque medem "a mesma coisa" — são conceitos distintos que o próprio release trata separadamente.
- Não force uma comparação quando os conceitos forem incompatíveis (ex.: comparar GMV de um trimestre com Receita Líquida de outro, ou um valor trimestral com um acumulado).

## Distinções obrigatórias

Ao registrar qualquer valor, identifique explicitamente:

- **Ajustado vs. reportado** — releases frequentemente mostram as duas versões lado a lado (ex.: EBITDA/Lucro Líquido ajustado por itens não recorrentes vs. o valor contábil reportado).
- **Trimestre isolado vs. acumulado vs. anual** — o mesmo indicador pode aparecer nas três formas no mesmo documento.
- **Valor absoluto vs. percentual vs. variação** — não confunda uma margem (%) com uma variação percentual (também %); são grandezas diferentes.
- **Segmento** — consolidado, lojas físicas, e-commerce, marketplace, 1P, 3P. Um "GMV" sem segmento declarado é ambíguo — sinalize se não estiver claro qual escopo o número cobre.

## Gatilhos de revisão humana

Qualquer uma das situações abaixo gera uma entrada na aba "Pendências" — não impede o restante da análise, mas impede que aquele valor específico seja tratado como definitivo:

- confiança baixa na leitura do valor ou do rótulo;
- conflito entre duas fontes do mesmo indicador (ex.: texto narrativo diz um número, tabela diz outro);
- ambiguidade sobre o que o número representa;
- unidade não clara (moeda, escala, %, pontos percentuais);
- tabela que perdeu estrutura na extração (colunas desalinhadas, células mescladas mal interpretadas);
- dúvida entre ajustado e reportado;
- dúvida entre trimestre e acumulado;
- diferença entre o valor narrativo (texto corrido) e o valor tabulado;
- uma conclusão qualitativa forte no resumo dependeria de interpretação subjetiva do analista;
- risco de a linguagem do resumo ou de uma observação parecer recomendação de investimento.

Para cada pendência, registre: o que gerou a dúvida, o trecho-fonte, o documento e página, e o indicador relacionado — o suficiente para um humano decidir sem precisar reabrir o PDF do zero.
