"""
Database models for Protokolant application
"""

from datetime import datetime
from .app import db

class Protocol(db.Model):
    """Model representing a meeting protocol"""
    __tablename__ = 'protocols'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    participants = db.relationship('Participant', backref='protocol', lazy=True, cascade='all, delete-orphan')
    agenda_items = db.relationship('AgendaItem', backref='protocol', lazy=True, cascade='all, delete-orphan')
    action_items = db.relationship('ActionItem', backref='protocol', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Protocol {self.title}>'

class Participant(db.Model):
    """Model representing a meeting participant"""
    __tablename__ = 'participants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    protocol_id = db.Column(db.Integer, db.ForeignKey('protocols.id'), nullable=False)
    
    def __repr__(self):
        return f'<Participant {self.name}>'

class AgendaItem(db.Model):
    """Model representing an agenda item in a meeting"""
    __tablename__ = 'agenda_items'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    discussion = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    protocol_id = db.Column(db.Integer, db.ForeignKey('protocols.id'), nullable=False)
    
    def __repr__(self):
        return f'<AgendaItem {self.title}>'

class ActionItem(db.Model):
    """Model representing an action item from a meeting"""
    __tablename__ = 'action_items'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    assignee = db.Column(db.String(100), nullable=False)
    deadline = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending, completed
    protocol_id = db.Column(db.Integer, db.ForeignKey('protocols.id'), nullable=False)
    
    def __repr__(self):
        return f'<ActionItem {self.description[:30]}>'
