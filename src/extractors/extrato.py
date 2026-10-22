from pathlib import Path
import re
from typing import Any, Dict, List
import pdfplumber

def extract_extrato_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    nome_arquivo = Path(pdf_path).name
    registros: List[Dict[str, Any]] = []
    ordem_contador = 1

    linha_regex = re.compile(
        r"^(\d{2}/\d{2}/\d{4})\s+(\S+)\s+(.*?)\s+([\d\.,]+\s*[CD])\s+([\d\.,]+\s*[CD])"
    )

    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            page_num = page_idx + 1
            text = page.extract_text() or ""

            if not ("GERENCIADOR" in text.upper() and ("CAIXA" in text.upper() or "EXTRATO" in text.upper())):
                continue

            conta_match = re.search(r"Conta:\s*\|?\s*(\d+)\s*\|?\s*(\d+)\s*\|?\s*([\d-]+)", text)
            banco_identificador = f"CAIXA_{conta_match.group(3)}" if conta_match else "CAIXA_OPERACIONAL"

            for linha in text.split("\n"):
                l_clean = linha.strip()
                if "SALDO DIA" in l_clean or "SALDO ANTERIOR" in l_clean:
                    continue

                match = linha_regex.match(l_clean)
                if match:
                    data_str, nr_doc, historico, valor_str, saldo_str = match.groups()
                    tipo_op = "C" if "C" in valor_str else "D"

                    registros.append({
                        "arquivo_origem": nome_arquivo,
                        "numero_pagina": page_num,
                        "ordem_linha": ordem_contador,
                        "banco_identificador": banco_identificador,
                        "data_movimentacao": data_str,
                        "numero_documento": nr_doc,
                        "descricao_historico": historico.strip(),
                        "tipo_operacao": tipo_op,
                        "valor_transacao": valor_str.strip(),
                        "saldo_resultante": saldo_str.strip(),
                    })
                    ordem_contador += 1

    return registros
