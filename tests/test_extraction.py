import json
from pathlib import Path

from magalu_analysis.extraction import extrair_paginas, salvar_paginas_json

FIXTURE_PDF = Path(__file__).parent / "fixtures" / "sample_release.pdf"


def test_extrai_uma_pagina_texto_por_pagina_do_pdf():
    paginas = extrair_paginas(FIXTURE_PDF, documento_id="magalu-2026-q1")

    assert len(paginas) == 2
    assert paginas[0].numero_pagina == 1
    assert paginas[1].numero_pagina == 2
    assert paginas[0].documento_id == "magalu-2026-q1"


def test_texto_extraido_preserva_conteudo_real_da_pagina():
    paginas = extrair_paginas(FIXTURE_PDF, documento_id="magalu-2026-q1")

    assert "Divulgação de Resultados" in paginas[0].texto
    assert "EBITDA" in paginas[0].texto


def test_salvar_paginas_json_grava_um_arquivo_por_documento(tmp_path):
    paginas = extrair_paginas(FIXTURE_PDF, documento_id="magalu-2026-q1")
    destino = tmp_path / "magalu-2026-q1.pages.json"

    salvar_paginas_json(paginas, destino)

    conteudo = json.loads(destino.read_text(encoding="utf-8"))
    assert len(conteudo) == 2
    assert conteudo[0]["numero_pagina"] == 1
    assert conteudo[0]["documento_id"] == "magalu-2026-q1"
