import re
from pathlib import Path
import pdfplumber


def parse_numeric(val_str: str) -> float:
  """Converte 'R$ 1.250,50' ou '1250,50' para float 1250.50."""
  if not val_str:
    return 0.0
  clean = (
      str(val_str)
      .replace("R$", "")
      .replace(" ", "")
      .replace(".", "")
      .replace(",", ".")
      .strip()
  )
  try:
    return float(clean)
  except ValueError:
    return 0.0


def parse_date(date_str: str) -> str | None:
  """Converte '23/08/2026' para '2026-08-23' (padrão ISO PostgreSQL)."""
  if not date_str or "/" not in str(date_str):
    return None
  parts = str(date_str).strip().split("/")
  if len(parts) == 3:
    return f"{parts[2]}-{parts[1]}-{parts[0]}"
  return None


def extract_cobrancas_pdf(pdf_path: str) -> list[dict]:
  """Extrai as linhas de cobrança das páginas 18 a 21 e valida totais[cite: 229, 230, 231, 232]."""
  nome_arquivo = Path(pdf_path).name
  registros = []

  total_esperado_cabecalho = None
  boletos_esperados_cabecalho = None

  with pdfplumber.open(pdf_path) as pdf:
    for page_idx, page in enumerate(pdf.pages):
      page_num = page_idx + 1

      # A cobrança detalhada fica estritamente até a página 25
      if page_num > 25:
        break

      text = page.extract_text() or ""

      if "Cobrança Detalhada" in text or (
          "Situação" in text and "Unidade" in text and "Valor Pago" in text
      ):
        comp_match = re.search(r"Competência:\s*(\d{2}/\d{4})", text)
        competencia = comp_match.group(1) if comp_match else "N/A"

        tot_match = re.search(r"Total Principal:\s*R\$\s*([\d\.,]+)", text)
        if tot_match:
          total_esperado_cabecalho = parse_numeric(tot_match.group(1))

        qtd_match = re.search(r"Quantidade de Boletos:\s*(\d+)", text)
        if qtd_match:
          boletos_esperados_cabecalho = int(qtd_match.group(1))

        tables = page.extract_tables()
        for table in tables:
          for row in table:
            if not row or not row[0]:
              continue

            cells = [c.replace("\n", " ").strip() if c else "" for c in row]

            if "N°" in cells[0] or "Número" in cells[0]:
              continue

            if len(cells) >= 8:
              v_principal = parse_numeric(cells[4])
              v_pago = parse_numeric(cells[6])

              registros.append({
                  "arquivo_origem": nome_arquivo,
                  "numero_pagina": page_num,
                  "competencia": competencia,
                  "numero_documento": cells[1],
                  "destinacao": cells[2],
                  "unidade_raw": cells[3],
                  "valor_principal_raw": cells[4],
                  "valor_principal": v_principal,
                  "data_pagamento_raw": cells[5],
                  "data_pagamento": parse_date(cells[5]),
                  "valor_pago_raw": cells[6],
                  "valor_pago": v_pago,
                  "situacao_raw": cells[7],
                  "payload_linha": {
                      "linha_ordem": cells[0],
                      "colunas_brutas": cells,
                  },
              })

  if registros:
    total_somado = round(sum(r["valor_principal"] for r in registros), 2)
    qtd_somada = len(registros)

    print("\n--- TESTE DE AUDITORIA: COBRANÇAS ---")
    if boletos_esperados_cabecalho:
      print(
          f"Boletos extraídos: {qtd_somada} | Esperados:"
          f" {boletos_esperados_cabecalho}"
      )

    if total_esperado_cabecalho:
      print(
          f"Total somado: R$ {total_somado:.2f} | Cabeçalho: R$"
          f" {total_esperado_cabecalho:.2f}"
      )

  return registros


def extract_extrato_pdf(pdf_path: str) -> list[dict]:
  """Extrai as movimentações bancárias da Caixa (páginas 11 a 14) via regex[cite: 222, 223, 224, 225]."""
  nome_arquivo = Path(pdf_path).name
  registros = []
  ordem_contador = 1

  padrao_linha = re.compile(
      r"^(\d{2}/\d{2}/\d{4})\s+(\S+)\s+(.*?)\s+([\d\.,]+\s*[CD])\s+([\d\.,]+\s*[CD])"
  )

  with pdfplumber.open(pdf_path) as pdf:
    for page_idx, page in enumerate(pdf.pages):
      page_num = page_idx + 1

      if page_num > 15:
        break

      text = page.extract_text() or ""

      if "GERENCIADOR" in text.upper() and (
          "CAIXA" in text.upper() or "EXTRATO" in text.upper()
      ):
        comp_match = re.search(
            r"Mês:\s*([A-Za-zçÇ]+/\d{4})", text, re.IGNORECASE
        )
        competencia = comp_match.group(1) if comp_match else "N/A"

        conta_match = re.search(
            r"Conta:\s*\|?\s*(\d+)\s*\|?\s*(\d+)\s*\|?\s*([\d-]+)", text
        )
        banco_conta = (
            f"CAIXA_{conta_match.group(3)}"
            if conta_match
            else "CAIXA_578357836-0"
        )

        for linha in text.split("\n"):
          linha = linha.strip()

          if "SALDO DIA" in linha or "SALDO ANTERIOR" in linha:
            continue

          match = padrao_linha.match(linha)
          if match:
            data_str, nr_doc, historico, valor_str, saldo_str = match.groups()

            data_mov = parse_date(data_str)
            historico = historico.strip()

            valor_str = valor_str.replace(" ", "")
            tipo_op = "C" if valor_str.endswith("C") else "D"
            valor_limpo = valor_str.replace("C", "").replace("D", "").strip()

            saldo_str = saldo_str.replace(" ", "")
            saldo_limpo = saldo_str.replace("C", "").replace("D", "").strip()

            valor_num = parse_numeric(valor_limpo)
            saldo_num = parse_numeric(saldo_limpo)

            if saldo_str.endswith("D"):
              saldo_num = -saldo_num

            registros.append({
                "arquivo_origem": nome_arquivo,
                "numero_pagina": page_num,
                "ordem_linha_extrato": ordem_contador,
                "competencia": competencia,
                "banco_conta": banco_conta,
                "data_movimento": data_mov,
                "numero_documento": nr_doc,
                "historico": historico,
                "valor": valor_num,
                "tipo_operacao": tipo_op,
                "saldo": saldo_num,
            })
            ordem_contador += 1

  print(f"Extrato Bancário: {len(registros)} movimentações extraídas com sucesso.")
  return registros