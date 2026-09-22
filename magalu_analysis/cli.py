import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from . import config
from .audit import amostrar_para_revisao_manual, auditar
from .classification import filtrar_releases_resultados
from .comparison import comparar_indicadores, construir_periodo_label
from .discovery import buscar_html_central_resultados, listar_documentos
from .download import baixar_e_validar_documento
from .excel_builder import construir_workbook
from .extraction import extrair_paginas, salvar_paginas_json
from .models import ComparacaoItem, ResultadoAuditoria, ResultadoCheck, RunManifest
from .pendencias import carregar_pendencias
from .persistence import carregar_manifest, consolidar_indicadores_do_run
from .selection import selecionar_mais_recentes
from .summary_schema import validar_linguagem_resumo


class ResumoAusenteError(Exception):
    pass


TAMANHO_AMOSTRA_AUDITORIA = 6
SEMENTE_AMOSTRA_AUDITORIA = 17


def executar_fetch(n: int, diretorio_runs: Path = config.DIRETORIO_RUNS) -> RunManifest:
    html = buscar_html_central_resultados()
    releases = filtrar_releases_resultados(listar_documentos(html))
    selecionados = selecionar_mais_recentes(releases, n)

    run_id = f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}-{uuid4().hex[:8]}"
    diretorio_run = diretorio_runs / run_id
    diretorio_documentos = diretorio_run / "documents"

    documentos = []
    for doc_bruto in selecionados:
        documento = baixar_e_validar_documento(doc_bruto, diretorio_destino=diretorio_documentos)
        documentos.append(documento)

        paginas = extrair_paginas(
            diretorio_documentos / documento.nome_arquivo, documento.documento_id
        )
        salvar_paginas_json(paginas, diretorio_documentos / f"{documento.documento_id}.pages.json")

    manifest = RunManifest(
        run_id=run_id,
        empresa=config.EMPRESA,
        n_releases=n,
        periodos_selecionados=[(d.ano, d.trimestre) for d in documentos],
        data_execucao=datetime.now(timezone.utc),
        documentos=documentos,
    )

    diretorio_run.mkdir(parents=True, exist_ok=True)
    (diretorio_run / "manifest.json").write_text(manifest.model_dump_json(indent=2), encoding="utf-8")

    return manifest


def executar_compare(run_id: str, diretorio_runs: Path = config.DIRETORIO_RUNS) -> list[ComparacaoItem]:
    diretorio_run = diretorio_runs / run_id
    manifest = carregar_manifest(diretorio_run)
    indicadores = consolidar_indicadores_do_run(diretorio_run)

    periodos_por_documento = {d.documento_id: (d.ano, d.trimestre) for d in manifest.documentos}
    comparativo = comparar_indicadores(indicadores, periodos_por_documento)

    (diretorio_run / "comparativo.json").write_text(
        json.dumps([item.model_dump(mode="json") for item in comparativo], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return comparativo


def executar_build_excel(
    run_id: str,
    diretorio_runs: Path = config.DIRETORIO_RUNS,
    diretorio_output: Path = config.DIRETORIO_OUTPUT,
) -> Path:
    diretorio_run = diretorio_runs / run_id
    manifest = carregar_manifest(diretorio_run)
    indicadores = consolidar_indicadores_do_run(diretorio_run)

    periodos_por_documento = {d.documento_id: (d.ano, d.trimestre) for d in manifest.documentos}
    comparativo = comparar_indicadores(indicadores, periodos_por_documento)
    periodos_selecionados = [
        construir_periodo_label(ano, trimestre) for ano, trimestre in sorted(set(periodos_por_documento.values()))
    ]

    caminho_resumo = diretorio_run / "resumo_executivo.md"
    if not caminho_resumo.exists():
        raise ResumoAusenteError(
            f"resumo_executivo.md não encontrado em {diretorio_run}. "
            "Escreva o resumo executivo (Claude Code) antes de gerar o Excel."
        )
    resumo_executivo = caminho_resumo.read_text(encoding="utf-8")
    validar_linguagem_resumo(resumo_executivo)

    pendencias = carregar_pendencias(diretorio_run / "pendencias.json")
    auditoria = auditar(indicadores, comparativo, resumo_executivo)

    agora = datetime.now(timezone.utc)
    for indicador in amostrar_para_revisao_manual(
        indicadores, tamanho=TAMANHO_AMOSTRA_AUDITORIA, semente=SEMENTE_AMOSTRA_AUDITORIA
    ):
        auditoria.append(
            ResultadoAuditoria(
                item_verificado=(
                    f"Amostra para revisão manual: {indicador.indicador} "
                    f"({indicador.documento_id}, pág. {indicador.pagina})"
                ),
                resultado=ResultadoCheck.ALERTA,
                detalhe=(
                    f'Confirmar contra o PDF original: "{indicador.trecho_fonte}" '
                    f'-> valor original "{indicador.valor_original}"'
                ),
                regra_aplicada="audit.py#amostrar_para_revisao_manual",
                timestamp=agora,
            )
        )

    workbook = construir_workbook(
        empresa=manifest.empresa,
        periodos_selecionados=periodos_selecionados,
        documentos=manifest.documentos,
        indicadores=indicadores,
        comparativo=comparativo,
        resumo_executivo=resumo_executivo,
        pendencias=pendencias,
        auditoria=auditoria,
    )

    diretorio_output.mkdir(parents=True, exist_ok=True)
    destino = diretorio_output / f"MagaluResultados_N{manifest.n_releases}_{manifest.run_id}.xlsx"
    workbook.save(destino)

    (diretorio_run / "auditoria.json").write_text(
        json.dumps([item.model_dump(mode="json") for item in auditoria], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return destino


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="magalu_analysis")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    fetch_parser = subparsers.add_parser("fetch")
    fetch_parser.add_argument("--n", type=int, required=True)

    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("--run", type=str, required=True)

    build_excel_parser = subparsers.add_parser("build-excel")
    build_excel_parser.add_argument("--run", type=str, required=True)

    args = parser.parse_args(argv)

    if args.comando == "fetch":
        manifest = executar_fetch(args.n)
        print(f"Run {manifest.run_id}: {len(manifest.documentos)} documento(s) baixado(s) de {args.n} solicitado(s).")
        print(
            "Próximo passo: o Claude Code deve ler os arquivos .pages.json e escrever "
            "um <documento_id>.indicators.json por documento, seguindo a skill magalu-release-analysis."
        )
    elif args.comando == "compare":
        comparativo = executar_compare(args.run)
        print(f"Run {args.run}: {len(comparativo)} série(s) comparativa(s) gravada(s) em comparativo.json.")
        print(
            "Próximo passo: o Claude Code deve ler comparativo.json e escrever "
            "resumo_executivo.md antes de rodar build-excel."
        )
    elif args.comando == "build-excel":
        destino = executar_build_excel(args.run)
        print(f"Run {args.run}: Excel final gravado em {destino}.")
