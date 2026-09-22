# Análise de Releases de Resultados da Magazine Luiza — Plano de Implementação

> **Nível de detalhe:** este é o plano macro do projeto, aprovado em nível de fase. Cada fase, ao ser iniciada, recebe seu próprio ciclo de "apresentar plano detalhado (TDD passo a passo) → aguardar aprovação → executar", conforme o processo definido em `CLAUDE.md`. Este documento não microgerencia cada função — define objetivo, arquivos, testes e ponto de validação por fase.

**Objetivo:** permitir que o usuário peça, em linguagem natural, "Analise os N releases mais recentes da Magazine Luiza" e receba um resumo executivo + planilha Excel com indicadores comparados, evidências rastreáveis, pendências e auditoria — sem inventar dados e sem recomendação de investimento.

**Arquitetura em uma frase:** um pipeline híbrido em que módulos Python determinísticos cuidam de coleta, extração, cálculo e montagem de artefatos, e o Claude Code (guiado pela skill `magalu-release-analysis`) executa as duas etapas que exigem leitura semântica — extrair indicadores do texto e redigir o resumo executivo — sem nenhuma chamada a API de LLM dentro do código Python.

**Stack:** Python 3.12, `.venv` existente, sem banco de dados, sem aplicação web, artefatos intermediários em JSON/PDF em disco.

**Skill de referência obrigatória:** `.claude/skills/magalu-release-analysis/` (domínio, indicadores, regras de interpretação, comparação, estrutura do Excel, gatilhos de revisão humana).

**Regra de configuração:** o único parâmetro exposto ao usuário final é **N** (quantidade de releases). Qualquer outro valor (tamanho de amostra de auditoria, URL da fonte, caminhos de saída) é constante interna, não um parâmetro de entrada.

---

## Visão geral da arquitetura

O fluxo de uma execução real ("Analise os 3 releases mais recentes") passa por 5 estágios, alternando entre código Python (determinístico, testável) e o próprio Claude Code (semântico, guiado pela skill):

```
[Python] fetch --n N
   descoberta → classificação → período fiscal → ordenação/seleção → download → extração de texto por página
   produz: manifest.json + <doc>.pages.json por documento
        │
        ▼
[Claude Code, guiado pela skill] lê os .pages.json e escreve <doc>.indicators.json
   (extração semântica dos indicadores + evidências — não é código Python)
        │
        ▼
[Python] compare --run <run_id>
   valida os .indicators.json contra o schema, consolida evidências,
   calcula comparação entre os N períodos
   produz: comparativo.json + pendências parciais
        │
        ▼
[Claude Code, guiado pela skill] lê comparativo.json e escreve resumo_executivo.md
   (redação do resumo — não é código Python)
        │
        ▼
[Python] build-excel --run <run_id>
   valida o resumo (sem linguagem de recomendação), roda a auditoria automática
   e a amostragem para revisão manual, monta e valida as 6 abas do Excel
   produz: output/MagaluResultados_N<N>_<timestamp>.xlsx
```

Não existe uma "aplicação" rodando em segundo plano: cada estágio Python é um comando de CLI curto que o Claude Code invoca via shell durante a conversa, na ordem acima. Os dois estágios semânticos são o próprio Claude Code trabalhando, não uma chamada de API dentro do código — por isso nunca aparecem como módulo `.py` de "análise" ou "resumo": o que existe em Python para eles é só o **contrato** (schema + validação) que a saída do Claude Code precisa respeitar.

A geração do Excel é código Python testável (openpyxl), seguindo a estrutura definida na skill; a skill `document-skills:xlsx` é consultada como referência de boas práticas de montagem/validação de planilha durante a implementação, não substitui esse código.

---

## Estrutura de diretórios prevista

```
TrabalhoEIIAgents/
├── .venv/                        (existente)
├── .gitignore                    (novo)
├── CLAUDE.md                     (existente)
├── README.md                     (a expandir)
├── requirements.txt              (gerado na Fase 14)
├── .claude/
│   └── skills/magalu-release-analysis/   (existente)
├── magalu_analysis/
│   ├── __init__.py
│   ├── __main__.py               # permite `python -m magalu_analysis <subcomando>`
│   ├── cli.py                    # subcomandos: fetch, compare, build-excel
│   ├── config.py                 # URL da Central de Resultados, paths, constantes internas
│   ├── models.py                 # Documento, PaginaTexto, Indicador, Pendencia, ComparacaoItem, ResultadoAuditoria, RunManifest
│   ├── discovery.py               # lista documentos da Central de Resultados oficial
│   ├── classification.py          # filtra apenas releases de resultados
│   ├── period_parsing.py          # interpreta ano/trimestre a partir do nome/metadado do documento
│   ├── selection.py               # ordena por período fiscal e seleciona os N mais recentes
│   ├── download.py                # baixa PDFs e valida que são textuais/não corrompidos
│   ├── extraction.py              # extrai texto por página preservando documento+página
│   ├── indicators_schema.py       # contrato/validador do JSON de indicadores (escrito pelo Claude Code)
│   ├── persistence.py             # carrega, valida e consolida indicators.json + evidências
│   ├── comparison.py              # regras de comparação entre N períodos
│   ├── summary_schema.py          # validador do resumo executivo (linguagem proibida, evidência mínima)
│   ├── pendencias.py              # consolida pendências vindas de indicadores/comparação/resumo
│   ├── excel_builder.py           # monta as 6 abas do Excel (openpyxl)
│   └── audit.py                   # auditoria automática + amostragem para revisão manual
├── data/
│   └── runs/<run_id>/             # artefatos intermediários por execução (gitignored)
├── output/                        # Excel finais gerados (gitignored)
├── tests/
│   ├── fixtures/                  # PDF textual de exemplo, HTML de exemplo da Central de Resultados, JSONs de exemplo
│   └── test_*.py                  # um arquivo de teste por módulo acima
└── docs/
    └── superpowers/plans/2026-09-17-magalu-release-analysis-pipeline.md   (este arquivo)
```

---

## Sequência numerada de fases

### Fase 1 — Fundação do projeto e modelos de dados
Cria o pacote `magalu_analysis/`, `config.py` (constantes internas) e `models.py` com as estruturas de dados centrais (`Documento`, `PaginaTexto`, `Indicador`, `Pendencia`, `ComparacaoItem`, `ResultadoAuditoria`, `RunManifest`), usando `pydantic` para validação. Cria `.gitignore` (excluindo `.venv/`, `data/runs/`, `output/`, `__pycache__/`). Cria `tests/` com os primeiros testes de modelo (validação de campos obrigatórios, `null` para ausentes, rejeição de tipos inválidos).
**Arquivos:** `magalu_analysis/{__init__,config,models}.py`, `.gitignore`, `tests/test_models.py`.
**Ponto de validação:** os modelos rejeitam dados inconsistentes com os testes (ex.: confiança fora de faixa, segmento fora do vocabulário controlado) antes de qualquer integração real.

### Fase 2 — Descoberta, classificação, período fiscal e seleção
Antes de codificar, inspecionar manualmente a página real da Central de Resultados oficial (estrutura HTML, se há listagem paginada, nomenclatura dos documentos) — isso define o parser real de `discovery.py`. Implementa `discovery.py` (lista documentos), `classification.py` (mantém só releases de resultados, descarta apresentações/formulários/atas), `period_parsing.py` (normaliza "3T24", "Terceiro Trimestre de 2024" etc. para `(ano, trimestre)`) e `selection.py` (ordena por período fiscal decrescente e seleciona os N mais recentes).
**Arquivos:** `magalu_analysis/{discovery,classification,period_parsing,selection}.py`, `tests/{test_discovery,test_classification,test_period_parsing,test_selection}.py`, fixtures de HTML de exemplo.
**Testes:** discovery testado com HTML fixture (mock de rede, nunca acessa a internet real em teste unitário); classificação com uma lista mista de tipos de documento; parsing de período com várias grafias observadas no site real; seleção com N variando (1, 3, todos os disponíveis, N maior que o disponível → deve sinalizar, não inventar).
**Ponto de validação:** rodar `discovery` uma vez contra o site real (fora da suíte automatizada) e conferir manualmente que os N mais recentes batem com o calendário público de resultados da Magalu.

### Fase 3 — Download, validação de PDF, extração de texto e comando `fetch`
Implementa `download.py` (baixa o PDF, confere integridade e que é textual — se `extract_text()` vier vazio em todas as páginas, rejeita como não-textual, sem OCR) e `extraction.py` (extrai texto por página, preservando o número da página). Implementa o subcomando `fetch --n N` em `cli.py`, que encadeia as Fases 2 e 3 e grava `data/runs/<run_id>/manifest.json` + um `<doc>.pages.json` por documento.
**Arquivos:** `magalu_analysis/{download,extraction,cli}.py`, `magalu_analysis/__main__.py`, `tests/{test_download,test_extraction,test_cli}.py`, fixture de PDF textual pequeno.
**Testes:** download com servidor mockado (sucesso, 404, PDF corrompido, PDF sem texto extraível); extração preservando página exata contra o PDF fixture; `fetch` de ponta a ponta com tudo mockado.
**Ponto de validação:** rodar `fetch --n 1` contra a fonte real uma vez, abrir o `pages.json` gerado e conferir manualmente que o texto de 2-3 páginas bate com o PDF original.

### Fase 4 — Contrato de indicadores e persistência das evidências
Define `indicators_schema.py`: o schema exato (pydantic) que o Claude Code deve preencher em `<doc>.indicators.json` para cada valor extraído (indicador, categoria, segmento, tipo de período, ajustado/reportado, unidade, valor original, valor normalizado, página, trecho-fonte, confiança) — espelhando `references/indicadores.md` e `references/regras-interpretacao.md` da skill. Implementa `persistence.py`, que carrega os `.indicators.json` de um `run_id`, valida contra o schema (erros claros em caso de campo ausente/tipo errado) e consolida num único dataset em memória para a fase seguinte.
**Interlúdio (não é código):** com o `fetch` já rodado, o Claude Code lê os `.pages.json` dos N documentos e escreve um `.indicators.json` por documento, seguindo o procedimento da skill.
**Arquivos:** `magalu_analysis/{indicators_schema,persistence}.py`, `tests/{test_indicators_schema,test_persistence}.py`, fixture de `indicators.json` válido e inválido.
**Ponto de validação:** validar um `.indicators.json` real escrito pelo Claude Code contra um documento de teste; conferir manualmente 3-5 valores contra o PDF original.

### Fase 5 — Comparação entre N períodos
Implementa `comparison.py` seguindo `references/comparacao.md`: ordena períodos cronologicamente, representa período ausente como `null`, calcula variação absoluta/percentual para valores monetários e quantidades, variação em pontos percentuais para margens, nunca calcula variação percentual sobre base zero nem sobre valor de confiança baixa, nunca mistura métricas incompatíveis (ajustado×reportado, trimestre×acumulado, segmentos diferentes).
**Arquivos:** `magalu_analysis/comparison.py`, `tests/test_comparison.py`.
**Testes:** casos para N=2, N=3, N=5; período ausente; base zero; confiança baixa; margem vs. valor monetário; tentativa de misturar séries incompatíveis (deve recusar/sinalizar, não calcular).
**Ponto de validação:** conferir manualmente 2-3 variações calculadas contra uma conta feita à mão a partir do `indicators.json` real.

### Fase 6 — Contrato e validação do resumo executivo
Define `summary_schema.py`: valida que `resumo_executivo.md` não contém linguagem promocional ou de recomendação de investimento (lista de termos/padrões proibidos, verificação heurística) e que menciona apenas períodos presentes no `comparativo.json`.
**Interlúdio (não é código):** com `compare` já rodado, o Claude Code lê `comparativo.json` e as evidências e redige `resumo_executivo.md`, seguindo a seção "Resumo executivo" da skill.
**Arquivos:** `magalu_analysis/summary_schema.py`, `tests/test_summary_schema.py`.
**Ponto de validação:** revisar manualmente um resumo real gerado, frase a frase, contra a lista de gatilhos de revisão humana da skill.

### Fase 7 — Geração e validação do Excel
Implementa `excel_builder.py` (openpyxl), montando as 6 abas definidas em `references/planilha-excel.md` (Resumo, Comparativo, Evidências, Documentos, Pendências, Auditoria) a partir dos artefatos já validados (`manifest.json`, dataset de indicadores, `comparativo.json`, `resumo_executivo.md`, pendências, auditoria). Inclui validação pós-geração (reabrir o arquivo com openpyxl, confirmar as 6 abas, cabeçalhos e contagem de linhas esperada).
**Arquivos:** `magalu_analysis/excel_builder.py`, `tests/test_excel_builder.py`.
**Ponto de validação:** abrir manualmente o Excel gerado a partir de um run real e conferir visualmente as 6 abas.

### Fase 8 — Consolidação de pendências
Implementa `pendencias.py`, agregando pendências vindas de `persistence.py` (unidade não clara, tabela sem estrutura, etc.), `comparison.py` (comparação recusada) e `summary_schema.py` (risco de linguagem de recomendação) num único conjunto para a aba "Pendências".
**Arquivos:** `magalu_analysis/pendencias.py`, `tests/test_pendencias.py`.
**Ponto de validação:** conferir que nenhuma pendência é perdida ao consolidar (teste com pendências vindas das três origens simultaneamente).

### Fase 9 — Auditoria automática e amostragem para revisão manual
Implementa `audit.py`: checagens automáticas mínimas definidas na skill (todo valor do Comparativo tem evidência; nenhuma comparação mistura métricas incompatíveis; nenhuma variação percentual com base zero; nenhuma variação sobre confiança baixa; resumo sem linguagem de recomendação) e uma amostragem interna (tamanho fixo, não exposto ao usuário) de indicadores extraídos para revisão manual, listados com página e trecho-fonte para facilitar a checagem humana.
**Arquivos:** `magalu_analysis/audit.py`, `tests/test_audit.py`.
**Ponto de validação:** revisar manualmente a amostra sugerida de um run real e confirmar que os valores batem com o PDF.

### Fase 10 — CLI final e integração ponta a ponta
Completa `cli.py` com os subcomandos `compare --run <run_id>` (Fases 4+5) e `build-excel --run <run_id>` (Fases 6+7+8+9), incluindo mensagens claras indicando o que o Claude Code deve fazer entre um comando e outro (ex.: "escreva os arquivos .indicators.json antes de rodar compare"). Testa o fluxo completo com todos os estágios Python encadeados sobre fixtures.
**Arquivos:** `magalu_analysis/cli.py` (extensão), `tests/test_cli.py` (extensão).
**Ponto de validação:** rodar `fetch → compare → build-excel` de ponta a ponta com fixtures e obter um Excel válido sem intervenção manual nos estágios Python.

### Fase 11 — Consolidação da suíte de testes unitários
Revisão cruzada da suíte: cobertura dos casos de borda listados nas regras da skill (confiança baixa, conflito, ambiguidade, unidade não clara, tabela sem estrutura, ajustado×reportado, trimestre×acumulado, narrativa×tabela, N maior que documentos disponíveis). Não é uma fase de código novo, é revisão e preenchimento de lacunas de teste identificadas nas fases anteriores.
**Ponto de validação:** rodar `pytest` completo e revisar manualmente a lista de casos de borda da skill contra os testes existentes, fechando qualquer lacuna encontrada.

### Fase 12 — Validação real controlada (execução completa)
Executa o pipeline completo contra a Central de Resultados oficial de verdade, com um N pequeno (ex.: N=2), do `fetch` ao Excel final, incluindo os dois interlúdios reais do Claude Code. Não é um teste automatizado — é uma checagem humana de ponta a ponta antes de considerar o projeto pronto para uso.
**Ponto de validação:** Excel final revisado manualmente linha a linha nas 6 abas; nenhum valor sem evidência; nenhuma pendência perdida; resumo executivo revisado quanto a linguagem de recomendação.

### Fase 13 — Documentação
Expande o `README.md`: como ativar o `.venv`, como rodar cada subcomando, como interpretar as 6 abas do Excel, e um resumo do fluxo híbrido Python/Claude Code (sem repetir o conteúdo da skill ou do CLAUDE.md, só referenciá-los).
**Arquivos:** `README.md`.

### Fase 14 — Geração final do `requirements.txt`
Com a implementação completa, gera `requirements.txt` a partir do que está de fato instalado e usado no `.venv` (ex.: `pip freeze` dentro do ambiente já populado só com os pacotes realmente importados pelo projeto).
**Arquivos:** `requirements.txt`.

### Fase 15 — Preparação para versionamento no GitHub
Revisão final antes de qualquer commit/push: conferir `.gitignore` (nada de `.venv/`, `data/runs/`, `output/`, artefatos com dados baixados), revisar `git status` em busca de arquivo sensível, e confirmar que a estrutura de commits proposta faz sentido (ex.: um commit por fase). Push continua exigindo aprovação explícita a cada vez, conforme as regras de segurança do agente.

---

## Arquivos previstos (resumo)

**Código:** `magalu_analysis/{__init__,__main__,cli,config,models,discovery,classification,period_parsing,selection,download,extraction,indicators_schema,persistence,comparison,summary_schema,pendencias,excel_builder,audit}.py`

**Testes:** um `tests/test_<módulo>.py` por módulo acima, mais `tests/fixtures/` (PDF textual de exemplo, HTML de exemplo da Central de Resultados, `indicators.json` válido/inválido de exemplo).

**Config/infra:** `.gitignore`, `requirements.txt` (Fase 14), `README.md` (Fase 13).

**Dados/execução (gitignored):** `data/runs/<run_id>/*.json`, PDFs baixados, `output/*.xlsx`.

## Testes previstos (resumo)

Um arquivo de teste por módulo (listado por fase acima), todos rodando sobre fixtures locais — nenhum teste unitário acessa a rede real. Casos de borda obrigatórios, extraídos das regras da skill: N maior que o disponível, período ausente, valor de confiança baixa, conflito entre fontes, unidade ambígua, tabela sem estrutura, dúvida ajustado×reportado, dúvida trimestre×acumulado, base zero na variação percentual, tentativa de comparar métricas incompatíveis, linguagem de recomendação no resumo.

## Dependências prováveis

- `requests` — download de páginas e PDFs.
- `beautifulsoup4` — parsing do HTML da Central de Resultados.
- `pdfplumber` — extração de texto por página (detecta PDF não-textual quando `extract_text()` vem vazio).
- `pydantic` — validação dos modelos de dados e dos contratos JSON (indicadores, resumo).
- `openpyxl` — geração e leitura de validação do Excel.
- `pytest` — testes.
- `requests-mock` — mock de HTTP nos testes de `discovery`/`download`, evitando acesso à rede real na suíte automatizada.

Lista final fechada apenas na Fase 14, com base no que realmente for importado.

## Pontos de validação (checklist consolidado)

1. Fase 2 — seleção dos N mais recentes confere com o calendário público real de resultados da Magalu.
2. Fase 3 — texto extraído de um PDF real bate manualmente com o conteúdo do documento.
3. Fase 4 — `indicators.json` real validado contra o schema e conferido manualmente contra o PDF.
4. Fase 5 — variações calculadas conferidas manualmente contra conta feita à mão.
5. Fase 6 — resumo executivo real revisado frase a frase contra os gatilhos de revisão humana.
6. Fase 7 — Excel real aberto e revisado visualmente nas 6 abas.
7. Fase 9 — amostra de auditoria revisada manualmente contra o PDF original.
8. Fase 10 — pipeline completo roda de ponta a ponta sobre fixtures sem intervenção manual nos estágios Python.
9. Fase 12 — execução real completa (N pequeno) revisada linha a linha antes de considerar o projeto pronto.
10. Fase 15 — `git status` revisado antes de qualquer commit/push, nada sensível ou gerado incluído.
