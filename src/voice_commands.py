"""
Voice Commands Module for Protokolant
System poleceń głosowych do sterowania aplikacją
"""

import re
from typing import Optional, Tuple, List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class VoiceCommandProcessor:
    """
    Klasa do przetwarzania poleceń głosowych
    Reaguje na słowo "Uwaga" i wykonuje polecenia sterujące
    """
    
    # Słowo aktywujące system poleceń
    TRIGGER_WORD = "uwaga"
    
    # Definicje poleceń
    COMMANDS = {
        'cofnij': 'undo_text',           # Cofa ostatni tekst mówiony ciągiem
        'cofnij słowo': 'undo_word',     # Cofa ostatnie słowo
        'cofnij zdanie': 'undo_sentence', # Cofa ostatnie zdanie
        'nowy': 'new_document',           # Zapisuje i tworzy nowy dokument
        'zapisz': 'save_document'         # Zapisuje wprowadzone zmiany
    }
    
    def __init__(self):
        """Inicjalizacja procesora poleceń głosowych"""
        self.text_history = []           # Historia wszystkich wprowadzonych tekstów
        self.current_text = ""           # Aktualny tekst dokumentu
        self.command_history = []        # Historia wykonanych poleceń
        self.last_command = None         # Ostatnie wykonane polecenie
        
    def parse_voice_input(self, voice_text: str) -> Tuple[bool, Optional[str], str]:
        """
        Parsuje tekst głosowy i sprawdza czy zawiera polecenie
        
        Args:
            voice_text: Rozpoznany tekst z mowy
        
        Returns:
            Tuple (is_command, command_name, remaining_text)
            - is_command: True jeśli wykryto polecenie
            - command_name: Nazwa polecenia lub None
            - remaining_text: Tekst bez polecenia
        """
        # Normalizacja tekstu (małe litery, usuń nadmiarowe spacje)
        normalized = voice_text.lower().strip()
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Sprawdź czy tekst zawiera słowo "uwaga"
        if self.TRIGGER_WORD not in normalized:
            return False, None, voice_text
        
        # Znajdź pozycję słowa "uwaga"
        parts = normalized.split(self.TRIGGER_WORD, 1)
        
        if len(parts) < 2:
            return False, None, voice_text
        
        before_trigger = parts[0].strip()
        after_trigger = parts[1].strip()
        
        # Sprawdź polecenia w kolejności od najdłuższych
        detected_command = None
        remaining = after_trigger
        
        for command_phrase, command_name in sorted(
            self.COMMANDS.items(), 
            key=lambda x: len(x[0]), 
            reverse=True
        ):
            if after_trigger.startswith(command_phrase):
                detected_command = command_name
                # Usuń polecenie z tekstu
                remaining = after_trigger[len(command_phrase):].strip()
                break
        
        if detected_command:
            logger.info(f"Wykryto polecenie: {detected_command}")
            return True, detected_command, before_trigger
        else:
            # "Uwaga" bez prawidłowego polecenia
            logger.warning(f"Wykryto 'uwaga' ale brak prawidłowego polecenia: {after_trigger}")
            return False, None, voice_text
    
    def add_text(self, text: str):
        """
        Dodaje nowy tekst do dokumentu
        
        Args:
            text: Tekst do dodania
        """
        if not text.strip():
            return
        
        # Zapisz w historii
        self.text_history.append({
            'text': text,
            'timestamp': datetime.now(),
            'type': 'addition'
        })
        
        # Dodaj do aktualnego tekstu
        if self.current_text:
            self.current_text += " " + text
        else:
            self.current_text = text
        
        logger.info(f"Dodano tekst: {text}")
    
    def undo_text(self) -> Tuple[bool, str]:
        """
        POLECENIE: Cofa ostatni tekst mówiony ciągiem
        
        Returns:
            Tuple (success, message)
        """
        if not self.text_history:
            return False, "Brak tekstu do cofnięcia"
        
        # Znajdź ostatnio dodany tekst
        last_entry = None
        for i in range(len(self.text_history) - 1, -1, -1):
            if self.text_history[i]['type'] == 'addition':
                last_entry = self.text_history[i]
                break
        
        if not last_entry:
            return False, "Brak tekstu do cofnięcia"
        
        # Usuń ostatni tekst
        text_to_remove = last_entry['text']
        
        # Usuń z aktualnego tekstu
        if self.current_text.endswith(text_to_remove):
            self.current_text = self.current_text[:-len(text_to_remove)].rstrip()
        else:
            # Usuń ostatnie wystąpienie
            last_pos = self.current_text.rfind(text_to_remove)
            if last_pos != -1:
                self.current_text = self.current_text[:last_pos] + self.current_text[last_pos + len(text_to_remove):]
                self.current_text = self.current_text.strip()
        
        # Zapisz w historii poleceń
        self.command_history.append({
            'command': 'undo_text',
            'timestamp': datetime.now(),
            'removed_text': text_to_remove
        })
        
        logger.info(f"Cofnięto tekst: {text_to_remove}")
        return True, f"Cofnięto: '{text_to_remove}'"
    
    def undo_word(self) -> Tuple[bool, str]:
        """
        POLECENIE: Cofa ostatnie słowo
        
        Returns:
            Tuple (success, message)
        """
        if not self.current_text.strip():
            return False, "Brak tekstu do cofnięcia"
        
        # Podziel na słowa
        words = self.current_text.split()
        
        if not words:
            return False, "Brak słów do cofnięcia"
        
        # Usuń ostatnie słowo
        removed_word = words[-1]
        words = words[:-1]
        
        # Zaktualizuj tekst
        self.current_text = " ".join(words)
        
        # Zapisz w historii
        self.command_history.append({
            'command': 'undo_word',
            'timestamp': datetime.now(),
            'removed_text': removed_word
        })
        
        logger.info(f"Cofnięto słowo: {removed_word}")
        return True, f"Cofnięto słowo: '{removed_word}'"
    
    def undo_sentence(self) -> Tuple[bool, str]:
        """
        POLECENIE: Cofa ostatnie zdanie
        
        Returns:
            Tuple (success, message)
        """
        if not self.current_text.strip():
            return False, "Brak tekstu do cofnięcia"
        
        # Znajdź ostatnie zdanie (kończy się kropką, wykrzyknikiem lub znakiem zapytania)
        sentence_endings = r'[.!?]'
        
        # Znajdź wszystkie zakończenia zdań
        matches = list(re.finditer(sentence_endings, self.current_text))
        
        if not matches:
            # Brak zakończenia zdania - usuń cały tekst jako niekompletne zdanie
            removed_sentence = self.current_text
            self.current_text = ""
        else:
            # Usuń tekst po ostatnim zakończeniu zdania
            last_ending = matches[-1].end()
            
            if last_ending < len(self.current_text):
                # Jest tekst po ostatnim zakończeniu - usuń go
                removed_sentence = self.current_text[last_ending:].strip()
                self.current_text = self.current_text[:last_ending].strip()
            else:
                # Usuń ostatnie kompletne zdanie
                if len(matches) > 1:
                    prev_ending = matches[-2].end()
                    removed_sentence = self.current_text[prev_ending:].strip()
                    self.current_text = self.current_text[:prev_ending].strip()
                else:
                    # To pierwsze zdanie - usuń wszystko
                    removed_sentence = self.current_text
                    self.current_text = ""
        
        # Zapisz w historii
        self.command_history.append({
            'command': 'undo_sentence',
            'timestamp': datetime.now(),
            'removed_text': removed_sentence
        })
        
        logger.info(f"Cofnięto zdanie: {removed_sentence}")
        return True, f"Cofnięto zdanie: '{removed_sentence}'"
    
    def save_document(self, filepath: Optional[str] = None) -> Tuple[bool, str]:
        """
        POLECENIE: Zapisuje wprowadzone zmiany
        
        Args:
            filepath: Ścieżka do pliku (jeśli None, generuje automatycznie)
        
        Returns:
            Tuple (success, message)
        """
        if not self.current_text.strip():
            return False, "Brak tekstu do zapisania"
        
        try:
            # Wygeneruj nazwę pliku jeśli nie podano
            if not filepath:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filepath = f"transcriptions/document_{timestamp}.txt"
            
            # Zapisz do pliku
            import os
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Dokument utworzony: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")
                f.write(self.current_text)
            
            # Zapisz w historii
            self.command_history.append({
                'command': 'save_document',
                'timestamp': datetime.now(),
                'filepath': filepath
            })
            
            logger.info(f"Zapisano dokument: {filepath}")
            return True, f"Zapisano do: {filepath}"
        
        except Exception as e:
            logger.error(f"Błąd zapisu: {e}")
            return False, f"Błąd zapisu: {str(e)}"
    
    def new_document(self, save_current: bool = True) -> Tuple[bool, str]:
        """
        POLECENIE: Zapisuje dotychczasowy dokument i tworzy nowy
        
        Args:
            save_current: Czy zapisać obecny dokument przed utworzeniem nowego
        
        Returns:
            Tuple (success, message)
        """
        messages = []
        
        # Zapisz obecny dokument jeśli ma treść
        if save_current and self.current_text.strip():
            success, message = self.save_document()
            if success:
                messages.append(message)
            else:
                return False, f"Błąd zapisu obecnego dokumentu: {message}"
        
        # Wyczyść obecny dokument
        old_text = self.current_text
        self.current_text = ""
        self.text_history = []
        
        # Zapisz w historii
        self.command_history.append({
            'command': 'new_document',
            'timestamp': datetime.now(),
            'old_text_length': len(old_text)
        })
        
        logger.info("Utworzono nowy dokument")
        messages.append("Utworzono nowy, czysty dokument")
        
        return True, " | ".join(messages)
    
    def execute_command(self, command_name: str, **kwargs) -> Tuple[bool, str]:
        """
        Wykonuje polecenie według nazwy
        
        Args:
            command_name: Nazwa polecenia
            **kwargs: Dodatkowe parametry dla polecenia
        
        Returns:
            Tuple (success, message)
        """
        command_map = {
            'undo_text': lambda: self.undo_text(),
            'undo_word': lambda: self.undo_word(),
            'undo_sentence': lambda: self.undo_sentence(),
            'save_document': lambda: self.save_document(kwargs.get('filepath')),
            'new_document': lambda: self.new_document(kwargs.get('save_current', True))
        }
        
        if command_name not in command_map:
            return False, f"Nieznane polecenie: {command_name}"
        
        try:
            self.last_command = command_name
            return command_map[command_name]()
        except Exception as e:
            logger.error(f"Błąd wykonania polecenia {command_name}: {e}")
            return False, f"Błąd wykonania: {str(e)}"
    
    def process_voice_input(self, voice_text: str, **kwargs) -> Dict:
        """
        GŁÓWNA FUNKCJA: Przetwarza wejście głosowe i wykonuje polecenia
        
        Args:
            voice_text: Rozpoznany tekst z mowy
            **kwargs: Dodatkowe parametry (np. filepath dla save)
        
        Returns:
            Dict z wynikami:
            {
                'is_command': bool,
                'command_executed': str or None,
                'command_result': tuple or None,
                'text_added': bool,
                'current_text': str,
                'message': str
            }
        """
        result = {
            'is_command': False,
            'command_executed': None,
            'command_result': None,
            'text_added': False,
            'current_text': self.current_text,
            'message': ''
        }
        
        # Parsuj wejście głosowe
        is_command, command_name, remaining_text = self.parse_voice_input(voice_text)
        
        if is_command and command_name:
            # Wykonaj polecenie
            result['is_command'] = True
            result['command_executed'] = command_name
            
            success, message = self.execute_command(command_name, **kwargs)
            result['command_result'] = (success, message)
            result['current_text'] = self.current_text
            result['message'] = message
            
            # Dodaj pozostały tekst jeśli jest
            if remaining_text.strip():
                self.add_text(remaining_text)
                result['text_added'] = True
                result['current_text'] = self.current_text
        else:
            # Zwykły tekst - dodaj do dokumentu
            self.add_text(voice_text)
            result['text_added'] = True
            result['current_text'] = self.current_text
            result['message'] = 'Dodano tekst'
        
        return result
    
    def get_text(self) -> str:
        """Zwraca aktualny tekst dokumentu"""
        return self.current_text
    
    def get_history(self) -> List[Dict]:
        """Zwraca historię wszystkich operacji"""
        return self.text_history + self.command_history
    
    def get_statistics(self) -> Dict:
        """Zwraca statystyki dokumentu"""
        words = len(self.current_text.split()) if self.current_text else 0
        sentences = len(re.findall(r'[.!?]', self.current_text))
        characters = len(self.current_text)
        
        return {
            'words': words,
            'sentences': sentences,
            'characters': characters,
            'text_additions': len([h for h in self.text_history if h['type'] == 'addition']),
            'commands_executed': len(self.command_history)
        }
    
    def reset(self):
        """Resetuje procesor do stanu początkowego"""
        self.text_history = []
        self.current_text = ""
        self.command_history = []
        self.last_command = None
        logger.info("Procesor poleceń zresetowany")


# Funkcja pomocnicza do szybkiego użycia
def process_voice_command(voice_text: str, processor: Optional[VoiceCommandProcessor] = None) -> Dict:
    """
    Szybka funkcja do przetwarzania poleceń głosowych
    
    Args:
        voice_text: Rozpoznany tekst z mowy
        processor: Istniejący procesor (opcjonalny)
    
    Returns:
        Dict z wynikami przetwarzania
    """
    if processor is None:
        processor = VoiceCommandProcessor()
    
    return processor.process_voice_input(voice_text)


# Przykład użycia i testy
if __name__ == '__main__':
    print("=== PROTOKOLANT - Test systemu poleceń głosowych ===\n")
    
    processor = VoiceCommandProcessor()
    
    # Test 1: Dodawanie tekstu
    print("Test 1: Dodawanie tekstu")
    result = processor.process_voice_input("Zebranie zarządu w sprawie budżetu.")
    print(f"Tekst: {result['current_text']}")
    print(f"Komunikat: {result['message']}\n")
    
    # Test 2: Dodanie kolejnego tekstu
    print("Test 2: Dodanie kolejnego tekstu")
    result = processor.process_voice_input("Omówiono projekt na rok 2025.")
    print(f"Tekst: {result['current_text']}")
    print(f"Komunikat: {result['message']}\n")
    
    # Test 3: Cofnij słowo
    print("Test 3: Polecenie 'uwaga cofnij słowo'")
    result = processor.process_voice_input("uwaga cofnij słowo")
    print(f"Polecenie: {result['command_executed']}")
    print(f"Tekst: {result['current_text']}")
    print(f"Komunikat: {result['message']}\n")
    
    # Test 4: Cofnij zdanie
    print("Test 4: Polecenie 'uwaga cofnij zdanie'")
    result = processor.process_voice_input("uwaga cofnij zdanie")
    print(f"Polecenie: {result['command_executed']}")
    print(f"Tekst: {result['current_text']}")
    print(f"Komunikat: {result['message']}\n")
    
    # Test 5: Dodaj nowy tekst
    print("Test 5: Dodanie nowego tekstu")
    result = processor.process_voice_input("Ustalono nowy harmonogram spotkań.")
    print(f"Tekst: {result['current_text']}")
    
    # Test 6: Cofnij tekst
    print("\nTest 6: Polecenie 'uwaga cofnij'")
    result = processor.process_voice_input("uwaga cofnij")
    print(f"Polecenie: {result['command_executed']}")
    print(f"Tekst: {result['current_text']}")
    print(f"Komunikat: {result['message']}\n")
    
    # Test 7: Zapisz dokument
    print("Test 7: Polecenie 'uwaga zapisz'")
    result = processor.process_voice_input("uwaga zapisz")
    print(f"Polecenie: {result['command_executed']}")
    print(f"Komunikat: {result['message']}\n")
    
    # Test 8: Nowy dokument
    print("Test 8: Dodaj tekst i wykonaj 'uwaga nowy'")
    processor.process_voice_input("To jest testowy dokument.")
    result = processor.process_voice_input("uwaga nowy")
    print(f"Polecenie: {result['command_executed']}")
    print(f"Tekst po komendzie: '{result['current_text']}'")
    print(f"Komunikat: {result['message']}\n")
    
    # Test 9: Statystyki
    print("Test 9: Statystyki")
    processor.process_voice_input("Nowy dokument z kilkoma zdaniami. To jest drugie zdanie. A to trzecie!")
    stats = processor.get_statistics()
    print(f"Słowa: {stats['words']}")
    print(f"Zdania: {stats['sentences']}")
    print(f"Znaki: {stats['characters']}")
    print(f"Dodanych tekstów: {stats['text_additions']}")
    print(f"Wykonanych poleceń: {stats['commands_executed']}")
