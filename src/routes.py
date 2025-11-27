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

@bp.route('/protocol/<int:protocol_id>/edit', methods=['GET', 'POST'])
def edit_protocol(protocol_id):
    """Edit an existing protocol"""
    protocol = Protocol.query.get_or_404(protocol_id)
    
    if request.method == 'POST':
        try:
            # Update protocol
            protocol.title = request.form['title']
            protocol.date = datetime.strptime(request.form['date'], '%Y-%m-%dT%H:%M')
            protocol.location = request.form.get('location', '')
            
            # Clear existing participants and add new ones
            Participant.query.filter_by(protocol_id=protocol.id).delete()
            participants_data = request.form.getlist('participants[]')
            for name in participants_data:
                if name.strip():
                    participant = Participant(name=name.strip(), protocol_id=protocol.id)
                    db.session.add(participant)
            
            # Clear existing agenda items and add new ones
            AgendaItem.query.filter_by(protocol_id=protocol.id).delete()
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
            
            # Clear existing action items and add new ones
            ActionItem.query.filter_by(protocol_id=protocol.id).delete()
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
            flash('Protokół został zaktualizowany pomyślnie!', 'success')
            return redirect(url_for('main.view_protocol', protocol_id=protocol.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Błąd podczas aktualizacji protokołu: {str(e)}', 'error')
            return redirect(url_for('main.edit_protocol', protocol_id=protocol_id))
    
    return render_template('edit_protocol.html', protocol=protocol)

@bp.route('/protocol/<int:protocol_id>/pdf')
def generate_pdf(protocol_id):
    """Generate PDF document from protocol"""
    from flask import send_file
    from .utils import generate_protocol_pdf
    import tempfile
    import re
    
    protocol = Protocol.query.get_or_404(protocol_id)
    
    # Create filename from participants and date
    participants_names = []
    for participant in protocol.participants[:3]:  # Max 3 names
        # Get last name (last word in name)
        name_parts = participant.name.strip().split()
        if name_parts:
            participants_names.append(name_parts[-1])
    
    # Format date
    date_str = protocol.date.strftime('%Y%m%d')
    
    # Create filename
    if participants_names:
        filename = f"Protokol_{'-'.join(participants_names)}_{date_str}.pdf"
    else:
        filename = f"Protokol_{date_str}.pdf"
    
    # Remove special characters from filename
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'[-\s]+', '_', filename)
    
    # Generate PDF in temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    try:
        generate_protocol_pdf(protocol, temp_file.name)
        return send_file(
            temp_file.name,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Błąd podczas generowania PDF: {str(e)}', 'error')
        return redirect(url_for('main.view_protocol', protocol_id=protocol_id))

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
    API endpoint do nagrywania i transkrypcji mowy - krótkie fragmenty (5s)
    Parametry POST:
        - chunk_duration: Długość fragmentu w sekundach (domyślnie 5s)
        - field: Pole do którego ma być wpisany tekst (opcjonalny)
    """
    try:
        # Pobierz parametry
        data = request.get_json() or {}
        chunk_duration = data.get('chunk_duration', 5)  # Krótkie fragmenty dla quasi-realtime
        field = data.get('field', 'general')
        
        # Utwórz procesor bez poleceń głosowych
        processor = SpeechToTextProcessor(enable_voice_commands=False)
        
        # Nagrywanie i transkrypcja krótkiego fragmentu
        result = processor.record_and_transcribe(
            duration=chunk_duration,
            save_audio=True,
            apply_corrections=False  # Wyłącz korekty dla szybkości
        )
        processor.cleanup()
        
        if result['success']:
            return jsonify({
                'success': True,
                'text': result['text'],
                'audio_path': result['audio_path'],
                'message': 'Fragment przetworzony pomyślnie'
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


# ================================================================================
# WebSocket Handlers - Strumieniowe rozpoznawanie mowy
# ================================================================================

from flask_socketio import emit
from .app import socketio
from .streaming_recognition import StreamingRecognizer
import logging

logger = logging.getLogger(__name__)

# Słownik aktywnych sesji rozpoznawania (session_id -> recognizer)
active_recognizers = {}

@socketio.on('connect')
def handle_connect():
    """Klient połączył się przez WebSocket"""
    logger.info(f"✅ Klient połączony: {request.sid}")
    emit('connected', {'message': 'Połączono z serwerem'})

@socketio.on('disconnect')
def handle_disconnect():
    """Klient rozłączył się"""
    logger.info(f"❌ Klient rozłączony: {request.sid}")
    # Zatrzymaj rozpoznawanie jeśli było aktywne
    if request.sid in active_recognizers:
        active_recognizers[request.sid].stop()
        del active_recognizers[request.sid]

@socketio.on('start_recording')
def handle_start_recording(data):
    """
    Rozpocznij strumieniowe rozpoznawanie mowy
    Data: {'language': 'pl-PL'}
    """
    try:
        session_id = request.sid
        language = data.get('language', 'pl-PL')
        
        logger.info(f"🎤 Rozpoczynam nagrywanie dla sesji: {session_id}")
        
        # Jeśli już trwa nagrywanie dla tej sesji, zatrzymaj je
        if session_id in active_recognizers:
            active_recognizers[session_id].stop()
            del active_recognizers[session_id]
        
        # Funkcja callback do wysyłania rozpoznanego tekstu
        def send_recognition(text: str, is_final: bool):
            socketio.emit('recognition_result', {
                'text': text,
                'is_final': is_final
            }, room=session_id)
        
        # Utwórz i uruchom rozpoznawanie
        recognizer = StreamingRecognizer(callback=send_recognition, language=language)
        active_recognizers[session_id] = recognizer
        recognizer.start()
        
        emit('recording_started', {'message': 'Nagrywanie rozpoczęte'})
        
    except Exception as e:
        logger.error(f"Błąd podczas rozpoczynania nagrywania: {e}")
        emit('error', {'message': f'Błąd: {str(e)}'})

@socketio.on('stop_recording')
def handle_stop_recording():
    """Zatrzymaj strumieniowe rozpoznawanie mowy"""
    try:
        session_id = request.sid
        
        logger.info(f"⏹️ Zatrzymuję nagrywanie dla sesji: {session_id}")
        
        if session_id in active_recognizers:
            active_recognizers[session_id].stop()
            del active_recognizers[session_id]
            emit('recording_stopped', {'message': 'Nagrywanie zatrzymane'})
        else:
            emit('error', {'message': 'Brak aktywnego nagrywania'})
            
    except Exception as e:
        logger.error(f"Błąd podczas zatrzymywania nagrywania: {e}")
        emit('error', {'message': f'Błąd: {str(e)}'})
