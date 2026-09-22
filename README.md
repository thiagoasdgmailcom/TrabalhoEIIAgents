# TrabalhoEIIAgents

Solução para analisar releases de resultados trimestrais da Magazine Luiza a partir de um único parâmetro: a quantidade N de releases mais recentes a analisar (ex.: "Analise os 3 releases mais recentes da Magazine Luiza").

As regras permanentes do projeto estão em [CLAUDE.md](CLAUDE.md) e o conhecimento de domínio / procedimento operacional da análise está na skill [`magalu-release-analysis`](.claude/skills/magalu-release-analysis/SKILL.md). Este README não repete esse conteúdo — apenas explica como rodar o que já existe.

## Ambiente

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Nunca crie outro ambiente virtual; use sempre o `.venv` já existente na raiz do repositório.

## Como funciona

O pipeline alterna entre código Python determinístico e leitura semântica feita pelo Claude Code (guiada pela skill `magalu-release-analysis`). Não há chamada a API de LLM dentro do código Python — a leitura semântica é o próprio Claude Code trabalhando durante a conversa.

```
python -m magalu_analysis fetch --n N
        ↓ (Claude Code lê os .pages.json e escreve <doc>.indicators.json)
python -m magalu_analysis compare --run <run_id>
        ↓ (Claude Code lê comparativo.json e escreve resumo_executivo.md)
python -m magalu_analysis build-excel --run <run_id>
```

### 1. `fetch`

```bash
python -m magalu_analysis fetch --n 3
```

Acessa a Central de Resultados oficial, identifica apenas releases de resultados, interpreta ano/trimestre, ordena por período fiscal, seleciona os N mais recentes, baixa os PDFs (validando que são textuais) e extrai o texto página a página. Grava tudo em `data/runs/<run_id>/` (`manifest.json` + um `<documento_id>.pages.json` por release).

### 2. Extração semântica (Claude Code)

Para cada documento do run, leia o `.pages.json` correspondente e escreva um `<documento_id>.indicators.json` na mesma pasta `documents/`, seguindo o schema de `Indicador` (`magalu_analysis/models.py`) e as regras da skill (nunca inventar valor, usar `null` para ausente, preservar valor original e evidência, distinguir ajustado/reportado, trimestre/acumulado/anual, segmentos etc.).

### 3. `compare`

```bash
python -m magalu_analysis compare --run <run_id>
```

Valida os `.indicators.json` contra o schema, consolida as evidências e calcula a comparação entre os N períodos (variação absoluta/percentual, pontos percentuais para margens, nunca misturando métricas incompatíveis). Grava `comparativo.json` no diretório do run.

### 4. Resumo executivo (Claude Code)

Leia `comparativo.json` e as evidências e escreva `resumo_executivo.md` no diretório do run: factual, comparativo, sem linguagem promocional ou de recomendação de investimento.

### 5. `build-excel`

```bash
python -m magalu_analysis build-excel --run <run_id>
```

Valida a linguagem do resumo, roda a auditoria automática (evidência para todo valor comparado, nenhuma variação % com base zero, nenhuma linguagem de recomendação) mais uma amostragem determinística de indicadores para revisão manual, e monta o Excel final com 6 abas — Resumo, Comparativo, Evidências, Documentos, Pendências, Auditoria — em `output/MagaluResultados_N<N>_<run_id>.xlsx`. Também grava `auditoria.json` no diretório do run.

## Testes

```bash
pytest
```

Nenhum teste acessa a rede real (HTTP é mockado com `requests-mock`); os testes usam fixtures em `tests/fixtures/`, incluindo um PDF textual real e uma cópia real da página da Central de Resultados.
