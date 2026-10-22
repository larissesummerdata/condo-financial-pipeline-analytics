from pathlib import Path
import re
from typing import Any, Dict, List
import pdfplumber

def extract_razao_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    nome_arquivo = Path(pdf_path).name
    registros: List[Dict[str, Any]] = []
    ordem_linha = 1

    current_codigo_conta = "N/A"
    current_classificacao = "N/A"
    current_grupo = "GERAL"

    conta_pattern = re.compile(
        r"(?:Conta:?\s*)?(\d+(?:\.\d+)+)\s*[-–—]\s*([A-Za-zÀ-ÖØ-öø-ÿ0-9\s/()._-]+)",
        re.IGNORECASE,
    )
    lancamento_pattern = re.compile(
        r"^(\d{2}/\d{2}/\d{4})\s+(?:([A-Za-z0-9/_.-]+)\s+)?(.+?)\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})(?:\s+(-?\d{1,3}(?:\.\d{3})*,\d{2}))?$",
        re.IGNORECASE,
    )

    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            page_num = page_idx + 1
            text = page.extract_text() or ""

            if "Balancete Analítico" not in text and "Razão" not in text and "Conta:" not in text:
                continue

            for linha in text.split("\n"):
                l_clean = linha.strip()
                if not l_clean or "Folha:" in l_clean:
                    continue

                for grupo_alvo in ["DESPESA COM PESSOAL", "DESPESA COM AQUISIÇÕES", "DESPESA COM SERVIÇOS", "RECEITAS OPERACIONAIS", "DESPESAS ADMINISTRATIVAS"]:
                    if grupo_alvo in l_clean.upper():
                        current_grupo = grupo_alvo
                        break

                c_match = conta_pattern.search(l_clean)
                if c_match and "TOTAL" not in l_clean.upper() and "SALDO" not in l_clean.upper():
                    current_codigo_conta = c_match.group(1).strip()
                    current_classificacao = c_match.group(2).strip()
                    continue

                l_match = lancamento_pattern.match(l_clean)
                if l_match:
                    dt_str, doc_ref, hist, v1, v2 = l_match.groups()
                    registros.append({
                        "arquivo_origem": nome_arquivo,
                        "numero_pagina": page_num,
                        "ordem_linha": ordem_linha,
                        "codigo_conta": current_codigo_conta,
                        "classificacao_contabil": current_classificacao,
                        "grupo_contabil": current_grupo,
                        "data_lancamento": dt_str,
                        "documento_fiscal_ref": doc_ref or "",
                        "fornecedor_favorecido": "",
                        "historico_detalhado": hist.strip(),
                        "valor_debito": v1,
                        "valor_credito": v2 if v2 else "0,00",
                        "saldo_atual": "0,00",
                    })
                    ordem_linha += 1

    return registros
