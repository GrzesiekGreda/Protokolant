"""
Voice Commands Configuration Manager
Zarządzanie konfiguracją poleceń głosowych z poziomu aplikacji
"""

import json
import os
import copy
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class VoiceCommandsConfig:
    """
    Klasa do zarządzania konfiguracją poleceń głosowych
    Umożliwia edycję słów kluczowych bez modyfikacji kodu
    """
    
    DEFAULT_CONFIG_PATH = 'config/voice_commands.json'
    
    DEFAULT_CONFIG = {
        'trigger_word': 'uwaga',
        'commands': {
            'cofnij': {
                'action': 'undo_text',
                'description': 'Cofa ostatni tekst mówiony ciągiem',
                'enabled': True,
                'aliases': []
            },
            'cofnij słowo': {
                'action': 'undo_word',
                'description': 'Cofa ostatnie słowo',
                'enabled': True,
                'aliases': ['cofnij wyraz']
            },
            'cofnij zdanie': {
                'action': 'undo_sentence',
                'description': 'Cofa ostatnie zdanie',
                'enabled': True,
                'aliases': []
            },
            'nowy': {
                'action': 'new_document',
                'description': 'Zapisuje dotychczasowy dokument i tworzy nowy',
                'enabled': True,
                'aliases': ['nowy dokument', 'nowy plik']
            },
            'zapisz': {
                'action': 'save_document',
                'description': 'Zapisuje wprowadzone zmiany',
                'enabled': True,
                'aliases': ['save', 'zachowaj']
            }
        },
        'metadata': {
            'version': '1.0',
            'last_modified': None,
            'created': None
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicjalizacja managera konfiguracji
        
        Args:
            config_path: Ścieżka do pliku konfiguracji (opcjonalna)
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = None
        self.load_config()
    
    def load_config(self) -> bool:
        """
        Ładuje konfigurację z pliku lub tworzy domyślną
        
        Returns:
            True jeśli udało się załadować
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info(f"Załadowano konfigurację z: {self.config_path}")
                return True
            else:
                # Utwórz domyślną konfigurację
                logger.info("Tworzenie domyślnej konfiguracji")
                self.config = copy.deepcopy(self.DEFAULT_CONFIG)
                self.config['metadata']['created'] = datetime.now().isoformat()
                self.save_config()
                return True
        except Exception as e:
            logger.error(f"Błąd ładowania konfiguracji: {e}")
            self.config = copy.deepcopy(self.DEFAULT_CONFIG)
            return False
    
    def save_config(self) -> Tuple[bool, str]:
        """
        Zapisuje konfigurację do pliku
        
        Returns:
            Tuple (success, message)
        """
        try:
            # Zaktualizuj metadata
            self.config['metadata']['last_modified'] = datetime.now().isoformat()
            
            # Utwórz katalog jeśli nie istnieje
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Zapisz do pliku
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Zapisano konfigurację do: {self.config_path}")
            return True, f"Zapisano do: {self.config_path}"
        except Exception as e:
            logger.error(f"Błąd zapisu konfiguracji: {e}")
            return False, f"Błąd zapisu: {str(e)}"
    
    def get_trigger_word(self) -> str:
        """Zwraca aktualne słowo aktywujące"""
        return self.config.get('trigger_word', 'uwaga')
    
    def set_trigger_word(self, new_trigger: str) -> Tuple[bool, str]:
        """
        Ustawia nowe słowo aktywujące
        
        Args:
            new_trigger: Nowe słowo aktywujące
        
        Returns:
            Tuple (success, message)
        """
        if not new_trigger or not new_trigger.strip():
            return False, "Słowo aktywujące nie może być puste"
        
        old_trigger = self.config['trigger_word']
        self.config['trigger_word'] = new_trigger.strip().lower()
        
        success, message = self.save_config()
        if success:
            return True, f"Zmieniono '{old_trigger}' na '{new_trigger}'"
        return False, message
    
    def get_all_commands(self) -> Dict:
        """Zwraca wszystkie polecenia"""
        return self.config.get('commands', {})
    
    def get_command(self, command_phrase: str) -> Optional[Dict]:
        """
        Zwraca szczegóły konkretnego polecenia
        
        Args:
            command_phrase: Fraza polecenia
        
        Returns:
            Dict z danymi polecenia lub None
        """
        return self.config['commands'].get(command_phrase)
    
    def add_command(
        self, 
        command_phrase: str, 
        action: str, 
        description: str = "",
        aliases: List[str] = None,
        enabled: bool = True
    ) -> Tuple[bool, str]:
        """
        Dodaje nowe polecenie
        
        Args:
            command_phrase: Fraza polecenia (np. "cofnij wszystko")
            action: Akcja do wykonania (np. "undo_all")
            description: Opis polecenia
            aliases: Lista aliasów
            enabled: Czy polecenie jest włączone
        
        Returns:
            Tuple (success, message)
        """
        if not command_phrase or not command_phrase.strip():
            return False, "Fraza polecenia nie może być pusta"
        
        if not action or not action.strip():
            return False, "Akcja nie może być pusta"
        
        command_phrase = command_phrase.strip().lower()
        
        if command_phrase in self.config['commands']:
            return False, f"Polecenie '{command_phrase}' już istnieje"
        
        self.config['commands'][command_phrase] = {
            'action': action.strip(),
            'description': description.strip(),
            'enabled': enabled,
            'aliases': aliases or []
        }
        
        success, message = self.save_config()
        if success:
            return True, f"Dodano polecenie '{command_phrase}'"
        return False, message
    
    def update_command(
        self,
        command_phrase: str,
        new_phrase: Optional[str] = None,
        action: Optional[str] = None,
        description: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        enabled: Optional[bool] = None
    ) -> Tuple[bool, str]:
        """
        Aktualizuje istniejące polecenie
        
        Args:
            command_phrase: Aktualna fraza polecenia
            new_phrase: Nowa fraza (opcjonalna)
            action: Nowa akcja (opcjonalna)
            description: Nowy opis (opcjonalny)
            aliases: Nowe aliasy (opcjonalne)
            enabled: Nowy status (opcjonalny)
        
        Returns:
            Tuple (success, message)
        """
        if command_phrase not in self.config['commands']:
            return False, f"Polecenie '{command_phrase}' nie istnieje"
        
        command = self.config['commands'][command_phrase]
        
        # Aktualizuj pola
        if action is not None:
            command['action'] = action.strip()
        if description is not None:
            command['description'] = description.strip()
        if aliases is not None:
            command['aliases'] = aliases
        if enabled is not None:
            command['enabled'] = enabled
        
        # Zmień frazę jeśli podano nową
        if new_phrase and new_phrase.strip() != command_phrase:
            new_phrase = new_phrase.strip().lower()
            if new_phrase in self.config['commands']:
                return False, f"Polecenie '{new_phrase}' już istnieje"
            self.config['commands'][new_phrase] = command
            del self.config['commands'][command_phrase]
            command_phrase = new_phrase
        
        success, message = self.save_config()
        if success:
            return True, f"Zaktualizowano polecenie '{command_phrase}'"
        return False, message
    
    def delete_command(self, command_phrase: str) -> Tuple[bool, str]:
        """
        Usuwa polecenie
        
        Args:
            command_phrase: Fraza polecenia do usunięcia
        
        Returns:
            Tuple (success, message)
        """
        if command_phrase not in self.config['commands']:
            return False, f"Polecenie '{command_phrase}' nie istnieje"
        
        del self.config['commands'][command_phrase]
        
        success, message = self.save_config()
        if success:
            return True, f"Usunięto polecenie '{command_phrase}'"
        return False, message
    
    def toggle_command(self, command_phrase: str) -> Tuple[bool, str]:
        """
        Przełącza status włączenia/wyłączenia polecenia
        
        Args:
            command_phrase: Fraza polecenia
        
        Returns:
            Tuple (success, message)
        """
        if command_phrase not in self.config['commands']:
            return False, f"Polecenie '{command_phrase}' nie istnieje"
        
        command = self.config['commands'][command_phrase]
        command['enabled'] = not command['enabled']
        
        success, message = self.save_config()
        if success:
            status = "włączono" if command['enabled'] else "wyłączono"
            return True, f"Polecenie '{command_phrase}' {status}"
        return False, message
    
    def add_alias(self, command_phrase: str, alias: str) -> Tuple[bool, str]:
        """
        Dodaje alias do polecenia
        
        Args:
            command_phrase: Fraza polecenia
            alias: Nowy alias
        
        Returns:
            Tuple (success, message)
        """
        if command_phrase not in self.config['commands']:
            return False, f"Polecenie '{command_phrase}' nie istnieje"
        
        alias = alias.strip().lower()
        if not alias:
            return False, "Alias nie może być pusty"
        
        command = self.config['commands'][command_phrase]
        if alias in command['aliases']:
            return False, f"Alias '{alias}' już istnieje"
        
        command['aliases'].append(alias)
        
        success, message = self.save_config()
        if success:
            return True, f"Dodano alias '{alias}' do '{command_phrase}'"
        return False, message
    
    def remove_alias(self, command_phrase: str, alias: str) -> Tuple[bool, str]:
        """
        Usuwa alias z polecenia
        
        Args:
            command_phrase: Fraza polecenia
            alias: Alias do usunięcia
        
        Returns:
            Tuple (success, message)
        """
        if command_phrase not in self.config['commands']:
            return False, f"Polecenie '{command_phrase}' nie istnieje"
        
        command = self.config['commands'][command_phrase]
        if alias not in command['aliases']:
            return False, f"Alias '{alias}' nie istnieje"
        
        command['aliases'].remove(alias)
        
        success, message = self.save_config()
        if success:
            return True, f"Usunięto alias '{alias}' z '{command_phrase}'"
        return False, message
    
    def reset_to_defaults(self) -> Tuple[bool, str]:
        """
        Resetuje konfigurację do wartości domyślnych
        
        Returns:
            Tuple (success, message)
        """
        self.config = copy.deepcopy(self.DEFAULT_CONFIG)
        self.config['metadata']['created'] = datetime.now().isoformat()
        
        success, message = self.save_config()
        if success:
            return True, "Zresetowano konfigurację do wartości domyślnych"
        return False, message
    
    def export_config(self, export_path: str) -> Tuple[bool, str]:
        """
        Eksportuje konfigurację do pliku
        
        Args:
            export_path: Ścieżka do pliku eksportu
        
        Returns:
            Tuple (success, message)
        """
        try:
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Wyeksportowano konfigurację do: {export_path}")
            return True, f"Wyeksportowano do: {export_path}"
        except Exception as e:
            logger.error(f"Błąd eksportu: {e}")
            return False, f"Błąd eksportu: {str(e)}"
    
    def import_config(self, import_path: str) -> Tuple[bool, str]:
        """
        Importuje konfigurację z pliku
        
        Args:
            import_path: Ścieżka do pliku importu
        
        Returns:
            Tuple (success, message)
        """
        try:
            if not os.path.exists(import_path):
                return False, f"Plik nie istnieje: {import_path}"
            
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Walidacja podstawowych pól
            if 'trigger_word' not in imported_config:
                return False, "Nieprawidłowy format konfiguracji: brak trigger_word"
            if 'commands' not in imported_config:
                return False, "Nieprawidłowy format konfiguracji: brak commands"
            
            # Zapisz obecną jako backup
            backup_path = self.config_path + '.backup'
            self.export_config(backup_path)
            
            # Załaduj nową konfigurację
            self.config = imported_config
            self.config['metadata']['last_modified'] = datetime.now().isoformat()
            
            success, message = self.save_config()
            if success:
                return True, f"Zaimportowano konfigurację z: {import_path}"
            return False, message
        except Exception as e:
            logger.error(f"Błąd importu: {e}")
            return False, f"Błąd importu: {str(e)}"
    
    def get_statistics(self) -> Dict:
        """
        Zwraca statystyki konfiguracji
        
        Returns:
            Dict ze statystykami
        """
        commands = self.config['commands']
        enabled_count = sum(1 for cmd in commands.values() if cmd['enabled'])
        total_aliases = sum(len(cmd['aliases']) for cmd in commands.values())
        
        return {
            'total_commands': len(commands),
            'enabled_commands': enabled_count,
            'disabled_commands': len(commands) - enabled_count,
            'total_aliases': total_aliases,
            'trigger_word': self.config['trigger_word'],
            'last_modified': self.config['metadata'].get('last_modified'),
            'version': self.config['metadata'].get('version')
        }


# Funkcja pomocnicza
def get_config_manager(config_path: Optional[str] = None) -> VoiceCommandsConfig:
    """
    Zwraca instancję managera konfiguracji
    
    Args:
        config_path: Opcjonalna ścieżka do pliku konfiguracji
    
    Returns:
        VoiceCommandsConfig instance
    """
    return VoiceCommandsConfig(config_path)


# Testy
if __name__ == '__main__':
    print("=== Test managera konfiguracji poleceń głosowych ===\n")
    
    # Testowa ścieżka
    test_config_path = 'config/test_voice_commands.json'
    
    # Inicjalizacja
    manager = VoiceCommandsConfig(test_config_path)
    
    print(f"1. Słowo aktywujące: {manager.get_trigger_word()}")
    print(f"2. Liczba poleceń: {len(manager.get_all_commands())}\n")
    
    # Zmiana słowa aktywującego
    print("3. Zmiana słowa aktywującego na 'hej':")
    success, msg = manager.set_trigger_word('hej')
    print(f"   {msg}\n")
    
    # Dodanie nowego polecenia
    print("4. Dodanie polecenia 'wyczyść':")
    success, msg = manager.add_command(
        'wyczyść',
        'clear_document',
        'Czyści cały dokument',
        ['clear', 'usuń wszystko']
    )
    print(f"   {msg}\n")
    
    # Aktualizacja polecenia
    print("5. Aktualizacja opisu polecenia 'zapisz':")
    success, msg = manager.update_command(
        'zapisz',
        description='Zapisuje dokument do pliku'
    )
    print(f"   {msg}\n")
    
    # Dodanie aliasu
    print("6. Dodanie aliasu 'cofnij literę' do 'cofnij słowo':")
    success, msg = manager.add_alias('cofnij słowo', 'cofnij literę')
    print(f"   {msg}\n")
    
    # Statystyki
    print("7. Statystyki:")
    stats = manager.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\nTest zakończony!")
