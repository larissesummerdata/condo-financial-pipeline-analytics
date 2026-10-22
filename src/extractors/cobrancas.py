from pathlib import Path
import re
from typing import Any, Dict, List, Tuple
import pdfplumber

def extract_cobrancas_pdf(pdf_path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    nome_arquivo = Path(pdf_path).name
    boletos_registros: List[Dict[str, Any]] = []
    destinacoes_registros: List[Dict[str, Any]] = []

    comp_regex = re.compile(r"Competência:\s*(\d{2}/\d{4})", re.IGNORECASE)
    venc_regex = re.compile(r"Vencimento:\s*(\d{2}/\d{2}/\d{4})", re.IGNORECASE)
    destinacao_regex = re.compile(r"^([A-Za-zÀ-ÖØ-öø-ÿ\s]+?)\s+(R\$\s*[\d\.,-]+)$")

    competencia = "N/A"
    vencimento_padrao = "N/A"

    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            page_num = page_idx + 1
            text = page.extract_text() or ""

            if "Cobrança Detalhada" not in text and "Destinações" not in text:
                continue

            c_match = comp_regex.search(text)
            if c_match:
                competencia = c_match.group(1)

            v_match = venc_regex.search(text)
            if v_match:
                vencimento_padrao = v_match.group(1)

            if "Destinações" in text:
                capturando = False
                for linha in text.split("\n"):
                    l_clean = linha.strip()
                    if "Destinações" in l_clean:
                        capturando = True
                        continue
                    if "Vencimento:" in l_clean or "N°" in l_clean:
                        capturando = False

                    if capturando:
                        d_match = destinacao_regex.match(l_clean)
                        if d_match:
                            rubrica = d_match.group(1).strip()
                            valor_rubrica = d_match.group(2).strip()
                            if rubrica.lower() != "taxa":
                                destinacoes_registros.append({
                                    "arquivo_origem": nome_arquivo,
                                    "numero_pagina": page_num,
                                    "competencia": competencia,
                                    "taxa_rubrica": rubrica,
                                    "valor_total_declarado": valor_rubrica,
                                })

            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or not row[0] or "N°" in str(row[0]) or len(row) < 8:
                        continue

                    cells = [str(c).replace("\n", " ").strip() if c is not None else "" for c in row]

                    boletos_registros.append({
                        "arquivo_origem": nome_arquivo,
                        "numero_pagina": page_num,
                        "unidade_bloco": cells[3],
                        "numero_documento": cells[1],
                        "competencia": competencia,
                        "destinacao": cells[2],
                        "data_vencimento": vencimento_padrao,
                        "data_pagamento": cells[5],
                        "valor_principal": cells[4],
                        "valor_multa": "0,00",
                        "valor_juros": "0,00",
                        "valor_desconto": "0,00",
                        "valor_total_pago": cells[6],
                        "situacao_cobranca": cells[7],
                    })

    return boletos_registros, destinacoes_registros
