from flask import Blueprint, request, jsonify, session
from functools import wraps
import hashlib
import secrets
from datetime import datetime
from supabase_client import get_supabase_client

users_bp = Blueprint('users_api', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login required'}), 401
        
        # Verificar se é admin
        user_role = session.get('user_role', 'user')
        if user_role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

def hash_password(password):
    """Gera hash da senha"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + password_hash.hex()

def verify_password(password, hashed):
    """Verifica se a senha está correta"""
    try:
        salt = hashed[:32]
        stored_hash = hashed[32:]
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return password_hash.hex() == stored_hash
    except:
        return False

@users_bp.route('/api/users', methods=['GET'])
@admin_required
def get_users():
    """Retorna lista de usuários"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return jsonify({'error': 'Erro de conexão com banco de dados'}), 500
        
        # Buscar usuários
        result = supabase.table('users').select('*').execute()
        
        users = []
        for user in result.data:
            # Não retornar senha
            user_data = {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user.get('role', 'user'),
                'is_active': user.get('is_active', True),
                'created_at': user.get('created_at'),
                'last_login': user.get('last_login')
            }
            users.append(user_data)
        
        return jsonify({'users': users})
        
    except Exception as e:
        print(f"Erro ao buscar usuários: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@users_bp.route('/api/users', methods=['POST'])
@admin_required
def create_user():
    """Cria novo usuário"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        username = data['username']
        email = data['email']
        password = data['password']
        role = data['role']
        
        # Validar role
        if role not in ['admin', 'user']:
            return jsonify({'error': 'Role deve ser admin ou user'}), 400
        
        # Validar senha
        if len(password) < 6:
            return jsonify({'error': 'Senha deve ter pelo menos 6 caracteres'}), 400
        
        supabase = get_supabase_client()
        if not supabase:
            return jsonify({'error': 'Erro de conexão com banco de dados'}), 500
        
        # Verificar se usuário já existe
        existing_user = supabase.table('users').select('id').eq('email', email).execute()
        if existing_user.data:
            return jsonify({'error': 'Email já está em uso'}), 400
        
        existing_username = supabase.table('users').select('id').eq('username', username).execute()
        if existing_username.data:
            return jsonify({'error': 'Nome de usuário já está em uso'}), 400
        
        # Hash da senha
        password_hash = hash_password(password)
        
        # Criar usuário
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'role': role,
            'is_active': True,
            'created_at': datetime.now().isoformat()
        }
        
        result = supabase.table('users').insert(user_data).execute()
        
        if result.data:
            user = result.data[0]
            return jsonify({
                'message': 'Usuário criado com sucesso',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'role': user['role'],
                    'is_active': user['is_active']
                }
            }), 201
        else:
            return jsonify({'error': 'Erro ao criar usuário'}), 500
            
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@users_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Atualiza usuário"""
    try:
        data = request.get_json()
        
        supabase = get_supabase_client()
        if not supabase:
            return jsonify({'error': 'Erro de conexão com banco de dados'}), 500
        
        # Verificar se usuário existe
        existing_user = supabase.table('users').select('*').eq('id', user_id).execute()
        if not existing_user.data:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        update_data = {}
        
        # Campos que podem ser atualizados
        if 'username' in data:
            # Verificar se username já existe (exceto o próprio usuário)
            existing_username = supabase.table('users').select('id').eq('username', data['username']).neq('id', user_id).execute()
            if existing_username.data:
                return jsonify({'error': 'Nome de usuário já está em uso'}), 400
            update_data['username'] = data['username']
        
        if 'email' in data:
            # Verificar se email já existe (exceto o próprio usuário)
            existing_email = supabase.table('users').select('id').eq('email', data['email']).neq('id', user_id).execute()
            if existing_email.data:
                return jsonify({'error': 'Email já está em uso'}), 400
            update_data['email'] = data['email']
        
        if 'role' in data:
            if data['role'] not in ['admin', 'user']:
                return jsonify({'error': 'Role deve ser admin ou user'}), 400
            update_data['role'] = data['role']
        
        if 'is_active' in data:
            update_data['is_active'] = bool(data['is_active'])
        
        if 'password' in data and data['password']:
            if len(data['password']) < 6:
                return jsonify({'error': 'Senha deve ter pelo menos 6 caracteres'}), 400
            update_data['password_hash'] = hash_password(data['password'])
        
        if not update_data:
            return jsonify({'error': 'Nenhum campo para atualizar'}), 400
        
        update_data['updated_at'] = datetime.now().isoformat()
        
        # Atualizar usuário
        result = supabase.table('users').update(update_data).eq('id', user_id).execute()
        
        if result.data:
            user = result.data[0]
            return jsonify({
                'message': 'Usuário atualizado com sucesso',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'role': user['role'],
                    'is_active': user['is_active']
                }
            })
        else:
            return jsonify({'error': 'Erro ao atualizar usuário'}), 500
            
    except Exception as e:
        print(f"Erro ao atualizar usuário: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@users_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Exclui usuário"""
    try:
        # Não permitir excluir o próprio usuário
        if session.get('user_id') == user_id:
            return jsonify({'error': 'Não é possível excluir seu próprio usuário'}), 400
        
        supabase = get_supabase_client()
        if not supabase:
            return jsonify({'error': 'Erro de conexão com banco de dados'}), 500
        
        # Verificar se usuário existe
        existing_user = supabase.table('users').select('*').eq('id', user_id).execute()
        if not existing_user.data:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Excluir usuário
        result = supabase.table('users').delete().eq('id', user_id).execute()
        
        return jsonify({'message': 'Usuário excluído com sucesso'})
        
    except Exception as e:
        print(f"Erro ao excluir usuário: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@users_bp.route('/api/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Ativa/desativa usuário"""
    try:
        # Não permitir desativar o próprio usuário
        if session.get('user_id') == user_id:
            return jsonify({'error': 'Não é possível desativar seu próprio usuário'}), 400
        
        supabase = get_supabase_client()
        if not supabase:
            return jsonify({'error': 'Erro de conexão com banco de dados'}), 500
        
        # Buscar usuário atual
        existing_user = supabase.table('users').select('*').eq('id', user_id).execute()
        if not existing_user.data:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        user = existing_user.data[0]
        new_status = not user.get('is_active', True)
        
        # Atualizar status
        result = supabase.table('users').update({
            'is_active': new_status,
            'updated_at': datetime.now().isoformat()
        }).eq('id', user_id).execute()
        
        if result.data:
            status_text = 'ativado' if new_status else 'desativado'
            return jsonify({'message': f'Usuário {status_text} com sucesso'})
        else:
            return jsonify({'error': 'Erro ao atualizar status do usuário'}), 500
            
    except Exception as e:
        print(f"Erro ao alterar status do usuário: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@users_bp.route('/api/users/stats', methods=['GET'])
@admin_required
def get_users_stats():
    """Retorna estatísticas de usuários"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return jsonify({'error': 'Erro de conexão com banco de dados'}), 500
        
        # Buscar todos os usuários
        result = supabase.table('users').select('role, is_active').execute()
        
        total_users = len(result.data)
        admin_users = len([u for u in result.data if u.get('role') == 'admin'])
        active_users = len([u for u in result.data if u.get('is_active', True)])
        
        return jsonify({
            'total_users': total_users,
            'admin_users': admin_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users
        })
        
    except Exception as e:
        print(f"Erro ao buscar estatísticas: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@users_bp.route('/api/users/search', methods=['GET'])
@admin_required
def search_users():
    """Busca usuários por termo"""
    try:
        search_term = request.args.get('q', '').strip()
        role_filter = request.args.get('role', '').strip()
        
        supabase = get_supabase_client()
        if not supabase:
            return jsonify({'error': 'Erro de conexão com banco de dados'}), 500
        
        # Construir query
        query = supabase.table('users').select('*')
        
        if role_filter and role_filter in ['admin', 'user']:
            query = query.eq('role', role_filter)
        
        if search_term:
            # Buscar por username ou email
            query = query.or_(f'username.ilike.%{search_term}%,email.ilike.%{search_term}%')
        
        result = query.execute()
        
        users = []
        for user in result.data:
            user_data = {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user.get('role', 'user'),
                'is_active': user.get('is_active', True),
                'created_at': user.get('created_at'),
                'last_login': user.get('last_login')
            }
            users.append(user_data)
        
        return jsonify({'users': users})
        
    except Exception as e:
        print(f"Erro ao buscar usuários: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

