"""
Protokolant - Meeting Minutes Management Application
Entry point for running the Flask application
"""

from src.app import create_app

if __name__ == '__main__':
    app = create_app()
    print("=" * 60)
    print("Protokolant - Aplikacja do zarządzania protokołami")
    print("=" * 60)
    print("\nAplikacja uruchomiona na: http://localhost:5000")
    print("Naciśnij Ctrl+C aby zatrzymać serwer\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
