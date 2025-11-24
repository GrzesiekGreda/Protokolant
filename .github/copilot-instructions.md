# Protokolant - Copilot Instructions

**Project Name**: Protokolant  
**Language**: Python 3.12+  
**Type**: Meeting Minutes & Protocol Management Application

---

## Project Overview

Protokolant is a Python-based application for creating, managing, and storing meeting minutes and protocols. The application helps organizations maintain professional records of meetings, decisions, and action items.

---

## Technology Stack

- **Language**: Python 3.12+
- **Framework**: Flask (web interface)
- **Database**: SQLite (local storage)
- **UI**: HTML/CSS/JavaScript (Bootstrap 5)
- **PDF Generation**: ReportLab or WeasyPrint
- **Date/Time**: Python datetime module

---

## Project Structure

```
Protokolant/
├── .github/
│   └── copilot-instructions.md
├── src/
│   ├── __init__.py
│   ├── app.py              # Flask application entry point
│   ├── models.py           # Database models
│   ├── routes.py           # Web routes
│   └── utils.py            # Utility functions
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── create_protocol.html
│   └── view_protocol.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
├── data/
│   └── protocols.db
├── requirements.txt
├── README.md
└── run.py
```

---

## Core Features

### 1. Speech-to-Text (MAIN FEATURE)
- **Automatic voice transcription** with punctuation and grammar correction
- Record audio from microphone or upload audio files
- OpenAI Whisper AI for high-quality Polish language recognition
- LanguageTool for automatic spelling and grammar corrections
- Save transcriptions to text files
- API endpoints: `/api/record-speech`, `/api/transcribe-file`, `/api/voice-command`
- Module: `src/speech_to_text.py`
- Documentation: `SPEECH_RECOGNITION.md`

### 1.1 Voice Commands System
- **Voice-controlled document editing** with trigger word "uwaga"
- Commands:
  - "uwaga cofnij" - undo last text block
  - "uwaga cofnij słowo" - undo last word
  - "uwaga cofnij zdanie" - undo last sentence
  - "uwaga zapisz" - save document
  - "uwaga nowy" - save current and create new document
- Module: `src/voice_commands.py`
- Documentation: `VOICE_COMMANDS.md`

### 2. Protocol Creation
- Form for entering meeting details (date, time, location, participants)
- Voice input buttons (🎤) for all text fields
- Agenda items with discussion notes
- Action items with assignees and deadlines
- Decisions tracking

### 2. Protocol Management
- List all protocols with search and filter
- View detailed protocol information
- Edit existing protocols
- Archive old protocols

### 3. Export & Sharing
- Generate PDF documents
- Export to HTML
- Email protocol to participants

### 4. Database Schema
```python
Protocol:
- id (Primary Key)
- title (String)
- date (DateTime)
- location (String)
- created_at (DateTime)
- updated_at (DateTime)

Participant:
- id (Primary Key)
- name (String)
- email (String)
- protocol_id (Foreign Key)

AgendaItem:
- id (Primary Key)
- title (String)
- discussion (Text)
- order (Integer)
- protocol_id (Foreign Key)

ActionItem:
- id (Primary Key)
- description (Text)
- assignee (String)
- deadline (Date)
- status (String: pending/completed)
- protocol_id (Foreign Key)
```

---

## Development Guidelines

### Code Style
- Follow PEP 8 conventions
- Use type hints for function parameters and returns
- Write docstrings for all functions and classes
- Keep functions small and focused (< 50 lines)

### Naming Conventions
- Variables: `snake_case`
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_CASE`
- Files: `lowercase.py`

### Error Handling
- Use try-except blocks for database operations
- Validate all user inputs
- Provide meaningful error messages in Polish
- Log errors to file for debugging

### Database
- Use SQLAlchemy ORM for database operations
- Always use context managers for sessions
- Create indexes for frequently queried fields
- Backup database before major operations

### UI/UX
- Polish language interface
- Responsive design (mobile-friendly)
- Clear navigation between sections
- Form validation with helpful error messages
- Loading indicators for async operations

---

## Testing Strategy

- Unit tests for utility functions
- Integration tests for database operations
- Manual testing for UI workflows
- Test with sample meeting data

---

## Deployment

### Local Development
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### Production Considerations
- Use environment variables for configuration
- Enable HTTPS for web interface
- Regular database backups
- Log rotation for application logs

---

## Future Enhancements

- User authentication and roles
- Meeting templates for recurring meetings
- Calendar integration
- Automatic reminder emails
- Rich text editor for notes
- File attachments support
- Multi-language support

---

## Polish Language Context

- Interface labels in Polish
- Date format: DD.MM.YYYY
- Time format: HH:MM (24-hour)
- PDF headers: "PROTOKÓŁ ZE SPOTKANIA"
- Navigation: "Lista protokołów", "Nowy protokół", "Szukaj", "Eksportuj"

---

## Getting Started

1. Set up Python virtual environment
2. Install dependencies from requirements.txt
3. Initialize database with schema
4. Run Flask development server
5. Navigate to http://localhost:5000
6. Create first protocol to test functionality
