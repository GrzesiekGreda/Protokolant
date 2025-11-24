# Protokolant - System Poleceń Głosowych

## 📋 Opis

System poleceń głosowych do sterowania aplikacją Protokolant. Umożliwia kontrolowanie dokumentu za pomocą głosu przez użycie słowa aktywującego **"UWAGA"** i konkretnych poleceń.

---

## 🎤 Słowo aktywujące

**"UWAGA"** - po wypowiedzeniu tego słowa system oczekuje polecenia sterującego.

---

## 📝 Dostępne polecenia

### 1. **Cofnij** - `uwaga cofnij`
Cofa ostatni tekst mówiony ciągiem.

**Przykład:**
```
Użytkownik: "Zebranie zarządu w sprawie budżetu"
Użytkownik: "Dodatkowe informacje o projekcie"
Użytkownik: "uwaga cofnij"
→ Efekt: Usuwa "Dodatkowe informacje o projekcie"
```

**Użycie w API:**
```javascript
// Nagraj mowę z poleceniem
await fetch('/api/voice-command', {
    method: 'POST',
    body: JSON.stringify({ duration: 5 })
});
```

---

### 2. **Cofnij słowo** - `uwaga cofnij słowo`
Cofa ostatnie słowo z dokumentu.

**Przykład:**
```
Dokument: "Zebranie zarządu w sprawie budżetu projektu"
Użytkownik: "uwaga cofnij słowo"
→ Efekt: "Zebranie zarządu w sprawie budżetu"
```

---

### 3. **Cofnij zdanie** - `uwaga cofnij zdanie`
Cofa ostatnie zdanie z dokumentu.

**Przykład:**
```
Dokument: "Zebranie zarządu. Omówiono budżet. Ustalono harmonogram."
Użytkownik: "uwaga cofnij zdanie"
→ Efekt: "Zebranie zarządu. Omówiono budżet."
```

**Działanie:**
- Znajduje ostatnie zakończenie zdania (`.`, `!`, `?`)
- Usuwa tekst po nim lub całe ostatnie zdanie
- Jeśli brak interpunkcji, usuwa cały tekst jako niekompletne zdanie

---

### 4. **Zapisz** - `uwaga zapisz`
Zapisuje wprowadzone zmiany do pliku.

**Przykład:**
```
Użytkownik: "uwaga zapisz"
→ Efekt: Zapisuje dokument do: transcriptions/document_20250124_153045.txt
```

**Struktura pliku:**
```
# Dokument utworzony: 24.11.2025 15:30

Zebranie zarządu w sprawie budżetu na rok 2025.
Ustalono harmonogram implementacji projektu.
```

---

### 5. **Nowy** - `uwaga nowy`
Zapisuje dotychczasowy dokument i tworzy nowy, czysty dokument.

**Przykład:**
```
Dokument: "Protokół spotkania nr 1..."
Użytkownik: "uwaga nowy"
→ Efekt: 
  1. Zapisuje "Protokół spotkania nr 1..." do pliku
  2. Czyści dokument
  3. Gotowy do wprowadzenia nowego tekstu
```

---

## 🔧 Implementacja techniczna

### Klasa główna: `VoiceCommandProcessor`

**Lokalizacja:** `src/voice_commands.py`

```python
from src.voice_commands import VoiceCommandProcessor

# Inicjalizacja
processor = VoiceCommandProcessor()

# Dodaj tekst
processor.add_text("Zebranie zarządu w sprawie budżetu.")

# Przetwórz polecenie głosowe
result = processor.process_voice_input("uwaga cofnij słowo")

if result['is_command']:
    print(f"Wykonano: {result['command_executed']}")
    print(f"Komunikat: {result['message']}")
    print(f"Aktualny tekst: {result['current_text']}")
```

---

## 🌐 API Endpoints

### POST `/api/voice-command`

Nagrywa mowę i przetwarza polecenia głosowe.

**Request Body:**
```json
{
    "duration": 5,              // Czas nagrywania (opcjonalny)
    "process_commands": true    // Czy przetwarzać polecenia (domyślnie true)
}
```

**Response (zwykły tekst):**
```json
{
    "success": true,
    "text": "Zebranie zarządu w sprawie budżetu.",
    "audio_path": "recordings/recording_20250124_153045.wav",
    "message": "Przetwarzanie zakończone pomyślnie"
}
```

**Response (z poleceniem):**
```json
{
    "success": true,
    "text": "Zebranie zarządu w sprawie",
    "audio_path": "recordings/recording_20250124_153046.wav",
    "message": "Przetwarzanie zakończone pomyślnie",
    "command_info": {
        "is_command": true,
        "command_executed": "undo_word",
        "message": "Cofnięto słowo: 'budżetu'"
    },
    "current_document": "Zebranie zarządu w sprawie",
    "statistics": {
        "words": 4,
        "sentences": 0,
        "characters": 28,
        "text_additions": 1,
        "commands_executed": 1
    }
}
```

---

## 🎯 Przykłady użycia

### Przykład 1: Dyktowanie z korektą

```python
from src.speech_to_text import SpeechToTextProcessor

# Inicjalizacja z poleceniami głosowymi
processor = SpeechToTextProcessor(enable_voice_commands=True)

# Nagraj i przetwórz
result = processor.record_and_transcribe(
    duration=None,  # Auto-stop
    process_commands=True
)

if result['success']:
    print(f"Tekst: {result['text']}")
    
    # Sprawdź czy było polecenie
    if result['command_info'] and result['command_info']['is_command']:
        print(f"Wykonano polecenie: {result['command_info']['command_executed']}")
        
        # Pobierz aktualny dokument
        current_doc = processor.get_current_document_text()
        print(f"Aktualny dokument: {current_doc}")

processor.cleanup()
```

### Przykład 2: Sesja dyktowania z wieloma poleceniami

```python
from src.voice_commands import VoiceCommandProcessor

processor = VoiceCommandProcessor()

# Dyktowanie pierwszego zdania
processor.process_voice_input("Zebranie zarządu w sprawie budżetu.")

# Dyktowanie drugiego zdania
processor.process_voice_input("Ustalono harmonogram projektu.")

# Ups, błąd w ostatnim słowie
processor.process_voice_input("uwaga cofnij słowo")

# Poprawka
processor.process_voice_input("implementacji.")

# Wyświetl wynik
print(processor.get_text())
# → "Zebranie zarządu w sprawie budżetu. Ustalono harmonogram implementacji."

# Zapisz dokument
success, message = processor.save_document()
print(message)
```

### Przykład 3: Wielodokumentowa sesja

```python
processor = VoiceCommandProcessor()

# Dokument 1
processor.add_text("Protokół spotkania nr 1. Temat: Budżet.")
processor.process_voice_input("uwaga zapisz")

# Dokument 2 (automatycznie zapisuje poprzedni)
processor.process_voice_input("uwaga nowy")
processor.add_text("Protokół spotkania nr 2. Temat: Harmonogram.")

# Statystyki
stats = processor.get_statistics()
print(f"Słowa: {stats['words']}")
print(f"Wykonanych poleceń: {stats['commands_executed']}")
```

---

## 🔍 Parser poleceń głosowych

### Jak działa rozpoznawanie?

1. **Normalizacja tekstu** - małe litery, usunięcie nadmiarowych spacji
2. **Wykrycie słowa "uwaga"** - split na to słowo
3. **Identyfikacja polecenia** - porównanie z listą poleceń (najdłuższe pierwsze)
4. **Wykonanie akcji** - wywołanie odpowiedniej metody
5. **Zwrot wyniku** - informacja o sukcesie/błędzie

### Przykład parsowania:

```python
# Input: "To jest tekst uwaga cofnij słowo i dalszy tekst"

parser_result = processor.parse_voice_input(input_text)

# Output:
# is_command = True
# command_name = "undo_word"
# remaining_text = "To jest tekst"  # przed "uwaga"
```

---

## 📊 Struktura danych

### Historia operacji

```python
processor.text_history = [
    {
        'text': 'Zebranie zarządu...',
        'timestamp': datetime(2025, 11, 24, 15, 30, 45),
        'type': 'addition'
    }
]

processor.command_history = [
    {
        'command': 'undo_word',
        'timestamp': datetime(2025, 11, 24, 15, 31, 10),
        'removed_text': 'budżetu'
    }
]
```

### Statystyki

```python
stats = processor.get_statistics()

{
    'words': 12,                # Liczba słów
    'sentences': 2,             # Liczba zdań
    'characters': 78,           # Liczba znaków
    'text_additions': 5,        # Ile razy dodano tekst
    'commands_executed': 3      # Ile poleceń wykonano
}
```

---

## ⚙️ Konfiguracja

### Zmiana słowa aktywującego

```python
# W src/voice_commands.py
class VoiceCommandProcessor:
    TRIGGER_WORD = "uwaga"  # ← Zmień tutaj
```

### Dodanie nowego polecenia

```python
# W src/voice_commands.py
class VoiceCommandProcessor:
    COMMANDS = {
        'cofnij': 'undo_text',
        'cofnij słowo': 'undo_word',
        'cofnij zdanie': 'undo_sentence',
        'nowy': 'new_document',
        'zapisz': 'save_document',
        # Dodaj nowe polecenie:
        'wyczyść': 'clear_document'  # ← Nowe
    }
    
    def clear_document(self) -> Tuple[bool, str]:
        """Nowe polecenie - czyści dokument"""
        self.current_text = ""
        return True, "Dokument wyczyszczony"
```

---

## 🧪 Testowanie

### Uruchom testy wbudowane:

```bash
cd c:\Users\g.greda\Documents\VisualStudioCode\SMK\Protokolant
python src/voice_commands.py
```

**Wynik testów:**
```
=== PROTOKOLANT - Test systemu poleceń głosowych ===

Test 1: Dodawanie tekstu
Tekst: Zebranie zarządu w sprawie budżetu.
Komunikat: Dodano tekst

Test 2: Dodanie kolejnego tekstu
Tekst: Zebranie zarządu w sprawie budżetu. Omówiono projekt na rok 2025.
Komunikat: Dodano tekst

Test 3: Polecenie 'uwaga cofnij słowo'
Polecenie: undo_word
Tekst: Zebranie zarządu w sprawie budżetu. Omówiono projekt na rok
Komunikat: Cofnięto słowo: '2025.'

Test 4: Polecenie 'uwaga cofnij zdanie'
Polecenie: undo_sentence
Tekst: Zebranie zarządu w sprawie budżetu.
Komunikat: Cofnięto zdanie: 'Omówiono projekt na rok'

...
```

---

## 🎨 Interfejs użytkownika

### Przycisk poleceń głosowych w formularzu

```html
<button type="button" class="btn btn-primary" onclick="voiceCommand()">
    🎤 Polecenie głosowe
</button>

<script>
async function voiceCommand() {
    const response = await fetch('/api/voice-command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ duration: null })  // Auto-stop
    });
    
    const result = await response.json();
    
    if (result.success && result.command_info?.is_command) {
        alert(`Wykonano: ${result.command_info.message}`);
        
        // Aktualizuj pole tekstowe
        document.getElementById('textField').value = result.current_document;
    }
}
</script>
```

---

## 🛠️ Rozwiązywanie problemów

### Problem: Polecenie nie jest rozpoznawane

**Rozwiązanie:**
- Upewnij się, że wyraźnie wypowiadasz słowo "uwaga"
- Zrób krótką pauzę po "uwaga" przed poleceniem
- Sprawdź czy model Whisper poprawnie transkrybuje polski

### Problem: Błąd "Brak tekstu do cofnięcia"

**Rozwiązanie:**
- Najpierw dodaj jakiś tekst do dokumentu
- Sprawdź czy dokument nie jest pusty: `processor.get_text()`

### Problem: Zapisywanie pliku kończy się błędem

**Rozwiązanie:**
- Sprawdź uprawnienia do zapisu w katalogu `transcriptions/`
- Utwórz katalog ręcznie: `mkdir transcriptions`

---

## 📈 Wydajność

| Operacja | Czas wykonania |
|----------|---------------|
| Parse polecenia | <1ms |
| Cofnij słowo | <1ms |
| Cofnij zdanie | 1-5ms |
| Zapis do pliku | 10-50ms |
| Pełny cykl (nagranie + polecenie) | 2-5s |

---

## 🔐 Bezpieczeństwo

- Polecenia działają tylko na lokalnym dokumencie użytkownika
- Brak możliwości nadpisania istniejących plików (timestamp w nazwie)
- Historia operacji umożliwia audyt zmian
- Brak poleceń systemowych - tylko operacje na tekście

---

## 📄 Licencja

MIT License - GREDA Sp. z o.o. © 2025
