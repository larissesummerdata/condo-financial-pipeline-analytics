from pathlib import Path
import re
from typing import Any, Dict, List
import pdfplumber

def extract_comprovantes_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    nome_arquivo = Path(pdf_path).name
    registros: List[Dict[str, Any]] = []

    auth_regex = re.compile(r"(?:Autentica[çc][ãa]o|Controle|Autenticidade)[:\s]+([A-Za-z0-9\.\-]+)", re.IGNORECASE)
    valor_regex = re.compile(r"(?:Valor|Total)[:\s]+(?:R\$\s*)?([\d\.,]+)", re.IGNORECASE)
    data_regex = re.compile(r"(\d{2}/\d{2}/\d{4})")

    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            page_num = page_idx + 1
            text = page.extract_text() or ""

            e_comprovante = any(k in text.upper() for k in ["COMPROVANTE DE", "PAGAMENTO PIX", "TRANSFERENCIA", "TEV ENVIADA", "DANFE", "NOTA FISCAL"])
            if not e_comprovante:
                continue

            tipo_doc = "OUTRO"
            if "PIX" in text.upper():
                tipo_doc = "PIX"
            elif "TEV" in text.upper():
                tipo_doc = "TEV"
            elif "BOLETO" in text.upper():
                tipo_doc = "BOLETO_PAGO"
            elif "DANFE" in text.upper() or "NOTA FISCAL" in text.upper():
                tipo_doc = "NOTA_FISCAL"

            auth_match = auth_regex.search(text)
            valor_match = valor_regex.search(text)
            data_match = data_regex.search(text)

            registros.append({
                "arquivo_origem": nome_arquivo,
                "numero_pagina": page_num,
                "tipo_documento": tipo_doc,
                "codigo_barras_ou_chave": "",
                "autenticacao_mecanica": auth_match.group(1).strip() if auth_match else "",
                "favorecido_nome": "",
                "favorecido_cnpj_cpf": "",
                "valor_documento": valor_match.group(1).strip() if valor_match else "0,00",
                "data_liquidacao": data_match.group(1).strip() if data_match else "",
                "contem_imagem_comprovante": len(page.images) > 0,
            })

    return registros
