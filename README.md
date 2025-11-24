# Protokolant

**Aplikacja do zarządzania protokołami i notatkami ze spotkań**

## Opis

Protokolant to aplikacja webowa w Pythonie, która pomaga organizacjom profesjonalnie dokumentować spotkania, decyzje i zadania. Umożliwia tworzenie, przeglądanie i eksportowanie protokołów ze spotkań w przejrzysty sposób.

## Funkcje

- ✅ Tworzenie protokołów ze spotkań
- ✅ Rejestrowanie uczestników, agend i decyzji
- ✅ Śledzenie zadań z terminami realizacji
- ✅ Eksport do PDF
- ✅ Wyszukiwanie i filtrowanie protokołów
- ✅ Responsywny interfejs webowy

## Wymagania

- Python 3.12 lub nowszy
- pip (menadżer pakietów Python)
- Przeglądarka internetowa (Chrome, Firefox, Edge)

## Instalacja

1. Sklonuj repozytorium:
```bash
git clone https://github.com/GrzesiekGreda/Protokolant.git
cd Protokolant
```

2. Utwórz środowisko wirtualne:
```bash
python -m venv venv
```

3. Aktywuj środowisko wirtualne:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

## Uruchomienie

```bash
python run.py
```

Aplikacja będzie dostępna pod adresem: http://localhost:5000

## Użycie

1. Otwórz przeglądarkę i wejdź na http://localhost:5000
2. Kliknij "Nowy protokół" aby utworzyć protokół ze spotkania
3. Wypełnij formularz z danymi spotkania
4. Dodaj uczestników, punkty agendy i zadania
5. Zapisz protokół
6. Eksportuj do PDF lub przeglądaj w interfejsie webowym

## Struktura projektu

```
Protokolant/
├── src/              # Kod źródłowy aplikacji
├── templates/        # Szablony HTML
├── static/           # Pliki CSS/JS
├── data/             # Baza danych
├── requirements.txt  # Zależności Python
└── run.py           # Punkt wejścia aplikacji
```

## Technologie

- **Backend**: Python 3.12, Flask
- **Database**: SQLite + SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **PDF**: ReportLab / WeasyPrint

## Rozwój

Projekt wykorzystuje `.github/copilot-instructions.md` do wsparcia rozwoju przez AI coding agents.

## Licencja

MIT License

## Autor

Grzegorz Greda - GREDA Sp. z o.o.

## Wsparcie

W razie pytań lub problemów, otwórz issue w repozytorium GitHub.
