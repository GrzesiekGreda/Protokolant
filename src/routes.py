"""
Web routes for Protokolant application
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import os
from .app import db
from .models import Protocol, Participant, AgendaItem, ActionItem
from .speech_to_text import SpeechToTextProcessor, record_speech_to_text
from .voice_config import VoiceCommandsConfig

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

@bp.route('/api/record-speech', methods=['POST'])
def record_speech():
    """
    API endpoint do nagrywania i transkrypcji mowy
    Parametry POST:
        - duration: Czas nagrywania w sekundach (opcjonalny)
        - field: Pole do którego ma być wpisany tekst (opcjonalny)
    """
    try:
        # Pobierz parametry
        data = request.get_json() or {}
        duration = data.get('duration', None)
        field = data.get('field', 'general')
        
        # Nagrywanie i transkrypcja
        result = record_speech_to_text(
            duration=duration,
            save_audio=True,
            save_text=False
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'text': result['text'],
                'audio_path': result['audio_path'],
                'message': 'Transkrypcja zakończona pomyślnie'
            })
        else:
            return jsonify({
                'success': False,
                'errors': result['errors'],
                'message': 'Błąd podczas transkrypcji'
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Błąd serwera: {str(e)}'
        }), 500

@bp.route('/api/transcribe-file', methods=['POST'])
def transcribe_file():
    """
    API endpoint do transkrypcji wgranego pliku audio
    """
    try:
        # Sprawdź czy plik został wgrany
        if 'audio_file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'Brak pliku audio'
            }), 400
        
        file = request.files['audio_file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'Nie wybrano pliku'
            }), 400
        
        # Zapisz plik tymczasowo
        upload_dir = 'uploads'
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Transkrypcja
        processor = SpeechToTextProcessor()
        result = processor.transcribe_from_file(
            file_path=filepath,
            apply_corrections=True
        )
        processor.cleanup()
        
        # Usuń plik tymczasowy
        if os.path.exists(filepath):
            os.remove(filepath)
        
        if result['success']:
            return jsonify({
                'success': True,
                'text': result['text'],
                'message': 'Transkrypcja zakończona pomyślnie'
            })
        else:
            return jsonify({
                'success': False,
                'errors': result['errors'],
                'message': 'Błąd podczas transkrypcji'
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Błąd serwera: {str(e)}'
        }), 500

@bp.route('/api/voice-command', methods=['POST'])
def voice_command():
    """
    API endpoint do przetwarzania poleceń głosowych
    Parametry POST:
        - duration: Czas nagrywania w sekundach (opcjonalny)
        - process_commands: Czy przetwarzać polecenia głosowe (domyślnie true)
    """
    try:
        data = request.get_json() or {}
        duration = data.get('duration', None)
        process_commands = data.get('process_commands', True)
        
        # Utwórz procesor z włączonymi poleceniami głosowymi
        processor = SpeechToTextProcessor(enable_voice_commands=True)
        
        result = processor.record_and_transcribe(
            duration=duration,
            save_audio=True,
            apply_corrections=True,
            process_commands=process_commands
        )
        
        if result['success']:
            response_data = {
                'success': True,
                'text': result['text'],
                'audio_path': result['audio_path'],
                'message': 'Przetwarzanie zakończone pomyślnie'
            }
            
            # Dodaj informacje o poleceniu jeśli było wykryte
            if result.get('command_info'):
                cmd_info = result['command_info']
                response_data['command_info'] = {
                    'is_command': cmd_info['is_command'],
                    'command_executed': cmd_info['command_executed'],
                    'message': cmd_info['message']
                }
                
                # Pobierz aktualny tekst dokumentu
                response_data['current_document'] = processor.get_current_document_text()
                response_data['statistics'] = processor.get_document_statistics()
            
            processor.cleanup()
            return jsonify(response_data)
        else:
            processor.cleanup()
            return jsonify({
                'success': False,
                'errors': result['errors'],
                'message': 'Błąd podczas przetwarzania'
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Błąd serwera API voice-command: {str(e)}'
        }), 500

# === ENDPOINTY DO ZARZĄDZANIA KONFIGURACJĄ POLECEŃ GŁOSOWYCH ===

@bp.route('/settings/voice-commands')
def voice_commands_settings():
    """
    Strona ustawień poleceń głosowych
    """
    config = VoiceCommandsConfig()
    return render_template('voice_commands_settings.html', config=config)

@bp.route('/api/voice-config', methods=['GET'])
def get_voice_config():
    """
    API: Pobiera aktualną konfigurację poleceń głosowych
    """
    try:
        config = VoiceCommandsConfig()
        
        return jsonify({
            'success': True,
            'trigger_word': config.get_trigger_word(),
            'commands': config.get_all_commands(),
            'statistics': config.get_statistics()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Błąd: {str(e)}'
        }), 500

@bp.route('/api/voice-config/trigger-word', methods=['POST'])
def update_trigger_word():
    """
    API: Aktualizuje słowo aktywujące
    Body: {"trigger_word": "nowe_słowo"}
    """
    try:
        data = request.get_json()
        new_trigger = data.get('trigger_word')
        
        if not new_trigger:
            return jsonify({
                'success': False,
                'message': 'Brak parametru trigger_word'
            }), 400
        
        config = VoiceCommandsConfig()
        success, message = config.set_trigger_word(new_trigger)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'trigger_word': config.get_trigger_word()
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Błąd: {str(e)}'
        }), 500

@bp.route('/api/voice-config/command', methods=['POST'])
def add_voice_command():
    """
    API: Dodaje nowe polecenie
    Body: {
        "command_phrase": "fraza",
        "action": "akcja",
        "description": "opis",
        "aliases": [],
        "enabled": true
    }
    """
    try:
        data = request.get_json()
        
        config = VoiceCommandsConfig()
        success, message = config.add_command(
            command_phrase=data.get('command_phrase'),
            action=data.get('action'),
            description=data.get('description', ''),
            aliases=data.get('aliases', []),
            enabled=data.get('enabled', True)
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'commands': config.get_all_commands()
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Błąd: {str(e)}'
        }), 500

@bp.route('/api/voice-config/command/<command_phrase>', methods=['PUT'])
def update_voice_command(command_phrase):
    """
    API: Aktualizuje istniejące polecenie
    """
    try:
        data = request.get_json()
        
        config = VoiceCommandsConfig()
        success, message = config.update_command(
            command_phrase=command_phrase,
            new_phrase=data.get('new_phrase'),
            action=data.get('action'),
            description=data.get('description'),
            aliases=data.get('aliases'),
            enabled=data.get('enabled')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'commands': config.get_all_commands()
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Błąd: {str(e)}'
        }), 500

@bp.route('/api/voice-config/command/<command_phrase>', methods=['DELETE'])
def delete_voice_command(command_phrase):
    """
    API: Usuwa polecenie
    """
    try:
        config = VoiceCommandsConfig()
        success, message = config.delete_command(command_phrase)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'commands': config.get_all_commands()
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Błąd: {str(e)}'
        }), 500

@bp.route('/api/voice-config/command/<command_phrase>/toggle', methods=['POST'])
def toggle_voice_command(command_phrase):
    """
    API: Przełącza status włączenia/wyłączenia polecenia
    """
    try:
        config = VoiceCommandsConfig()
        success, message = config.toggle_command(command_phrase)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'commands': config.get_all_commands()
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Błąd: {str(e)}'
        }), 500

@bp.route('/api/voice-config/reset', methods=['POST'])
def reset_voice_config():
    """
    API: Resetuje konfigurację do wartości domyślnych
    """
    try:
        config = VoiceCommandsConfig()
        success, message = config.reset_to_defaults()
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'trigger_word': config.get_trigger_word(),
                'commands': config.get_all_commands()
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Błąd: {str(e)}'
        }), 500
