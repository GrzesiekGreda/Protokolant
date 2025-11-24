# Protokolant - Funkcja rozpoznawania mowy

## 📋 Opis

Główna funkcja projektu Protokolant do **automatycznej transkrypcji mowy na tekst** z uwzględnieniem:
- ✅ **Automatycznej interpunkcji** (kropki, przecinki, znaki zapytania)
- ✅ **Korekty ortograficznej** polskiego języka
- ✅ **Korekty gramatycznej** 
- ✅ **Zapisu do pliku** w formacie tekstowym

---

## 🎯 Główna funkcja: `record_and_transcribe()`

### Lokalizacja
`src/speech_to_text.py` → Klasa `SpeechToTextProcessor`

### Parametry
```python
def record_and_transcribe(
    duration: Optional[int] = None,      # Czas nagrywania w sekundach (None = auto)
    save_audio: bool = True,             # Czy zapisać plik audio
    apply_corrections: bool = True       # Czy zastosować korekty ortograficzne
) -> dict:
```

### Zwraca
```python
{
    'success': True/False,               # Czy operacja się powiodła
    'text': 'Rozpoznany tekst...',      # Transkrybowany tekst
    'audio_path': 'ścieżka/do/pliku',   # Ścieżka do nagranego audio
    'errors': []                         # Lista błędów (jeśli wystąpiły)
}
```

---

## 🚀 Przykłady użycia

### 1. Prosty przykład - Nagrywanie przez 5 sekund
```python
from src.speech_to_text import record_speech_to_text

# Nagraj i transkrybuj
result = record_speech_to_text(duration=5)

if result['success']:
    print(f"Rozpoznany tekst: {result['text']}")
    print(f"Plik audio: {result['audio_path']}")
else:
    print(f"Błędy: {result['errors']}")
```

### 2. Nagrywanie do momentu ciszy
```python
from src.speech_to_text import record_speech_to_text

# Automatyczne wykrycie końca mowy
result = record_speech_to_text(duration=None)  # None = auto-stop
```

### 3. Użycie klasy z pełną kontrolą
```python
from src.speech_to_text import SpeechToTextProcessor

# Inicjalizacja procesora
processor = SpeechToTextProcessor(
    language='pl-PL',
    use_whisper=True  # Użyj OpenAI Whisper (lepsza jakość)
)

# Nagrywanie i transkrypcja
result = processor.record_and_transcribe(
    duration=10,
    save_audio=True,
    apply_corrections=True
)

# Wyświetl wynik
if result['success']:
    print(result['text'])
    
    # Opcjonalnie zapisz do pliku
    processor.save_transcription_to_file(
        text=result['text'],
        output_path='protocols/meeting_2025-01-15.txt'
    )

# Zwolnij zasoby
processor.cleanup()
```

### 4. Transkrypcja istniejącego pliku audio
```python
from src.speech_to_text import SpeechToTextProcessor

processor = SpeechToTextProcessor()

# Transkrybuj plik
result = processor.transcribe_from_file(
    file_path='recordings/meeting.wav',
    apply_corrections=True
)

if result['success']:
    print(result['text'])

processor.cleanup()
```

---

## 🔧 Technologie

### Silniki rozpoznawania mowy
1. **OpenAI Whisper** (domyślny, najlepsza jakość)
   - Automatyczna interpunkcja
   - Wysoka dokładność dla języka polskiego
   - Działa offline po pobraniu modelu

2. **Google Speech Recognition** (fallback)
   - Wymaga połączenia internetowego
   - Podstawowa interpunkcja dodawana przez algorytm heurystyczny

### Korekta ortografii
- **LanguageTool** dla języka polskiego
- Automatyczna korekta błędów ortograficznych
- Sugestie poprawek gramatycznych

---

## 📊 Proces transkrypcji

```
┌─────────────────┐
│  1. Nagrywanie  │ → Mikrofon → Kalibracja szumu → Nagranie WAV
└────────┬────────┘
         │
┌────────▼────────┐
│ 2. Transkrypcja │ → Whisper AI / Google → Tekst bez interpunkcji
└────────┬────────┘
         │
┌────────▼────────┐
│ 3. Interpunkcja │ → Dodanie kropek, przecinków, znaków zapytania
└────────┬────────┘
         │
┌────────▼────────┐
│ 4. Korekta      │ → LanguageTool → Poprawiony tekst
└────────┬────────┘
         │
┌────────▼────────┐
│ 5. Zapis        │ → Plik TXT / Baza danych / Zwrot do użytkownika
└─────────────────┘
```

---

## 🌐 API Endpointy

### POST `/api/record-speech`
Nagrywa i transkrybuje mowę

**Request Body:**
```json
{
    "duration": 5,        // Opcjonalnie: czas w sekundach
    "field": "title"      // Opcjonalnie: identyfikator pola
}
```

**Response:**
```json
{
    "success": true,
    "text": "Zebranie zarządu w sprawie budżetu",
    "audio_path": "recordings/recording_20250115_143022.wav",
    "message": "Transkrypcja zakończona pomyślnie"
}
```

### POST `/api/transcribe-file`
Transkrybuje wgrany plik audio

**Form Data:**
- `audio_file`: Plik audio (WAV, MP3, M4A, itp.)

**Response:**
```json
{
    "success": true,
    "text": "Transkrybowany tekst z pliku audio...",
    "message": "Transkrypcja zakończona pomyślnie"
}
```

---

## 🎤 Interfejs użytkownika

W formularzu tworzenia protokołu każde pole tekstowe ma przycisk 🎤:

```html
<input type="text" id="title" name="title">
<button onclick="recordSpeech('title')">🎤</button>
```

**JavaScript:**
```javascript
async function recordSpeech(fieldId, duration = null) {
    // Wywołanie API
    const response = await fetch('/api/record-speech', {
        method: 'POST',
        body: JSON.stringify({ duration, field: fieldId })
    });
    
    const result = await response.json();
    
    if (result.success) {
        document.getElementById(fieldId).value = result.text;
    }
}
```

---

## 📦 Wymagania systemowe

### Instalacja zależności
```bash
pip install -r requirements.txt
```

### Biblioteki
- `SpeechRecognition==3.10.0` - Rozpoznawanie mowy
- `pyaudio==0.2.14` - Nagrywanie audio z mikrofonu
- `openai-whisper==20231117` - Model AI do transkrypcji
- `language-tool-python==2.8` - Korekta ortografii
- `torch==2.1.1` - Backend dla Whisper AI

### Windows - PyAudio
```bash
# Jeśli pip install pyaudio nie działa:
pip install pipwin
pipwin install pyaudio
```

### Linux - PyAudio
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

---

## 🔍 Testowanie funkcji

Plik testowy: `src/speech_to_text.py`

```bash
# Uruchom test
cd c:\Users\g.greda\Documents\VisualStudioCode\SMK\Protokolant
python src/speech_to_text.py
```

**Wynik testu:**
```
=== PROTOKOLANT - Test rozpoznawania mowy ===

Test 1: Nagrywanie przez 5 sekund...
=== ROZPOCZYNAM NAGRYWANIE ===
Nasłuchiwanie... Proszę mówić.
Nagrywanie przez 5 sekund...
Nagranie zapisane: recordings/recording_20250115_143022.wav
=== ROZPOCZYNAM TRANSKRYPCJĘ ===
Transkrypcja za pomocą Whisper AI...
Transkrypcja zakończona pomyślnie
=== DODAWANIE INTERPUNKCJI ===
=== KOREKTA ORTOGRAFICZNA ===
Zastosowano 2 poprawek ortograficznych
=== ZAKOŃCZONO POMYŚLNIE ===
Rozpoznany tekst: Zebranie zarządu w sprawie budżetu na rok 2025.

✓ Sukces!
Rozpoznany tekst: Zebranie zarządu w sprawie budżetu na rok 2025.
Plik audio: recordings/recording_20250115_143022.wav
```

---

## 📝 Struktura plików

```
Protokolant/
├── src/
│   ├── speech_to_text.py      # ← GŁÓWNY MODUŁ
│   ├── routes.py              # API endpointy
│   └── utils.py
├── recordings/                # Nagrania audio
├── transcriptions/            # Zapisane transkrypcje
├── uploads/                   # Tymczasowe pliki
└── templates/
    └── create_protocol.html   # Formularz z przyciskami 🎤
```

---

## 🛠️ Konfiguracja

### Zmiana modelu Whisper
```python
# W src/speech_to_text.py
processor = SpeechToTextProcessor()

# Dostępne modele: tiny, base, small, medium, large
processor.whisper_model = whisper.load_model("medium")  # Lepsza jakość, wolniejsze
```

### Wyłączenie Whisper (użyj Google)
```python
processor = SpeechToTextProcessor(use_whisper=False)
```

### Zmiana języka
```python
processor = SpeechToTextProcessor(
    language='en-US',  # Angielski
    use_whisper=True
)
```

---

## 🎯 Zastosowania

1. **Tworzenie protokołów** - Dyktowanie treści spotkania
2. **Notatki głosowe** - Szybkie zapisywanie pomysłów
3. **Transkrypcja nagrań** - Automatyczna obróbka plików audio
4. **Dokumentacja** - Głosowe tworzenie dokumentów
5. **Dostępność** - Dla osób z trudnościami w pisaniu

---

## 🐛 Rozwiązywanie problemów

### Błąd: "Microphone not found"
```bash
# Sprawdź dostępne mikrofony
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

### Błąd: "PyAudio could not be imported"
```bash
# Windows
pip install pipwin
pipwin install pyaudio

# Linux
sudo apt-get install portaudio19-dev
pip install pyaudio
```

### Niska jakość rozpoznawania
- Użyj lepszego mikrofonu
- Nagrywaj w cichym pomieszczeniu
- Mów wyraźnie i w stałym tempie
- Zmień model Whisper na większy (medium/large)

---

## 📊 Parametry wydajności

| Model Whisper | Rozmiar | Czas transkrypcji* | Dokładność |
|---------------|---------|-------------------|------------|
| tiny          | 39 MB   | ~1x               | 80%        |
| base          | 74 MB   | ~2x               | 85%        |
| small         | 244 MB  | ~4x               | 90%        |
| medium        | 769 MB  | ~8x               | 95%        |
| large         | 1550 MB | ~16x              | 98%        |

*Czas dla 1 minuty nagrania na CPU

---

## 📄 Licencja

MIT License - GREDA Sp. z o.o. © 2025
