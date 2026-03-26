# Hammarby Supporterklubb - Webbplats

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Officiell webbplats för Hammarby Supporterklubb. Byggd med Flask och modern webbutveckling.

## 🟢 Första och främsta!

Denna webbplats är designad för att hantera medlemskap, event, och kommunikation för Hammarby Supporterklubb.

## ✨ Funktioner

- **Responsiv Design** - Fungerar perfekt på alla enheter
- **Medlemshantering** - Registrering och inloggning
- **Eventkalender** - Översikt över kommande event
- **Modern UI** - Hammarby-färger (#217A4A grön)
- **HAProxy-kompatibel** - Optimerad för produktion

## 📋 Krav

- Python 3.9 eller högre
- pip (Python package manager)
- Git

## 🚀 Snabbstart

```bash
# Klona repository
git clone <repository-url>
cd hammarby_website

# Installera beroenden
pip install -r requirements.txt

# Kör applikationen
python backend/app.py
```

## 📁 Projektstruktur

```
hammarby_website/
├── backend/              # Flask applikation
│   ├── app.py           # Huvudapplikation
│   ├── routes/          # Route handlers
│   ├── services/        # Business logic
│   └── utils/           # Hjälpfunktioner
├── frontend/            # Frontend resurser
│   ├── templates/       # HTML templates
│   └── static/          # CSS, JS, images
├── tests/               # Testfiler (TDD)
├── docs/                # Dokumentation
├── requirements.txt     # Python beroenden
├── README.md           # Denna fil
└── INSTALLATION.md     # Installationsguide
```

## 🧪 Testning

Projektet följer TDD-principer (Test-Driven Development):

```bash
# Kör alla tester
pytest

# Kör med detaljerad output
pytest -v

# Kör med täckningsrapport
pytest --cov=backend
```

## 🔧 Konfiguration

Applikationen använder miljövariabler för konfiguration:

```bash
# Viktiga variabler
SECRET_KEY=din-hemliga-nyckel
FLASK_ENV=production
FLASK_DEBUG=false
```

## 📝 Bidra

1. Fork projektet
2. Skapa en feature branch (`git checkout -b feature/AmazingFeature`)
3. Commita dina ändringar (`git commit -m 'Add some AmazingFeature'`)
4. Pusha till branchen (`git push origin feature/AmazingFeature`)
5. Öppna en Pull Request

## 📄 Licens

Denna projekt är licensierat under MIT-lisens - se LICENSE-filen för detaljer.

## 👥 Kontakt

- Email: info@hammarby-support.se
- Telefon: +46 8 123 456 78

**Första och främsta! 🟢⚪**
