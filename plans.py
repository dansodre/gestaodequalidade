from flask import Blueprint, request, jsonify, session
from functools import wraps
from datetime import datetime
from email_service import get_email_service
from supabase_client import get_supabase_client

plans_bp = Blueprint('plans', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@plans_bp.route('/api/plans', methods=['GET'])
@login_required
def get_plans():
    """Retorna lista de planos"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            # Retornar dados mockados se não houver conexão
            return jsonify({'plans': []})
        
        # Buscar planos do usuário
        result = supabase.table('plans').select('*').execute()
        
        plans = []
        for plan in result.data:
            plan_data = {
                'id': plan['id'],
                'name': plan['name'],
                'sector': plan['sector'],
                'responsible_person': plan['responsible_person'],
                'responsible_email': plan['responsible_email'],
                'creation_date': plan['creation_date'],
                'status': plan.get('status', 'pending'),
                'created_at': plan.get('created_at')
            }
            plans.append(plan_data)
        
        return jsonify({'plans': plans})
        
    except Exception as e:
        print(f"Erro ao buscar planos: {e}")
        return jsonify({'plans': []})

@plans_bp.route('/api/plans', methods=['POST'])
@login_required
def create_plan():
    """Cria novo plano"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['name', 'sector', 'responsible_person', 'responsible_email', 'creation_date']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        supabase = get_supabase_client()
        if not supabase:
            return jsonify({'error': 'Erro de conexão com banco de dados'}), 500
        
        # Criar plano
        plan_data = {
            'name': data['name'],
            'sector': data['sector'],
            'responsible_person': data['responsible_person'],
            'responsible_email': data['responsible_email'],
            'creation_date': data['creation_date'],
            'status': 'pending',
            'created_by': session['user_id'],
            'created_at': datetime.now().isoformat()
        }
        
        result = supabase.table('plans').insert(plan_data).execute()
        
        if result.data:
            plan = result.data[0]
            return jsonify({
                'message': 'Plano criado com sucesso',
                'plan': plan
            }), 201
        else:
            return jsonify({'error': 'Erro ao criar plano'}), 500
            
    except Exception as e:
        print(f"Erro ao criar plano: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@plans_bp.route('/api/plans/<int:plan_id>/actions', methods=['POST'])
@login_required
def create_action(plan_id):
    """Cria nova ação para um plano"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['title', 'responsible_person', 'justification', 'responsible_email', 'execution_date']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        supabase = get_supabase_client()
        if not supabase:
            return jsonify({'error': 'Erro de conexão com banco de dados'}), 500
        
        # Verificar se o plano existe
        plan_result = supabase.table('plans').select('*').eq('id', plan_id).execute()
        if not plan_result.data:
            return jsonify({'error': 'Plano não encontrado'}), 404
        
        # Criar ação
        action_data = {
            'plan_id': plan_id,
            'title': data['title'],
            'responsible_person': data['responsible_person'],
            'description': data.get('description', ''),
            'justification': data['justification'],
            'responsible_email': data['responsible_email'],
            'estimated_cost': float(data.get('estimated_cost', 0)),
            'resource_source': data.get('resource_source', ''),
            'execution_date': data['execution_date'],
            'status': 'pending',
            'created_by': session['user_id'],
            'created_at': datetime.now().isoformat()
        }
        
        result = supabase.table('actions').insert(action_data).execute()
        
        if result.data:
            action = result.data[0]
            
            # Enviar email para o responsável pela ação
            try:
                email_service = get_email_service()
                plan = plan_result.data[0]
                
                subject = f"Nova Ação Atribuída: {action['title']}"
                body = f"""
Olá {action['responsible_person']},

Uma nova ação foi atribuída a você no plano "{plan['name']}":

Título: {action['title']}
Descrição: {action['description']}
Justificativa: {action['justification']}
Data de Execução: {action['execution_date']}
Custo Estimado: R$ {action['estimated_cost']:.2f}

Por favor, revise e tome as medidas necessárias.

Atenciosamente,
Sistema de Gestão de Qualidade
"""
                
                email_service.send_email(
                    to_email=action['responsible_email'],
                    subject=subject,
                    body=body
                )
                
            except Exception as e:
                print(f"Erro ao enviar email: {e}")
            
            return jsonify({
                'message': 'Ação criada com sucesso',
                'action': action
            }), 201
        else:
            return jsonify({'error': 'Erro ao criar ação'}), 500
            
    except Exception as e:
        print(f"Erro ao criar ação: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@plans_bp.route('/api/plans/<int:plan_id>/actions', methods=['GET'])
@login_required
def get_plan_actions(plan_id):
    """Retorna ações de um plano"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return jsonify({'actions': []})
        
        # Buscar ações do plano
        result = supabase.table('actions').select('*').eq('plan_id', plan_id).execute()
        
        actions = []
        for action in result.data:
            action_data = {
                'id': action['id'],
                'title': action['title'],
                'responsible_person': action['responsible_person'],
                'description': action.get('description', ''),
                'justification': action['justification'],
                'responsible_email': action['responsible_email'],
                'estimated_cost': action.get('estimated_cost', 0),
                'resource_source': action.get('resource_source', ''),
                'execution_date': action['execution_date'],
                'status': action.get('status', 'pending'),
                'created_at': action.get('created_at')
            }
            actions.append(action_data)
        
        return jsonify({'actions': actions})
        
    except Exception as e:
        print(f"Erro ao buscar ações: {e}")
        return jsonify({'actions': []})

@plans_bp.route('/api/plans/<int:plan_id>', methods=['GET'])
@login_required
def get_plan(plan_id):
    """Retorna detalhes de um plano"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return jsonify({'error': 'Erro de conexão com banco de dados'}), 500
        
        # Buscar plano
        plan_result = supabase.table('plans').select('*').eq('id', plan_id).execute()
        if not plan_result.data:
            return jsonify({'error': 'Plano não encontrado'}), 404
        
        plan = plan_result.data[0]
        
        # Buscar ações do plano
        actions_result = supabase.table('actions').select('*').eq('plan_id', plan_id).execute()
        
        plan_data = {
            'id': plan['id'],
            'name': plan['name'],
            'sector': plan['sector'],
            'responsible_person': plan['responsible_person'],
            'responsible_email': plan['responsible_email'],
            'creation_date': plan['creation_date'],
            'status': plan.get('status', 'pending'),
            'created_at': plan.get('created_at'),
            'actions': actions_result.data
        }
        
        return jsonify({'plan': plan_data})
        
    except Exception as e:
        print(f"Erro ao buscar plano: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@plans_bp.route('/api/plans/<int:plan_id>/send-email', methods=['POST'])
@login_required
def send_plan_email(plan_id):
    """Envia email com o plano de ação completo"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return jsonify({'error': 'Erro de conexão com banco de dados'}), 500
        
        # Buscar plano
        plan_result = supabase.table('plans').select('*').eq('id', plan_id).execute()
        if not plan_result.data:
            return jsonify({'error': 'Plano não encontrado'}), 404
        
        plan = plan_result.data[0]
        
        # Buscar ações do plano
        actions_result = supabase.table('actions').select('*').eq('plan_id', plan_id).execute()
        actions = actions_result.data
        
        if not actions:
            return jsonify({'error': 'Plano não possui ações'}), 400
        
        # Enviar email
        email_service = get_email_service()
        success = email_service.send_action_plan_email(
            to_email=plan['responsible_email'],
            plan_name=plan['name'],
            actions=actions,
            responsible_person=plan['responsible_person']
        )
        
        if success:
            return jsonify({'message': 'Email enviado com sucesso'})
        else:
            return jsonify({'error': 'Erro ao enviar email'}), 500
            
    except Exception as e:
        print(f"Erro ao enviar email do plano: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@plans_bp.route('/api/plans/<int:plan_id>', methods=['PUT'])
@login_required
def update_plan(plan_id):
    """Atualiza um plano"""
    try:
        data = request.get_json()
        
        supabase = get_supabase_client()
        if not supabase:
            return jsonify({'error': 'Erro de conexão com banco de dados'}), 500
        
        # Verificar se plano existe
        existing_plan = supabase.table('plans').select('*').eq('id', plan_id).execute()
        if not existing_plan.data:
            return jsonify({'error': 'Plano não encontrado'}), 404
        
        update_data = {}
        
        # Campos que podem ser atualizados
        allowed_fields = ['name', 'sector', 'responsible_person', 'responsible_email', 'status']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify({'error': 'Nenhum campo para atualizar'}), 400
        
        update_data['updated_at'] = datetime.now().isoformat()
        
        # Atualizar plano
        result = supabase.table('plans').update(update_data).eq('id', plan_id).execute()
        
        if result.data:
            return jsonify({
                'message': 'Plano atualizado com sucesso',
                'plan': result.data[0]
            })
        else:
            return jsonify({'error': 'Erro ao atualizar plano'}), 500
            
    except Exception as e:
        print(f"Erro ao atualizar plano: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@plans_bp.route('/api/plans/<int:plan_id>', methods=['DELETE'])
@login_required
def delete_plan(plan_id):
    """Exclui um plano"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return jsonify({'error': 'Erro de conexão com banco de dados'}), 500
        
        # Verificar se plano existe
        existing_plan = supabase.table('plans').select('*').eq('id', plan_id).execute()
        if not existing_plan.data:
            return jsonify({'error': 'Plano não encontrado'}), 404
        
        # Excluir ações do plano primeiro
        supabase.table('actions').delete().eq('plan_id', plan_id).execute()
        
        # Excluir plano
        result = supabase.table('plans').delete().eq('id', plan_id).execute()
        
        return jsonify({'message': 'Plano excluído com sucesso'})
        
    except Exception as e:
        print(f"Erro ao excluir plano: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

