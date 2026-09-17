# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Objetivo do projeto

Desenvolver uma solução para analisar releases de resultados da Magazine Luiza. A entrada principal da solução é a quantidade de releases a serem analisados (N). A partir dela, a solução deve identificar, baixar e interpretar os N releases mais recentes, comparar os períodos analisados e produzir um resumo executivo e uma planilha Excel com os indicadores financeiros e operacionais relevantes, com evidências rastreáveis para cada valor utilizado.

## Escopo

Escopo desta primeira versão:

- Empresa fixa: Magazine Luiza.
- Fonte fixa: Central de Resultados oficial da Magazine Luiza.
- Quantidade de releases configurável (N), sem alteração manual de código para diferentes valores de N.
- Apenas releases de resultados — outros tipos de documento da Central de Resultados devem ser identificados e descartados.
- Apenas PDFs textuais. Sem OCR.
- Sem banco de dados.
- Sem aplicação web.
- Sem chamadas a APIs de LLM dentro do código Python.
- Sem recomendação de compra, venda ou manutenção de investimentos.

## Ambiente do projeto

- Python 3.12.
- Usar exclusivamente o ambiente virtual já existente em `.venv` na raiz do repositório (`source .venv/bin/activate`). Nunca criar outro ambiente virtual.
- `requirements.txt` deve ser gerado ao final, contendo somente as dependências efetivamente utilizadas pelo código.

## Processo de trabalho do agente

- Antes de implementar qualquer tarefa relevante, analisar o objetivo da tarefa e apresentar um plano ao usuário.
- Não iniciar a implementação antes da aprovação explícita do plano.
- Após a aprovação, executar o plano de forma autônoma.
- Seguir Test-Driven Development (TDD) durante toda a implementação.

## Uso das skills

- Usar a skill `using-superpowers` para checar e acionar skills aplicáveis antes de qualquer ação de desenvolvimento.
- A análise dos releases do Magalu é guiada por uma skill específica do projeto, criada com `skill-creator`. Essa skill concentra o procedimento detalhado do pipeline (acesso à Central de Resultados, seleção de releases, extração, indicadores, comparação, geração de resumo e planilha, evidências, auditoria) e deve ser usada como referência para qualquer tarefa relacionada a essa análise. Este arquivo não repete esse procedimento.

## Regras de engenharia

- Etapas determinísticas do pipeline são implementadas em código Python.
- Toda implementação é acompanhada de testes automatizados, seguindo TDD.
- `requirements.txt` é gerado a partir das dependências realmente usadas, não mantido manualmente de forma antecipada.

## Confiabilidade dos dados

- Nunca inventar, estimar ou completar valores sem evidência.
- Usar `null` para representar dados ausentes.
- Preservar o valor original e o valor normalizado de cada indicador.
- Preservar, para cada valor: documento de origem, período, página, trecho-fonte, unidade e nível de confiança.
- Distinguir valores ajustados de valores reportados.
- Distinguir trimestre isolado, acumulado e anual.
- Distinguir valores absolutos, percentuais e variações.
- Distinguir consolidado, lojas físicas, e-commerce, marketplace, 1P e 3P.
- Sinalizar conflitos, ambiguidades e valores de baixa confiança em vez de resolvê-los silenciosamente.

## Validação

- Registrar dados ausentes, ambiguidades e itens que exigem revisão humana.
- Auditar os resultados da análise antes de concluir qualquer execução.

## Versionamento

- O repositório é versionado com Git (branch principal: `main`).
- Alterações nas regras permanentes deste CLAUDE.md exigem solicitação e aprovação explícitas do usuário antes de serem aplicadas.
- O `requirements.txt` é atualizado para refletir as dependências vigentes ao final de cada tarefa aprovada que as alterar.
