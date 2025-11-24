"""
Speech-to-Text Module for Protokolant
Główny moduł do rozpoznawania mowy i automatycznej transkrypcji z interpunkcją
"""

import speech_recognition as sr
import language_tool_python
import os
import re
from typing import Optional, Tuple
from datetime import datetime
import logging
from .voice_commands import VoiceCommandProcessor

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Próba załadowania Whisper
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("OpenAI Whisper nie jest dostępny - używaj tylko Google Speech Recognition")

class SpeechToTextProcessor:
    """
    Klasa do przetwarzania mowy na tekst z automatyczną korektą ortografii i interpunkcji
    """
    
    def __init__(self, language: str = 'pl-PL', use_whisper: bool = True, enable_voice_commands: bool = True):
        """
        Inicjalizacja procesora mowy
        
        Args:
            language: Kod języka (domyślnie polski)
            use_whisper: Czy używać OpenAI Whisper (lepsza jakość)
            enable_voice_commands: Czy włączyć system poleceń głosowych
        """
        self.language = language
        self.use_whisper = use_whisper
        self.recognizer = sr.Recognizer()
        
        # System poleceń głosowych
        self.enable_voice_commands = enable_voice_commands
        if self.enable_voice_commands:
            self.voice_commander = VoiceCommandProcessor()
            logger.info("System poleceń głosowych włączony")
        else:
            self.voice_commander = None
        
        # Inicjalizacja Whisper AI
        if self.use_whisper and WHISPER_AVAILABLE:
            try:
                logger.info("Ładowanie modelu Whisper...")
                self.whisper_model = whisper.load_model("base")
                logger.info("Model Whisper załadowany pomyślnie")
            except Exception as e:
                logger.warning(f"Nie udało się załadować Whisper: {e}. Używam Google Speech Recognition.")
                self.use_whisper = False
        elif self.use_whisper and not WHISPER_AVAILABLE:
            logger.warning("Whisper nie jest zainstalowany. Używam Google Speech Recognition.")
            self.use_whisper = False
        
        # Inicjalizacja narzędzia do korekty gramatycznej
        try:
            logger.info("Inicjalizacja narzędzia do korekty ortografii...")
            self.grammar_tool = language_tool_python.LanguageTool('pl-PL')
            logger.info("Narzędzie do korekty ortografii gotowe")
        except Exception as e:
            logger.error(f"Błąd inicjalizacji korekty ortografii: {e}")
            self.grammar_tool = None
    
    def record_audio(self, duration: Optional[int] = None, save_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Nagrywa dźwięk z mikrofonu
        
        Args:
            duration: Czas nagrywania w sekundach (None = do momentu ciszy)
            save_path: Ścieżka do zapisu pliku audio
        
        Returns:
            Tuple (sukces, ścieżka_do_pliku_lub_komunikat_błędu)
        """
        try:
            with sr.Microphone() as source:
                logger.info("Nasłuchiwanie... Proszę mówić.")
                
                # Kalibracja poziomu szumu
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Nagrywanie
                if duration:
                    logger.info(f"Nagrywanie przez {duration} sekund...")
                    audio = self.recognizer.record(source, duration=duration)
                else:
                    logger.info("Nagrywanie do momentu ciszy...")
                    audio = self.recognizer.listen(source, timeout=30, phrase_time_limit=300)
                
                # Zapis do pliku
                if save_path:
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                else:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    save_path = f"recordings/recording_{timestamp}.wav"
                    os.makedirs('recordings', exist_ok=True)
                
                with open(save_path, 'wb') as f:
                    f.write(audio.get_wav_data())
                
                logger.info(f"Nagranie zapisane: {save_path}")
                return True, save_path
        
        except sr.WaitTimeoutError:
            return False, "Przekroczono limit czasu oczekiwania na mowę"
        except Exception as e:
            logger.error(f"Błąd podczas nagrywania: {e}")
            return False, str(e)
    
    def transcribe_audio(self, audio_path: str) -> Tuple[bool, str]:
        """
        Transkrybuje plik audio na tekst
        
        Args:
            audio_path: Ścieżka do pliku audio
        
        Returns:
            Tuple (sukces, tekst_lub_komunikat_błędu)
        """
        try:
            if self.use_whisper:
                # Użyj Whisper AI (lepsza jakość i automatyczna interpunkcja)
                logger.info("Transkrypcja za pomocą Whisper AI...")
                result = self.whisper_model.transcribe(
                    audio_path, 
                    language='pl',
                    task='transcribe',
                    fp16=False
                )
                text = result['text'].strip()
                logger.info("Transkrypcja zakończona pomyślnie")
                return True, text
            else:
                # Użyj Google Speech Recognition
                logger.info("Transkrypcja za pomocą Google Speech Recognition...")
                with sr.AudioFile(audio_path) as source:
                    audio = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio, language=self.language)
                    logger.info("Transkrypcja zakończona pomyślnie")
                    return True, text
        
        except sr.UnknownValueError:
            return False, "Nie rozpoznano mowy w nagraniu"
        except sr.RequestError as e:
            return False, f"Błąd usługi rozpoznawania mowy: {e}"
        except Exception as e:
            logger.error(f"Błąd podczas transkrypcji: {e}")
            return False, str(e)
    
    def apply_grammar_corrections(self, text: str) -> str:
        """
        Aplikuje korekty ortograficzne i gramatyczne do tekstu
        
        Args:
            text: Tekst do korekty
        
        Returns:
            Poprawiony tekst
        """
        if not self.grammar_tool:
            logger.warning("Narzędzie do korekty ortografii niedostępne")
            return text
        
        try:
            logger.info("Aplikowanie korekty ortograficznej...")
            matches = self.grammar_tool.check(text)
            corrected_text = language_tool_python.utils.correct(text, matches)
            
            # Liczba poprawek
            if matches:
                logger.info(f"Zastosowano {len(matches)} poprawek ortograficznych")
            
            return corrected_text
        
        except Exception as e:
            logger.error(f"Błąd podczas korekty ortografii: {e}")
            return text
    
    def add_punctuation(self, text: str) -> str:
        """
        Dodaje interpunkcję do tekstu (prosty algorytm heurystyczny)
        
        Args:
            text: Tekst bez interpunkcji
        
        Returns:
            Tekst z interpunkcją
        """
        if not text:
            return text
        
        # Whisper już dodaje interpunkcję, więc ten krok jest opcjonalny
        if self.use_whisper:
            return text
        
        # Podstawowa interpunkcja dla Google Speech Recognition
        text = text.strip()
        
        # Wielka litera na początku
        text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
        
        # Dodaj kropkę na końcu jeśli brak
        if not text.endswith(('.', '!', '?')):
            text += '.'
        
        # Wielkie litery po kropkach
        text = re.sub(r'\.(\s+)([a-ząćęłńóśźż])', lambda m: '.' + m.group(1) + m.group(2).upper(), text)
        
        return text
    
    def record_and_transcribe(
        self, 
        duration: Optional[int] = None,
        save_audio: bool = True,
        apply_corrections: bool = True,
        process_commands: bool = True
    ) -> dict:
        """
        GŁÓWNA FUNKCJA: Nagrywa mowę i konwertuje na tekst z korektą
        
        Args:
            duration: Czas nagrywania w sekundach (None = automatyczne)
            save_audio: Czy zapisać plik audio
            apply_corrections: Czy zastosować korekty ortograficzne
            process_commands: Czy przetwarzać polecenia głosowe (wymaga enable_voice_commands=True)
        
        Returns:
            Dict z kluczami: success, text, audio_path, errors, command_info
        """
        result = {
            'success': False,
            'text': '',
            'audio_path': None,
            'errors': [],
            'command_info': None
        }
        
        try:
            # Krok 1: Nagrywanie
            logger.info("=== ROZPOCZYNAM NAGRYWANIE ===")
            success, audio_path_or_error = self.record_audio(
                duration=duration,
                save_path=None if save_audio else None
            )
            
            if not success:
                result['errors'].append(f"Nagrywanie: {audio_path_or_error}")
                return result
            
            audio_path = audio_path_or_error
            result['audio_path'] = audio_path
            
            # Krok 2: Transkrypcja
            logger.info("=== ROZPOCZYNAM TRANSKRYPCJĘ ===")
            success, text_or_error = self.transcribe_audio(audio_path)
            
            if not success:
                result['errors'].append(f"Transkrypcja: {text_or_error}")
                return result
            
            text = text_or_error
            
            # Krok 3: Dodanie interpunkcji (jeśli potrzebne)
            logger.info("=== DODAWANIE INTERPUNKCJI ===")
            text = self.add_punctuation(text)
            
            # Krok 4: Korekta ortograficzna
            if apply_corrections:
                logger.info("=== KOREKTA ORTOGRAFICZNA ===")
                text = self.apply_grammar_corrections(text)
            
            # Krok 5: Przetwarzanie poleceń głosowych (jeśli włączone)
            if process_commands and self.enable_voice_commands and self.voice_commander:
                logger.info("=== PRZETWARZANIE POLECEŃ GŁOSOWYCH ===")
                command_result = self.voice_commander.process_voice_input(text)
                
                result['command_info'] = {
                    'is_command': command_result['is_command'],
                    'command_executed': command_result['command_executed'],
                    'command_result': command_result['command_result'],
                    'text_added': command_result['text_added'],
                    'message': command_result['message']
                }
                
                # Jeśli wykryto polecenie, użyj aktualnego tekstu z procesora poleceń
                if command_result['is_command']:
                    text = command_result['current_text']
                    logger.info(f"Wykonano polecenie: {command_result['command_executed']}")
            
            # Sukces!
            result['success'] = True
            result['text'] = text
            
            logger.info(f"=== ZAKOŃCZONO POMYŚLNIE ===")
            logger.info(f"Rozpoznany tekst: {text}")
            
            # Opcjonalne: usuń plik audio jeśli nie ma być zapisany
            if not save_audio and audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
                result['audio_path'] = None
            
            return result
        
        except Exception as e:
            logger.error(f"Nieoczekiwany błąd: {e}")
            result['errors'].append(f"Błąd ogólny: {str(e)}")
            return result
    
    def transcribe_from_file(
        self, 
        file_path: str,
        apply_corrections: bool = True
    ) -> dict:
        """
        Transkrybuje istniejący plik audio
        
        Args:
            file_path: Ścieżka do pliku audio
            apply_corrections: Czy zastosować korekty ortograficzne
        
        Returns:
            Dict z kluczami: success, text, errors
        """
        result = {
            'success': False,
            'text': '',
            'errors': []
        }
        
        try:
            # Sprawdź czy plik istnieje
            if not os.path.exists(file_path):
                result['errors'].append(f"Plik nie istnieje: {file_path}")
                return result
            
            # Transkrypcja
            logger.info(f"Transkrypcja pliku: {file_path}")
            success, text_or_error = self.transcribe_audio(file_path)
            
            if not success:
                result['errors'].append(f"Transkrypcja: {text_or_error}")
                return result
            
            text = text_or_error
            
            # Dodaj interpunkcję
            text = self.add_punctuation(text)
            
            # Korekta ortograficzna
            if apply_corrections:
                text = self.apply_grammar_corrections(text)
            
            result['success'] = True
            result['text'] = text
            
            return result
        
        except Exception as e:
            logger.error(f"Błąd podczas transkrypcji pliku: {e}")
            result['errors'].append(str(e))
            return result
    
    def save_transcription_to_file(self, text: str, output_path: str) -> Tuple[bool, str]:
        """
        Zapisuje transkrypcję do pliku tekstowego
        
        Args:
            text: Tekst do zapisania
            output_path: Ścieżka do pliku wyjściowego
        
        Returns:
            Tuple (sukces, komunikat)
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                # Nagłówek z metadanymi
                f.write(f"# Transkrypcja z dnia {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")
                f.write(text)
            
            logger.info(f"Transkrypcja zapisana do: {output_path}")
            return True, f"Zapisano do: {output_path}"
        
        except Exception as e:
            logger.error(f"Błąd podczas zapisu: {e}")
            return False, str(e)
    
    def get_current_document_text(self) -> str:
        """
        Zwraca aktualny tekst dokumentu z procesora poleceń głosowych
        
        Returns:
            Aktualny tekst lub pusty string jeśli polecenia głosowe wyłączone
        """
        if self.voice_commander:
            return self.voice_commander.get_text()
        return ""
    
    def get_document_statistics(self) -> dict:
        """
        Zwraca statystyki dokumentu z procesora poleceń głosowych
        
        Returns:
            Dict ze statystykami lub pusty dict jeśli polecenia głosowe wyłączone
        """
        if self.voice_commander:
            return self.voice_commander.get_statistics()
        return {}
    
    def save_current_document(self, filepath: Optional[str] = None) -> Tuple[bool, str]:
        """
        Zapisuje aktualny dokument z procesora poleceń głosowych
        
        Args:
            filepath: Ścieżka do pliku (opcjonalna)
        
        Returns:
            Tuple (success, message)
        """
        if self.voice_commander:
            return self.voice_commander.save_document(filepath)
        return False, "Polecenia głosowe są wyłączone"
    
    def cleanup(self):
        """Zamyka narzędzia i zwalnia zasoby"""
        if self.grammar_tool:
            try:
                self.grammar_tool.close()
            except:
                pass


# Funkcja pomocnicza do łatwego użycia
def record_speech_to_text(
    duration: Optional[int] = None,
    save_audio: bool = True,
    save_text: bool = False,
    output_dir: str = 'transcriptions'
) -> dict:
    """
    Szybka funkcja do nagrywania i transkrypcji mowy
    
    Args:
        duration: Czas nagrywania w sekundach
        save_audio: Czy zapisać plik audio
        save_text: Czy zapisać transkrypcję do pliku
        output_dir: Katalog wyjściowy
    
    Returns:
        Dict z wynikami transkrypcji
    """
    processor = SpeechToTextProcessor()
    result = processor.record_and_transcribe(
        duration=duration,
        save_audio=save_audio,
        apply_corrections=True
    )
    
    # Opcjonalnie zapisz transkrypcję
    if result['success'] and save_text:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(output_dir, f'transcription_{timestamp}.txt')
        processor.save_transcription_to_file(result['text'], output_path)
    
    processor.cleanup()
    return result


# Przykład użycia
if __name__ == '__main__':
    print("=== PROTOKOLANT - Test rozpoznawania mowy ===\n")
    
    # Test 1: Nagrywanie i transkrypcja
    print("Test 1: Nagrywanie przez 5 sekund...")
    result = record_speech_to_text(duration=5, save_text=True)
    
    if result['success']:
        print(f"\n✓ Sukces!")
        print(f"Rozpoznany tekst: {result['text']}")
        if result['audio_path']:
            print(f"Plik audio: {result['audio_path']}")
    else:
        print(f"\n✗ Błąd:")
        for error in result['errors']:
            print(f"  - {error}")
