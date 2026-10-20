import os
from dotenv import load_dotenv
from supabase import Client, create_client

# Carrega as variáveis de ambiente do ficheiro .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Variáveis SUPABASE_URL ou SUPABASE_SERVICE_ROLE_KEY em falta no .env.")

def get_supabase_client() -> Client:
    """Retorna uma instância autenticada do cliente Supabase com permissões de service_role."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

if __name__ == "__main__":
    # Teste rápido de conectividade
    client = get_supabase_client()
    print("Conexão ao Supabase estabelecida com sucesso!")