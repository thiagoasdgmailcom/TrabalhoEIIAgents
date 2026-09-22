from magalu_analysis.period_parsing import interpretar_periodo


def test_interpreta_rotulo_padrao_ntyy():
    assert interpretar_periodo("1T26") == (2026, 1)


def test_interpreta_rotulo_com_trimestre_quatro():
    assert interpretar_periodo("4T25") == (2025, 4)


def test_rejeita_rotulo_sem_padrao_reconhecido():
    assert interpretar_periodo("Segundo Trimestre") is None


def test_rejeita_rotulo_vazio():
    assert interpretar_periodo("") is None
