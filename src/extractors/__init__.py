# src/extractors/__init__.py
from .cobrancas import extract_cobrancas_pdf
from .comprovantes import extract_comprovantes_pdf
from .extrato import extract_extrato_pdf
from .razao import extract_razao_pdf

__all__ = [
    "extract_cobrancas_pdf",
    "extract_extrato_pdf",
    "extract_razao_pdf",
    "extract_comprovantes_pdf",
]