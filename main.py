import os
import sys
# DON'T CHANGE THIS LINE
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import hashlib
import secrets
from functools import wraps

# Importar blueprints
from auth import auth_bp
from plans import plans_bp
from users_api import users_bp
from config_api import config_bp

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Configurar CORS
CORS(app, supports_credentials=True)

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(plans_bp)
app.register_blueprint(users_bp)
app.register_blueprint(config_bp)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/login.html')
def login_page():
    return send_from_directory('.', 'login.html')

@app.route('/styles.css')
def styles():
    return send_from_directory('.', 'styles.css')

@app.route('/script.js')
def script():
    return send_from_directory('.', 'script.js')

@app.route('/favicon.ico')
def favicon():
    return '', 404

# Rota para verificar status da sessão
@app.route('/api/session/status')
def session_status():
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'user_id': session['user_id'],
            'username': session.get('username'),
            'role': session.get('user_role', 'user')
        })
    else:
        return jsonify({'logged_in': False})

# Rota para logout
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout realizado com sucesso'})

# Rota de health check
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# Middleware para verificar sessão expirada
@app.before_request
def check_session_timeout():
    if 'user_id' in session:
        last_activity = session.get('last_activity')
        if last_activity:
            last_activity = datetime.fromisoformat(last_activity)
            if datetime.now() - last_activity > timedelta(hours=2):  # 2 horas de timeout
                session.clear()
                if request.path.startswith('/api/'):
                    return jsonify({'error': 'Sessão expirada'}), 401
        
        # Atualizar última atividade
        session['last_activity'] = datetime.now().isoformat()

# Handler de erro 404
@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Endpoint não encontrado'}), 404
    return redirect(url_for('index'))

# Handler de erro 500
@app.errorhandler(500)
def internal_error(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Erro interno do servidor'}), 500
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Criar usuário admin padrão se não existir
    try:
        from supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        if supabase:
            # Verificar se existe usuário admin
            admin_check = supabase.table('users').select('id').eq('email', 'eng.danilosodre@gmail.com').execute()
            
            if not admin_check.data:
                # Criar usuário admin padrão
                salt = secrets.token_hex(16)
                password = 'adm123'
                password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
                full_hash = salt + password_hash.hex()
                
                admin_data = {
                    'username': 'admin',
                    'email': 'eng.danilosodre@gmail.com',
                    'password_hash': full_hash,
                    'role': 'admin',
                    'is_active': True,
                    'created_at': datetime.now().isoformat()
                }
                
                result = supabase.table('users').insert(admin_data).execute()
                if result.data:
                    print("Usuário admin criado com sucesso!")
                else:
                    print("Erro ao criar usuário admin")
            else:
                print("Usuário admin já existe")
    except Exception as e:
        print(f"Erro ao verificar/criar usuário admin: {e}")
    
    app.run(debug=True, host='0.0.0.0', port=5001)

