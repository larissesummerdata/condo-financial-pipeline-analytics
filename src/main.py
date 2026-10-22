import hashlib
from pathlib import Path
import re
from typing import Any, Dict, List
from dotenv import load_dotenv
import pdfplumber
from connection import get_supabase_client
from extractors import (
    extract_cobrancas_pdf,
    extract_comprovantes_pdf,
    extract_extrato_pdf,
    extract_razao_pdf,
)

load_dotenv()


def calcular_md5(caminho_arquivo: str) -> str:
    """Calcula hash MD5 do arquivo para garantir integridade e rastreabilidade."""
    hasher = hashlib.md5()
    with open(caminho_arquivo, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


def registrar_controle_arquivo(
    client, nome_arquivo: str, hash_md5: str, total_paginas: int, competencia: str
) -> None:
    """
    Garante Idempotência Física:
    Remove histórico prévio do arquivo na tabela de controle (que apaga em cascata
    todas as linhas filhas nas tabelas raw via ON DELETE CASCADE).
    """
    controle_ref = client.table("raw_arquivos_controle")
    controle_ref.delete().eq("nome_arquivo", nome_arquivo).execute()

    controle_ref.insert({
        "nome_arquivo": nome_arquivo,
        "competencia_declarada": competencia,
        "hash_md5": hash_md5,
        "total_paginas": total_paginas,
        "status_processamento": "PROCESSANDO",
    }).execute()


def finalizar_controle_arquivo(client, nome_arquivo: str, status: str = "CONCLUIDO") -> None:
    client.table("raw_arquivos_controle").update({
        "status_processamento": status
    }).eq("nome_arquivo", nome_arquivo).execute()


def load_to_supabase(
    supabase_client,
    table_name: str,
    records: List[Dict[str, Any]],
    batch_size: int = 150,
) -> None:
    """Insere registros em lotes utilizando a conexão padrão (schema bronze configurado)."""
    total = len(records)
    if total == 0:
        print(f"[!] Sem registros para inserir em 'bronze.{table_name}'.")
        return

    print(f"[*] Carregando {total} registros em 'bronze.{table_name}'...")
    table_ref = supabase_client.table(table_name)

    for i in range(0, total, batch_size):
        batch = records[i:i + batch_size]
        try:
            table_ref.insert(batch).execute()
        except Exception as e:
            print(f"[X] Erro ao inserir lote {i + 1}-{min(i + batch_size, total)} em {table_name}: {e}")
            raise e

    print(f"[✓] Carga concluída: {total} registros em 'bronze.{table_name}'.\n")


def run_pipeline(pdf_path: str) -> None:
    caminho = Path(pdf_path)
    if not caminho.exists():
        print(f"[X] Arquivo PDF não encontrado: {pdf_path}")
        return

    nome_arquivo = caminho.name
    hash_md5 = calcular_md5(pdf_path)

    # Identifica dinamicamente total de páginas e competência
    with pdfplumber.open(pdf_path) as pdf:
        total_paginas = len(pdf.pages)
        primeira_pagina = pdf.pages[0].extract_text() or ""
        comp_match = re.search(r"Competência:\s*(\d{2}/\d{4})", primeira_pagina, re.IGNORECASE)
        competencia = comp_match.group(1) if comp_match else "N/A"

    print("==================================================")
    print("INICIANDO PIPELINE ELT BRONZE (IDEMPOTENTE)")
    print(f"Arquivo: {nome_arquivo}")
    print(f"Competência: {competencia} | Páginas: {total_paginas}")
    print(f"MD5: {hash_md5}")
    print("==================================================\n")

    supabase = get_supabase_client()

    try:
        # 0. Controle e Idempotência
        print("[*] Registrando controle e expurgando cargas anteriores do arquivo...")
        registrar_controle_arquivo(supabase, nome_arquivo, hash_md5, total_paginas, competencia)

        # 1. Extrato Bancário
        print("[*] Processando Extrato Bancário...")
        extrato_records = extract_extrato_pdf(pdf_path)
        load_to_supabase(supabase, "raw_extrato_bancario", extrato_records)

        # 2. Cobrança de Boletos & Destinações
        print("[*] Processando Cobrança e Destinações...")
        boletos_records, destinacoes_records = extract_cobrancas_pdf(pdf_path)
        load_to_supabase(supabase, "raw_cobranca_destinacoes", destinacoes_records)
        load_to_supabase(supabase, "raw_cobranca_boletos", boletos_records)

        # 3. Livro Razão Analítico (dinâmico, sem hardcoding)
        print("[*] Processando Livro Razão...")
        razao_records = extract_razao_pdf(pdf_path)
        load_to_supabase(supabase, "raw_razao", razao_records)

        # 4. Comprovantes e Notas Fiscais
        print("[*] Processando Comprovantes e Anexos...")
        comprovantes_records = extract_comprovantes_pdf(pdf_path)
        load_to_supabase(supabase, "raw_comprovantes", comprovantes_records)

        # Finaliza com sucesso
        finalizar_controle_arquivo(supabase, nome_arquivo, "CONCLUIDO")
        print("==================================================")
        print("[✓] Carga da Camada Bronze finalizada com sucesso!")
        print("==================================================")

    except Exception as err:
        print(f"\n[X] Falha na esteira: {err}")
        finalizar_controle_arquivo(supabase, nome_arquivo, "ERRO")
        raise err


if __name__ == "__main__":
    diretorio_raw = Path("data/raw")
    arquivos_pdf = list(diretorio_raw.glob("*.pdf"))

    if not arquivos_pdf:
        print("[X] Nenhum arquivo .pdf encontrado na pasta data/raw/")
    else:
        pdf_alvo = str(arquivos_pdf[0])
        print(f"[*] PDF selecionado automaticamente: {pdf_alvo}\n")
        run_pipeline(pdf_path=pdf_alvo)