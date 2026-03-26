# Installationsguide - Hammarby Supporterklubb

Denna guide beskriver hur du installerar och konfigurerar Hammarby Supporterklubb webbplats.

## 📋 Systemkrav

### Minsta krav
- **Operativsystem**: Linux (Ubuntu 20.04+, Debian 11+), macOS 11+, Windows 10+
- **Python**: 3.9 eller högre
- **RAM**: 2GB
- **Diskutrymme**: 500MB

### Rekommenderade krav
- **Python**: 3.11 eller högre
- **RAM**: 4GB
- **Diskutrymme**: 1GB

## 🔧 Installation Steg-för-Steg

### Steg 1: Klona Repository

```bash
# Klona projektet
git clone <repository-url>
cd hammarby_website
```

### Steg 2: Skapa Python Virtual Environment

```bash
# Skapa virtual environment
python3 -m venv venv

# Aktivera virtual environment
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### Steg 3: Installera Beroenden

```bash
# Uppdatera pip
pip install --upgrade pip

# Installera projektberoenden
pip install -r requirements.txt
```

### Steg 4: Konfigurera Miljövariabler

```bash
# Kopiera exempel-miljöfil
cp .env.example .env

# Redigera miljöfilen
nano .env
```

Konfigurera följande variabler:

```bash
# Hemlig nyckel (generera med: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=din-genererade-hemliga-nyckel-har

# Flask läge
FLASK_ENV=production

# Debug läge (sätt till false i produktion)
FLASK_DEBUG=false

# Port
PORT=5000
```

### Steg 5: Skapa Mappar

```bash
# Skapa nödvändiga mappar
mkdir -p backend/uploads
mkdir -p frontend/static/images
```

### Steg 6: Lägg till Logotyp och Bilder

Placera följande bilder i `frontend/static/images/`:

- `logo.png` - Hammarby logotyp (200x50px rekommenderas)
- `favicon.png` - Favicon (32x32px)

## 🚀 Starta Applikationen

### Utvecklingsläge

```bash
# Aktivera virtual environment
source venv/bin/activate

# Kör Flask utvecklingsserver
python backend/app.py
```

Öppna webbläsaren och gå till: `http://localhost:5000`

### Produktionsläge (med Gunicorn)

```bash
# Aktivera virtual environment
source venv/bin/activate

# Kör med Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 backend.app:create_app()
```

## 🔒 HAProxy Konfiguration

För produktion bakom HAProxy, se till att `ProxyFix` är aktiverat (redan konfigurerat i `app.py`).

### HAProxy Example Configuration

```haproxy
frontend http_front
    bind *:80
    default_backend http_back

backend http_back
    option http-server-close
    option forwardfor
    server flask1 127.0.0.1:5000 check
```

## 🧪 Kör Tester

```bash
# Kör alla tester
pytest

# Kör med detaljerad output
pytest -v

# Kör med täckningsrapport
pytest --cov=backend --cov-report=html
```

## 📊 Övervakning

### Loggar

Applikationen skriver till standard output. För produktion, använd logghantering:

```bash
# Med systemd
sudo journalctl -u hammarby-web -f

# Med logrotate (konfigurera /etc/logrotate.d/hammarby-web)
```

## 🔧 Felsökning

### Problem: Import Error

```bash
# Återinstallera beroenden
pip install -r requirements.txt --force-reinstall
```

### Problem: Port Already in Use

```bash
# Hitta process som använder porten
lsof -i :5000

# Stoppa processen
kill -9 <PID>
```

### Problem: Permission Denied

```bash
# Ge rättigheter till mappar
chmod -R 755 backend/uploads
chmod -R 755 frontend/static
```

## 🔄 Uppdatering

```bash
# Dra senaste ändringar
git pull origin main

# Uppdatera beroenden
pip install -r requirements.txt --upgrade

# Starta om applikationen
```

## 📞 Support

För teknisk support:
- **Email**: info@hammarby-support.se
- **Telefon**: +46 8 123 456 78

## ✅ Verifiering

Efter installation, verifiera att allt fungerar:

1. ✅ Applikationen startar utan fel
2. ✅ Hemsidan visas på http://localhost:5000
3. ✅ Alla tester går igenom (`pytest`)
4. ✅ CSS och JavaScript laddas korrekt
5. ✅ Responsiv design fungerar på mobil

**Första och främsta! 🟢⚪**
