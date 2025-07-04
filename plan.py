from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from user import db

class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sector = db.Column(db.String(100), nullable=False)
    responsible_person = db.Column(db.String(100), nullable=False)
    responsible_email = db.Column(db.String(120), nullable=False)
    creation_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'in-progress', 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relacionamento com ações
    actions = db.relationship('Action', backref='plan', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Plan {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sector': self.sector,
            'responsible_person': self.responsible_person,
            'responsible_email': self.responsible_email,
            'creation_date': self.creation_date.isoformat() if self.creation_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'actions': [action.to_dict() for action in self.actions]
        }

class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    responsible_person = db.Column(db.String(100), nullable=False)
    responsible_email = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    justification = db.Column(db.Text, nullable=False)
    estimated_cost = db.Column(db.Float, default=0.0)
    resource_source = db.Column(db.String(200))
    execution_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'in-progress', 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Chave estrangeira para o plano
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)

    def __repr__(self):
        return f'<Action {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'responsible_person': self.responsible_person,
            'responsible_email': self.responsible_email,
            'description': self.description,
            'justification': self.justification,
            'estimated_cost': self.estimated_cost,
            'resource_source': self.resource_source,
            'execution_date': self.execution_date.isoformat() if self.execution_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'plan_id': self.plan_id
        }

