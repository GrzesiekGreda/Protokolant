"""
Web routes for Protokolant application
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from .app import db
from .models import Protocol, Participant, AgendaItem, ActionItem

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Display list of all protocols"""
    protocols = Protocol.query.order_by(Protocol.date.desc()).all()
    return render_template('index.html', protocols=protocols)

@bp.route('/protocol/new', methods=['GET', 'POST'])
def new_protocol():
    """Create a new protocol"""
    if request.method == 'POST':
        try:
            # Create protocol
            protocol = Protocol(
                title=request.form['title'],
                date=datetime.strptime(request.form['date'], '%Y-%m-%dT%H:%M'),
                location=request.form.get('location', '')
            )
            db.session.add(protocol)
            db.session.flush()  # Get protocol ID
            
            # Add participants
            participants_data = request.form.getlist('participants[]')
            for name in participants_data:
                if name.strip():
                    participant = Participant(name=name.strip(), protocol_id=protocol.id)
                    db.session.add(participant)
            
            # Add agenda items
            agenda_titles = request.form.getlist('agenda_title[]')
            agenda_discussions = request.form.getlist('agenda_discussion[]')
            for i, title in enumerate(agenda_titles):
                if title.strip():
                    agenda = AgendaItem(
                        title=title.strip(),
                        discussion=agenda_discussions[i] if i < len(agenda_discussions) else '',
                        order=i,
                        protocol_id=protocol.id
                    )
                    db.session.add(agenda)
            
            # Add action items
            action_descriptions = request.form.getlist('action_description[]')
            action_assignees = request.form.getlist('action_assignee[]')
            action_deadlines = request.form.getlist('action_deadline[]')
            for i, description in enumerate(action_descriptions):
                if description.strip():
                    deadline_str = action_deadlines[i] if i < len(action_deadlines) else None
                    deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None
                    
                    action = ActionItem(
                        description=description.strip(),
                        assignee=action_assignees[i] if i < len(action_assignees) else '',
                        deadline=deadline,
                        protocol_id=protocol.id
                    )
                    db.session.add(action)
            
            db.session.commit()
            flash('Protokół został utworzony pomyślnie!', 'success')
            return redirect(url_for('main.view_protocol', protocol_id=protocol.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Błąd podczas tworzenia protokołu: {str(e)}', 'error')
            return redirect(url_for('main.new_protocol'))
    
    return render_template('create_protocol.html')

@bp.route('/protocol/<int:protocol_id>')
def view_protocol(protocol_id):
    """View a specific protocol"""
    protocol = Protocol.query.get_or_404(protocol_id)
    return render_template('view_protocol.html', protocol=protocol)

@bp.route('/protocol/<int:protocol_id>/delete', methods=['POST'])
def delete_protocol(protocol_id):
    """Delete a protocol"""
    try:
        protocol = Protocol.query.get_or_404(protocol_id)
        db.session.delete(protocol)
        db.session.commit()
        flash('Protokół został usunięty.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Błąd podczas usuwania protokołu: {str(e)}', 'error')
    
    return redirect(url_for('main.index'))
