from flask import Blueprint, request, jsonify, session
from functools import wraps
import json
import os
from email_service import send_test_email
from supabase_client import get_supabase_client

config_bp = Blueprint('config', __name__)

# Arquivo para armazenar configurações localmente
CONFIG_FILE = 'system_config.json'

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login required'}), 401
        
        # Verificar se é admin (implementar verificação real)
        user_role = session.get('user_role', 'user')
        if user_role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

def load_config():
    """Carrega configurações do arquivo"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar configurações: {e}")
    
    # Configurações padrão
    return {
        'email': {
            'smtp_server': '',
            'smtp_port': 587,
            'smtp_username': '',
            'smtp_password': '',
            'email_from': ''
        },
        'system': {
            'system_name': 'Gestão de Qualidade',
            'company_name': '',
            'timezone': 'America/Sao_Paulo',
            'language': 'pt-BR',
            'maintenance_mode': False
        },
        'database': {
            'db_type': 'supabase',
            'supabase_url': '',
            'supabase_key': '',
            'supabase_service_key': ''
        },
        'security': {
            'session_timeout': 60,
            'require_uppercase': False,
            'require_numbers': False,
            'require_special': False,
            'min_password_length': 8
        }
    }

def save_config(config):
    """Salva configurações no arquivo"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")
        return False

@config_bp.route('/api/config', methods=['GET'])
@admin_required
def get_config():
    """Retorna todas as configurações"""
    try:
        config = load_config()
        # Não retornar senhas por segurança
        if 'email' in config and 'smtp_password' in config['email']:
            config['email']['smtp_password'] = '***' if config['email']['smtp_password'] else ''
        if 'database' in config:
            if 'supabase_key' in config['database']:
                config['database']['supabase_key'] = '***' if config['database']['supabase_key'] else ''
            if 'supabase_service_key' in config['database']:
                config['database']['supabase_service_key'] = '***' if config['database']['supabase_service_key'] else ''
        
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/api/config/email', methods=['POST'])
@admin_required
def save_email_config():
    """Salva configurações de email"""
    try:
        data = request.get_json()
        config = load_config()
        
        # Validar dados obrigatórios
        required_fields = ['smtp_server', 'smtp_port', 'smtp_username', 'email_from']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        # Atualizar configurações de email
        config['email'].update(data)
        
        if save_config(config):
            return jsonify({'message': 'Configurações de email salvas com sucesso'})
        else:
            return jsonify({'error': 'Erro ao salvar configurações'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/api/config/email/test', methods=['POST'])
@admin_required
def test_email_config():
    """Testa configurações de email"""
    try:
        config = load_config()
        email_config = config.get('email', {})
        
        # Verificar se as configurações estão completas
        required_fields = ['smtp_server', 'smtp_port', 'smtp_username', 'smtp_password', 'email_from']
        for field in required_fields:
            if not email_config.get(field):
                return jsonify({'error': f'Configuração de email incompleta: {field}'}), 400
        
        # Enviar email de teste
        test_email = session.get('user_email', 'admin@teste.com')
        success = send_test_email(
            to_email=test_email,
            smtp_config=email_config
        )
        
        if success:
            return jsonify({'message': 'Email de teste enviado com sucesso'})
        else:
            return jsonify({'error': 'Falha ao enviar email de teste'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/api/config/system', methods=['POST'])
@admin_required
def save_system_config():
    """Salva configurações do sistema"""
    try:
        data = request.get_json()
        config = load_config()
        
        # Atualizar configurações do sistema
        config['system'].update(data)
        
        if save_config(config):
            return jsonify({'message': 'Configurações do sistema salvas com sucesso'})
        else:
            return jsonify({'error': 'Erro ao salvar configurações'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/api/config/database', methods=['POST'])
@admin_required
def save_database_config():
    """Salva configurações do banco de dados"""
    try:
        data = request.get_json()
        config = load_config()
        
        # Atualizar configurações do banco
        config['database'].update(data)
        
        if save_config(config):
            # Atualizar variáveis de ambiente se for Supabase
            if data.get('db_type') == 'supabase':
                os.environ['SUPABASE_URL'] = data.get('supabase_url', '')
                os.environ['SUPABASE_KEY'] = data.get('supabase_key', '')
                os.environ['SUPABASE_SERVICE_KEY'] = data.get('supabase_service_key', '')
            
            return jsonify({'message': 'Configurações do banco de dados salvas com sucesso'})
        else:
            return jsonify({'error': 'Erro ao salvar configurações'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/api/config/database/test', methods=['POST'])
@admin_required
def test_database_connection():
    """Testa conexão com banco de dados"""
    try:
        config = load_config()
        db_config = config.get('database', {})
        
        if db_config.get('db_type') == 'supabase':
            # Testar conexão com Supabase
            supabase = get_supabase_client()
            if supabase:
                # Fazer uma consulta simples para testar
                result = supabase.table('users').select('id').limit(1).execute()
                return jsonify({'message': 'Conexão com Supabase testada com sucesso'})
            else:
                return jsonify({'error': 'Falha ao conectar com Supabase'}), 500
        else:
            return jsonify({'error': 'Tipo de banco não suportado para teste'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Erro ao testar conexão: {str(e)}'}), 500

@config_bp.route('/api/config/security', methods=['POST'])
@admin_required
def save_security_config():
    """Salva configurações de segurança"""
    try:
        data = request.get_json()
        config = load_config()
        
        # Validar dados
        if 'session_timeout' in data:
            timeout = int(data['session_timeout'])
            if timeout < 5 or timeout > 480:
                return jsonify({'error': 'Timeout deve estar entre 5 e 480 minutos'}), 400
        
        if 'min_password_length' in data:
            min_length = int(data['min_password_length'])
            if min_length < 6 or min_length > 20:
                return jsonify({'error': 'Tamanho mínimo da senha deve estar entre 6 e 20 caracteres'}), 400
        
        # Atualizar configurações de segurança
        config['security'].update(data)
        
        if save_config(config):
            return jsonify({'message': 'Configurações de segurança salvas com sucesso'})
        else:
            return jsonify({'error': 'Erro ao salvar configurações'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/api/config/backup', methods=['POST'])
@admin_required
def backup_config():
    """Cria backup das configurações"""
    try:
        config = load_config()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'config_backup_{timestamp}.json'
        
        with open(backup_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return jsonify({'message': f'Backup criado: {backup_file}'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/api/config/restore', methods=['POST'])
@admin_required
def restore_config():
    """Restaura configurações de um backup"""
    try:
        data = request.get_json()
        backup_file = data.get('backup_file')
        
        if not backup_file or not os.path.exists(backup_file):
            return jsonify({'error': 'Arquivo de backup não encontrado'}), 400
        
        with open(backup_file, 'r') as f:
            config = json.load(f)
        
        if save_config(config):
            return jsonify({'message': 'Configurações restauradas com sucesso'})
        else:
            return jsonify({'error': 'Erro ao restaurar configurações'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

