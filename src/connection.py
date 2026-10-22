# src/connection.py
import os
from dotenv import load_dotenv
from supabase import Client, ClientOptions, create_client

load_dotenv()


def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY precisam estar configurados no .env")

    # Define 'bronze' nas opções globais para evitar bloqueio PGRST106
    options = ClientOptions(schema="bronze")
    return create_client(url, key, options=options)