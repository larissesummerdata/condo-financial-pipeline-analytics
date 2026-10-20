from pathlib import Path
from connection import get_supabase_client
from extractors import extract_cobrancas_pdf, extract_extrato_pdf


def main():
  supabase = get_supabase_client()
  raw_dir = Path("data/raw")

  pdf_files = list(raw_dir.glob("*.pdf"))
  if not pdf_files:
    print(f"Nenhum PDF encontrado em '{raw_dir.resolve()}'.")
    return

  for pdf_path in pdf_files:
    print(f"\n=======================================================")
    print(f"Processando arquivo: {pdf_path.name}")
    print(f"=======================================================")

    # 1. Extração do Extrato Bancário
    movimentacoes = extract_extrato_pdf(str(pdf_path))
    if movimentacoes:
      print(f"Limpando registros antigos do extrato para {pdf_path.name}...")
      supabase.table("raw_extrato_bancario").delete().eq(
          "arquivo_origem", pdf_path.name
      ).execute()

      print(
          f"Gravando {len(movimentacoes)} transações em"
          " 'raw_extrato_bancario'..."
      )
      batch_size = 100
      for i in range(0, len(movimentacoes), batch_size):
        batch = movimentacoes[i : i + batch_size]
        supabase.table("raw_extrato_bancario").insert(batch).execute()
      print("✓ Extrato bancário sincronizado no Supabase com sucesso!")

    # 2. Extração das Cobranças dos Boletos
    cobrancas = extract_cobrancas_pdf(str(pdf_path))
    if cobrancas:
      print(f"\nLimpando registros antigos de cobrança para {pdf_path.name}...")
      supabase.table("raw_cobranca_boletos").delete().eq(
          "arquivo_origem", pdf_path.name
      ).execute()

      print(f"Gravando {len(cobrancas)} boletos em 'raw_cobranca_boletos'...")
      batch_size = 100
      for i in range(0, len(cobrancas), batch_size):
        batch = cobrancas[i : i + batch_size]
        supabase.table("raw_cobranca_boletos").insert(batch).execute()
      print("✓ Cobranças sincronizadas no Supabase com sucesso!")


if __name__ == "__main__":
  main()