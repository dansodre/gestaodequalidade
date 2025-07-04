from flask import Blueprint, request, jsonify, session
from user import db, User
from datetime import datetime
import hashlib

users_bp = Blueprint("users", __name__)

def hash_password(password):
    """Hash da senha usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def require_admin():
    """Decorator para verificar se o usuário é admin"""
    if session.get("user_role") != "admin":
        return jsonify({"error": "Acesso negado"}), 403
    return None

@users_bp.route("/api/users", methods=["GET"])
def get_users():
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    try:
        users = User.query.all()
        return jsonify({
            "success": True,
            "users": [user.to_dict() for user in users]
        })
        
    except Exception as e:
        print(f"Erro ao buscar usuários: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@users_bp.route("/api/users", methods=["POST"])
def create_user():
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    try:
        data = request.get_json()
        
        # Verificar se e-mail já existe
        existing_user = User.query.filter_by(email=data["email"]).first()
        
        if existing_user:
            return jsonify({"error": "E-mail já cadastrado"}), 400
        
        new_user = User(
            username=data["username"],
            email=data["email"],
            role=data.get("role", "user")
        )
        new_user.set_password(data["password"])
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            "message": "Usuário criado com sucesso",
            "user": new_user.to_dict()
        }), 201
        
    except Exception as e:
        print(f"Erro ao criar usuário: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@users_bp.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404
        
        data = request.get_json()
        user.username = data.get("username", user.username)
        user.email = data.get("email", user.email)
        user.role = data.get("role", user.role)
        user.status = data.get("status", user.status)
        
        if "password" in data:
            user.set_password(data["password"])
            
        db.session.commit()
        
        return jsonify({
            "message": "Usuário atualizado com sucesso",
            "user": user.to_dict()
        })
        
    except Exception as e:
        print(f"Erro ao atualizar usuário: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@users_bp.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({"message": "Usuário excluído com sucesso"}), 200
        
    except Exception as e:
        print(f"Erro ao excluir usuário: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500


