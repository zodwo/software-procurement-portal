# Portal Zamówień Oprogramowania - Instrukcja

Projekt uniwersytecki: automatyzacja nadawania uprawnień do oprogramowania z AI

## 📁 Pliki w projekcie

- `app.py` - główna aplikacja Streamlit
- `catalogue.json` - katalog dostępnego oprogramowania
- `requirements.txt` - wymagane biblioteki Python
- `README.md` - ten plik z instrukcjami

## 🚀 Jak uruchomić projekt

### Krok 1: Stwórz nowe repozytorium na GitHub

1. Zaloguj się na GitHub
2. Kliknij "+" w prawym górnym rogu → "New repository"
3. Nazwa: `software-procurement-portal` (lub inna)
4. Ustaw jako **Public**
5. Kliknij "Create repository"

### Krok 2: Wgraj pliki do repozytorium

1. W swoim nowym repozytorium kliknij "uploading an existing file"
2. Przeciągnij wszystkie 4 pliki:
   - `app.py`
   - `catalogue.json`
   - `requirements.txt`
   - `README.md`
3. Kliknij "Commit changes"

### Krok 3: Stwórz konto Anthropic API (dla AI)

1. Idź na: https://console.anthropic.com/
2. Zarejestruj się (darmowe konto)
3. Przejdź do "API Keys"
4. Kliknij "Create Key"
5. Skopiuj klucz (zaczyna się od `sk-ant-...`)
6. **ZAPISZ GO BEZPIECZNIE** - będzie potrzebny później

### Krok 4: Stwórz konto Gmail dla projektu

1. Stwórz nowy Gmail: https://accounts.google.com/signup
2. Nazwa: np. `software.portal.projekt@gmail.com`
3. Po utworzeniu, włącz App Password:
   - Idź do: https://myaccount.google.com/security
   - "2-Step Verification" → włącz (wymagane dla App Password)
   - Wróć do Security → "App passwords"
   - Wybierz "Mail" i "Other" → wpisz "Streamlit App"
   - Skopiuj 16-znakowy kod (bez spacji)
   - **ZAPISZ GO** - będzie potrzebny później

### Krok 5: Wdróż na Streamlit Community Cloud

1. Idź na: https://share.streamlit.io/
2. Zaloguj się przez GitHub
3. Kliknij "New app"
4. Wybierz:
   - Repository: `twoje-konto/software-procurement-portal`
   - Branch: `main`
   - Main file path: `app.py`
5. Kliknij "Advanced settings"
6. W sekcji "Secrets" wklej:

```toml
ANTHROPIC_API_KEY = "sk-ant-twój-klucz-tutaj"
GMAIL_ADDRESS = "twoj.email@gmail.com"
GMAIL_APP_PASSWORD = "twoj-16-znakowy-kod"
```

7. Zamień wartości na swoje prawdziwe dane
8. Kliknij "Deploy!"

### Krok 6: Gotowe! 🎉

Aplikacja będzie dostępna pod adresem typu: `https://twoja-nazwa-app.streamlit.app`

Ten link możesz otworzyć na dowolnym urządzeniu i pokazać podczas prezentacji!

## 🧪 Jak przetestować

1. Otwórz aplikację
2. Wpisz w polu AI: "potrzebuję stworzyć diagramy procesów"
3. Kliknij "Uzyskaj rekomendację AI"
4. AI zasugeruje Microsoft Visio
5. Wpisz swój login i email
6. Kliknij "Zamów oprogramowanie"
7. Sprawdź email - powinno przyjść potwierdzenie!

## 📊 Co się dzieje w tle

1. AI (Claude) analizuje Twój opis i szuka najlepszego dopasowania w katalogu
2. Po zamówieniu dane trafiają do pliku Excel `user_registry.xlsx`
3. Email z potwierdzeniem jest wysyłany automatycznie przez Gmail
4. Wszystko działa w chmurze - zero instalacji lokalnych!

## ⚠️ Rozwiązywanie problemów

**Aplikacja nie działa po wdrożeniu:**
- Sprawdź czy Secrets są poprawnie ustawione w Streamlit
- Upewnij się że klucz API zaczyna się od `sk-ant-`
- Sprawdź czy App Password z Gmail ma 16 znaków bez spacji

**Email nie przychodzi:**
- Sprawdź folder SPAM
- Upewnij się że 2-Step Verification jest włączona na Gmail
- Sprawdź czy użyłaś App Password, nie zwykłego hasła

**AI nie rekomenduje:**
- Sprawdź czy ANTHROPIC_API_KEY jest ustawiony
- Sprawdź czy masz dostępny limit API (free tier: $5/miesiąc)

## 📝 Podczas prezentacji

1. Pokaż live demo - otwórz link na projektorze
2. Poproś kogoś z klasy o wpisanie swojego emaila i potrzeby
3. Zaprezentuj jak AI rekomenduje oprogramowanie
4. Pokaż że email przychodzi od razu (możesz sprawdzić na telefonie)
5. Otwórz plik `user_registry.xlsx` na GitHub i pokaż że dane się zapisały

## 🎓 Mapowanie do briefu

- **AS-IS proces:** Manual, przez ticketing, czeka na IT
- **TO-BE proces:** Self-service, AI-driven, instant
- **Technologie:** Streamlit (prototyp), Claude API (AI), Gmail (notyfikacje)
- **Dane:** JSON (katalog), Excel (rejestr), Email (potwierdzenia)

Powodzenia w projekcie! 🚀
