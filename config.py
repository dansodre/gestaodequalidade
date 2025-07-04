import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    # Configurações do Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Configurações do Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    
    # Configurações de E-mail
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    EMAIL_FROM = os.getenv("EMAIL_FROM")
    
    # Configurações da aplicação
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    
    @staticmethod
    def validate_config():
        """Valida se todas as configurações necessárias estão presentes"""
        required_vars = [
            "SUPABASE_URL",
            "SUPABASE_KEY", 
            "SUPABASE_SERVICE_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(Config, var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"Aviso: Variáveis de ambiente não encontradas: {', '.join(missing_vars)}")
            print("O sistema funcionará em modo de desenvolvimento com SQLite local.")
            return False
        
        return True

