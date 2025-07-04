import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    print("Supabase não está instalado. Usando modo local.")
    SUPABASE_AVAILABLE = False
    Client = None

class SupabaseClient:
    def __init__(self):
        self.client = None
        
        if not SUPABASE_AVAILABLE:
            return
            
        # Obter configurações do ambiente
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if url and key and url != "placeholder" and key != "placeholder":
            try:
                self.client: Client = create_client(url, key)
                print("Conectado ao Supabase com sucesso!")
            except Exception as e:
                print(f"Erro ao conectar ao Supabase: {e}")
                self.client = None
        else:
            print("Configurações do Supabase não encontradas. Usando modo local.")

# Instância global
_supabase_client = None

def get_supabase_client():
    """Retorna a instância do cliente Supabase"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client.client

def init_supabase():
    """Inicializa o cliente Supabase"""
    global _supabase_client
    _supabase_client = SupabaseClient()
    return _supabase_client.client

