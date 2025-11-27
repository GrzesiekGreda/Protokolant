"""
Moduł do strumieniowego rozpoznawania mowy w czasie rzeczywistym
Używa PyAudio do nagrywania i Google Speech Recognition API
"""

import pyaudio
import speech_recognition as sr
import threading
import queue
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)

class StreamingRecognizer:
    """Klasa do strumieniowego rozpoznawania mowy"""
    
    def __init__(self, callback: Callable[[str, bool], None], language: str = "pl-PL"):
        """
        Inicjalizacja rozpoznawania strumieniowego
        
        Args:
            callback: Funkcja wywoływana z rozpoznanym tekstem (text, is_final)
            language: Język rozpoznawania (domyślnie polski)
        """
        self.callback = callback
        self.language = language
        self.is_running = False
        self.audio_queue = queue.Queue()
        self.recognizer = sr.Recognizer()
        
        # Konfiguracja audio
        self.CHUNK = 1024  # 1KB chunks
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000  # 16kHz dla lepszej jakości
        
        self.audio_interface = None
        self.stream = None
        self.recording_thread = None
        self.recognition_thread = None
        
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback wywoływany przez PyAudio gdy dostępne są dane audio"""
        if self.is_running:
            self.audio_queue.put(in_data)
        return (in_data, pyaudio.paContinue)
    
    def _recording_worker(self):
        """Wątek nagrywający - zbiera audio z mikrofonu"""
        try:
            self.audio_interface = pyaudio.PyAudio()
            
            # Kalibracja - znajdź najlepszy mikrofon
            device_index = None
            for i in range(self.audio_interface.get_device_count()):
                dev = self.audio_interface.get_device_info_by_index(i)
                if dev['maxInputChannels'] > 0:
                    device_index = i
                    logger.info(f"Używam mikrofonu: {dev['name']}")
                    break
            
            self.stream = self.audio_interface.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.CHUNK,
                stream_callback=self._audio_callback
            )
            
            self.stream.start_stream()
            logger.info("🎤 Rozpoczęto nagrywanie strumieniowe")
            
            # Czekaj aż nagrywanie się zakończy
            while self.is_running and self.stream.is_active():
                threading.Event().wait(0.1)
                
        except Exception as e:
            logger.error(f"Błąd w wątku nagrywania: {e}")
            self.callback(f"Błąd mikrofonu: {e}", True)
        finally:
            self._cleanup_audio()
    
    def _recognition_worker(self):
        """Wątek rozpoznający - przetwarza audio i wysyła do Google API"""
        audio_buffer = b''
        silence_threshold = 0.5  # 0.5 sekundy ciszy
        min_audio_length = 1.0   # Minimum 1 sekunda audio do rozpoznania
        
        try:
            while self.is_running:
                try:
                    # Zbieraj audio przez krótki czas
                    chunk_data = self.audio_queue.get(timeout=0.1)
                    audio_buffer += chunk_data
                    
                    # Co ~2 sekundy audio, spróbuj rozpoznać
                    buffer_duration = len(audio_buffer) / (self.RATE * 2)  # 2 bytes per sample
                    
                    if buffer_duration >= min_audio_length:
                        # Utwórz AudioData z bufora
                        audio_data = sr.AudioData(audio_buffer, self.RATE, 2)
                        
                        try:
                            # Rozpoznaj fragment (partial result)
                            text = self.recognizer.recognize_google(
                                audio_data, 
                                language=self.language,
                                show_all=False
                            )
                            
                            if text and text.strip():
                                logger.info(f"📝 Rozpoznano fragment: {text}")
                                # Wyślij częściowy wynik (is_final=False)
                                self.callback(text, False)
                                
                                # Wyczyść bufor po rozpoznaniu
                                audio_buffer = b''
                                
                        except sr.UnknownValueError:
                            # Nie rozpoznano mowy - kontynuuj zbieranie
                            pass
                        except sr.RequestError as e:
                            logger.error(f"Błąd API Google: {e}")
                            self.callback(f"Błąd połączenia: {e}", True)
                            break
                            
                except queue.Empty:
                    continue
                    
        except Exception as e:
            logger.error(f"Błąd w wątku rozpoznawania: {e}")
            self.callback(f"Błąd rozpoznawania: {e}", True)
    
    def start(self):
        """Rozpocznij strumieniowe rozpoznawanie"""
        if self.is_running:
            logger.warning("Rozpoznawanie już działa")
            return
        
        self.is_running = True
        
        # Uruchom wątek nagrywający
        self.recording_thread = threading.Thread(target=self._recording_worker, daemon=True)
        self.recording_thread.start()
        
        # Uruchom wątek rozpoznający
        self.recognition_thread = threading.Thread(target=self._recognition_worker, daemon=True)
        self.recognition_thread.start()
        
        logger.info("✅ Strumieniowe rozpoznawanie uruchomione")
    
    def stop(self):
        """Zatrzymaj strumieniowe rozpoznawanie"""
        if not self.is_running:
            return
        
        logger.info("⏹️ Zatrzymywanie rozpoznawania...")
        self.is_running = False
        
        # Zaczekaj na zakończenie wątków
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2)
        
        if self.recognition_thread and self.recognition_thread.is_alive():
            self.recognition_thread.join(timeout=2)
        
        self._cleanup_audio()
        logger.info("✅ Rozpoznawanie zatrzymane")
    
    def _cleanup_audio(self):
        """Wyczyść zasoby audio"""
        try:
            if self.stream:
                if self.stream.is_active():
                    self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            if self.audio_interface:
                self.audio_interface.terminate()
                self.audio_interface = None
        except Exception as e:
            logger.error(f"Błąd podczas czyszczenia zasobów audio: {e}")
