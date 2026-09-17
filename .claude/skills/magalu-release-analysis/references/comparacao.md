# Regras de Comparação entre Períodos

Aplicável para qualquer quantidade N de períodos (não assuma N=2).

## Ordenação e ausências

- Ordene os períodos em ordem cronológica crescente (do mais antigo para o mais recente) antes de montar qualquer série comparativa.
- Se um indicador não existir em um dos períodos, represente o período como `null` na série — não interpole, não repita o valor anterior.

## Como calcular variações

- Preserve o valor original e a evidência de cada ponto da série, mesmo depois de calculada a variação.
- Valores monetários e quantidades: calcule variação absoluta (diferença) e variação percentual.
- Margens e outros percentuais: calcule variação em **pontos percentuais**, nunca "variação percentual de um percentual" (ex.: margem de 20% para 22% é "+2 p.p.", não "+10%").
- Não calcule variação percentual quando o valor do período anterior for zero (divisão por zero não tem leitura financeira válida) — registre a variação absoluta e marque a variação percentual como `null` com uma observação.
- Não calcule variação nenhuma quando a confiança de um dos dois valores envolvidos for baixa — registre os valores individualmente e sinalize a comparação como pendente em vez de publicar uma variação sobre um número não confiável.
- Valores textuais/qualitativos (ex.: comentários de guidance, mudanças de estratégia) devem ser comparados apenas qualitativamente — nunca transformados em uma variação numérica artificial.
- Nunca misture métricas incompatíveis na mesma série (ajustado com reportado, trimestre com acumulado, segmentos diferentes) — cada combinação de (indicador, segmento, tipo de período, ajustado/reportado) tem sua própria série.
