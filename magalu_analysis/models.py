from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class Documento(BaseModel):
    documento_id: str
    nome_arquivo: str
    url_origem: str
    ano: int
    trimestre: int = Field(ge=1, le=4)
    data_download: date | None = None
    num_paginas: int | None = None
    sha256: str | None = None


class PaginaTexto(BaseModel):
    documento_id: str
    numero_pagina: int
    texto: str


class Categoria(str, Enum):
    FINANCEIRO = "financeiro"
    OPERACIONAL = "operacional"


class Segmento(str, Enum):
    CONSOLIDADO = "consolidado"
    LOJAS_FISICAS = "lojas_fisicas"
    ECOMMERCE = "ecommerce"
    MARKETPLACE = "marketplace"
    UM_P = "1p"
    TRES_P = "3p"


class TipoPeriodo(str, Enum):
    TRIMESTRE = "trimestre"
    ACUMULADO = "acumulado"
    ANUAL = "anual"


class AjustadoReportado(str, Enum):
    AJUSTADO = "ajustado"
    REPORTADO = "reportado"


class Confianca(str, Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"


class Indicador(BaseModel):
    documento_id: str
    indicador: str
    categoria: Categoria
    segmento: Segmento | None = None
    tipo_periodo: TipoPeriodo
    ajustado_ou_reportado: AjustadoReportado | None = None
    unidade: str | None = None
    valor_original: str | None = None
    valor_normalizado: float | None = None
    pagina: int
    trecho_fonte: str
    confianca: Confianca


class TipoGatilho(str, Enum):
    CONFIANCA_BAIXA = "confianca_baixa"
    CONFLITO = "conflito"
    AMBIGUIDADE = "ambiguidade"
    UNIDADE_NAO_CLARA = "unidade_nao_clara"
    TABELA_SEM_ESTRUTURA = "tabela_sem_estrutura"
    DUVIDA_AJUSTADO_REPORTADO = "duvida_ajustado_reportado"
    DUVIDA_TRIMESTRE_ACUMULADO = "duvida_trimestre_acumulado"
    NARRATIVA_VS_TABELA = "narrativa_vs_tabela"
    CONCLUSAO_QUALITATIVA_FORTE = "conclusao_qualitativa_forte"
    RISCO_LINGUAGEM_RECOMENDACAO = "risco_linguagem_recomendacao"


class Pendencia(BaseModel):
    tipo_gatilho: TipoGatilho
    descricao: str
    documento_id: str | None = None
    pagina: int | None = None
    indicador_relacionado: str | None = None
    trecho_fonte: str | None = None
    acao_sugerida: str


class ComparacaoItem(BaseModel):
    indicador: str
    categoria: Categoria
    segmento: Segmento | None = None
    tipo_periodo: TipoPeriodo
    ajustado_ou_reportado: AjustadoReportado | None = None
    unidade: str | None = None
    valores_por_periodo: dict[str, float | None]
    variacao_absoluta: dict[str, float | None] = {}
    variacao_percentual_ou_pp: dict[str, float | None] = {}
    observacoes: str | None = None


class ResultadoCheck(str, Enum):
    OK = "ok"
    FALHA = "falha"
    ALERTA = "alerta"


class ResultadoAuditoria(BaseModel):
    item_verificado: str
    resultado: ResultadoCheck
    detalhe: str
    regra_aplicada: str
    timestamp: datetime


class RunManifest(BaseModel):
    run_id: str
    empresa: str
    n_releases: int
    periodos_selecionados: list[tuple[int, int]]
    data_execucao: datetime
    documentos: list[Documento]
