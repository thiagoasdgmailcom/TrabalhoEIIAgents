import json

from magalu_analysis.models import Pendencia
from magalu_analysis.pendencias import carregar_pendencias, consolidar_pendencias

PENDENCIA_EXEMPLO = {
    "tipo_gatilho": "narrativa_vs_tabela",
    "descricao": "Destaque textual diverge do valor tabulado",
    "documento_id": "magalu-2026-q2",
    "pagina": 1,
    "indicador_relacionado": "Fluxo de Caixa Operacional",
    "trecho_fonte": "geração de caixa operacional foi de R$258,8 milhões",
    "acao_sugerida": "Confirmar qual valor é o oficial",
}


def test_carregar_pendencias_retorna_lista_vazia_quando_arquivo_nao_existe(tmp_path):
    assert carregar_pendencias(tmp_path / "nao-existe.json") == []


def test_carregar_pendencias_parseia_arquivo_valido(tmp_path):
    caminho = tmp_path / "pendencias.json"
    caminho.write_text(json.dumps([PENDENCIA_EXEMPLO]), encoding="utf-8")

    pendencias = carregar_pendencias(caminho)

    assert len(pendencias) == 1
    assert pendencias[0].tipo_gatilho == "narrativa_vs_tabela"


def test_consolidar_pendencias_concatena_mantendo_ordem():
    p1 = Pendencia(**PENDENCIA_EXEMPLO)
    p2 = Pendencia(**{**PENDENCIA_EXEMPLO, "indicador_relacionado": "EBITDA"})

    resultado = consolidar_pendencias([p1], [p2])

    assert resultado == [p1, p2]
