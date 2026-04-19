# Plan: Hjemmeserver med Flask-app og PostgreSQL

## Oversikt

Mål: Kjøre Flask-app ("Spillturnering og Liga") hjemmefra med PostgreSQL-database.

---

## Del 1: Forberedelser

### 1.1 Sjekk gammel PC
- [ ] Blås støv av maskinen
- [ ] Test om den starter
- [ ] Sjekk specs (CPU, RAM, disk)

### 1.2 Last ned operativsystem
**Anbefalt:** Ubuntu Server 22.04 LTS

Last ned fra: https://ubuntu.com/download/server

### 1.3 Installer Ubuntu Server
1. Lag bootbar USB med Rufus (Windows) eller Etcher (Mac/Linux)
2. Boot fra USB
3. Følg installasjonsveiledningen
4. **Tips:** Velg "LVM" og "Encrypt" hvis du vil ha kryptering

### 1.4 Første oppsett etter installasjon
```bash
# Oppdater systemet
sudo apt update && sudo apt upgrade -y

# Sett til norsk/tidsone
sudo timedatectl set-timezone Europe/Oslo
```

---

## Del 2: PostgreSQL Database

### 2.1 Installer PostgreSQL
```bash
sudo apt install postgresql postgresql-contrib -y
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### 2.2 Opprett database og bruker
```bash
# Bytt til postgres-bruker
sudo -u postgres psql

# Kjør disse kommandoene i psql:
CREATE DATABASE gaming_liga;

-- (Bytt ut 'ditt_passord' med ditt eget passord)
CREATE USER appuser WITH PASSWORD 'ditt_passord';

GRANT ALL PRIVILEGES ON DATABASE gaming_liga TO appuser;

-- Gå ut av psql med \q
\q
```

### 2.3 Test tilkobling
```bash
# Bytt 'appuser' og 'ditt_passord' med dine verdier
psql -h localhost -U appuser -d gaming_liga
```

**Miljøvariabler du trenger (for appconfig.py):**
```
DATABASE_URL=postgresql://appuser:ditt_passord@localhost:5432/gaming_liga
```

---

## Del 3: Flask-app på server

### 3.1 Installer avhengigheter
```bash
# Installere Python og verktøy
sudo apt install python3 python3-venv python3-pip git -y

# Klone appen (endre URL til din egen git URL)
cd ~
git clone https://github.com/Teiteland/tourneyandleaguesforfriends.git
cd tourneyandleaguesforfriends

# Opprette virtuell environment
python3 -m venv venv
source venv/bin/activate

# Installere avhengigheter
pip install -r requirements.txt
```

### 3.2 Konfigurer miljøvariabler
```bash
# Lag .env-fil
nano .env
```

Innhold:
```
FLASK_APP=app
FLASK_ENV=production
SECRET_KEY=lag-en-sikker-random-string-her
DATABASE_URL=postgresql://appuser:ditt_passord@localhost:5432/gaming_liga
```

### 3.3 Initialiser database
```bash
# Aktiver venv hvis ikke allerede aktivt
source venv/bin/activate

# Sett miljøvariabler og initialiser
export $(cat .env | xargs) && flask init-db
```

---

## Del 4: Automatisk oppstart med systemd

### 4.1 Opprett systemd service
```bash
sudo nano /etc/systemd/system/gaming-liga.service
```

Innhold:
```ini
[Unit]
Description=Gaming Liga Flask App
After=network.target postgresql.service

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/tourneyandleaguesforfriends
Environment="PATH=/home/ubuntu/tourneyandleaglesforfriends/venv/bin"
Environment="FLASK_APP=app"
Environment="FLASK_ENV=production"
Environment="DATABASE_URL=postgresql://appuser:ditt_passord@localhost:5432/gaming_liga"
Environment="SECRET_KEY=din-sikre-key-her"
ExecStart=/home/ubuntu/tourneyandleaglesforfriends/venv/bin/gunicorn -b 127.0.0.1:5000 "app:create_app()" --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4.2 Aktiver og start
```bash
sudo systemctl daemon-reload
sudo systemctl enable gaming-liga
sudo systemctl start gaming-liga

# Sjekk status
sudo systemctl status gaming-liga
```

---

## Del 5: Nettverk - Tilgang utenfra

### 5.1 Installer og konfigurer Nginx som reverse proxy
```bash
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/gaming-liga
```

Innhold:
```nginx
server {
    listen 80;
    server_name din-domene.no ELLER IP-ADRESSE;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 5.2 Aktiver og test
```bash
sudo ln -s /etc/nginx/sites-available/gaming-liga /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5.3 Konfigurer brannmur
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp  # Hvis du skal bruke HTTPS
sudo ufw enable
```

### 5.4 Port-forwarding på ruter
Dette varierer per ruter, men generelt:
1. Logg inn på ruterens admin-grensesnitt
2. Gå til "Port Forwarding" eller "NAT"
3. Forward port 80 og 443 til serverens interne IP-adresse

---

## Del 6: Sette opp Dynamic DNS (hvis du vil ha fast domene)

### Alternativ 1: Gratis DDNS-tjenester
- **DuckDNS** (anbefalt): https://duckdns.org
- **No-IP**: https://no-ip.com

### Alternativ 2: Bruke IP direkte
Du kan la andre koble til via din offentlige IP-adresse:
```bash
# Finn din offentlige IP
curl ifconfig.me
```

---

## Del 7: Backup

### 7.1 Backup-script
```bash
sudo nano /usr/local/bin/backup-db.sh
```

Innhold:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"
mkdir -p $BACKUP_DIR

pg_dump -U appuser gaming_liga > $BACKUP_DIR/db_$DATE.sql

# Behold kun siste 7 dager
find $BACKUP_DIR -name "db_*.sql" -mtime +7 -delete
```

### 7.2 GjørScript kjørbart og sett opp cron
```bash
sudo chmod +x /usr/local/bin/backup-db.sh

# Legg til cron jobb (kjører daglig kl 02:00)
sudo crontab -e
# Legg til denne linjen:
# 0 2 * * * /usr/local/bin/backup-db.sh
```

---

## Sjekkliste for fremgang

| Oppgave | Status |
|--------|--------|
| PC sjekket og fungerer | [ ] |
| Ubuntu Server installert | [ ] |
| PostgreSQL installert | [ ] |
| Database opprettet | [ ] |
| Flask-app lastet ned | [ ] |
| Gunicorn service opprettet | [ ] |
| Nginx konfigurert | [ ] |
| Brannmur konfigurert | [ ] |
| Port-forwarding satt opp | [ ] |
| Backup-script installert | [ ] |

---

## Nyttig kommandoer

```bash
# Sjekke app-status
sudo systemctl status gaming-liga

# Restart app
sudo systemctl restart gaming-liga

# Se logger
sudo journalctl -u gaming-liga -f

# Sjekke diskplass
df -h

# Sjekke minne
free -h
```

---

## Ressurser

- Ubuntu Server guide: https://ubuntu.com/tutorials/install-ubuntu-server
- PostgreSQL dokumentasjon: https://www.postgresql.org/docs/
- Flask + Gunicorn: https://docs.gunicorn.org/
- Nginx: https://nginx.org/en/docs/

---

*Oppdater denne listen etter hvert som du blir ferdig med hvert steg!*

  Session   Project kickoff: AGENTS.md for Mario Kart 8 tourn…
  Continue  opencode -s ses_2a34772fdffe6v7AOd84WaySrn

SQL
---
Lag admin
INSERT INTO "user" (username, email, password_hash, is_admin, is_locked, failed_login_attempts)
VALUES ('DittNavn', 'epost@domene.no', 'bcrypt:hash', TRUE, FALSE, 0);
Hvis bruker finnes:

SQL for å gjøre en bruker til admin i DBeaver
Kjør denne setningen (bytt ut epost og navn):
UPDATE "user" 
SET is_admin = TRUE 
WHERE email = 'epost@domene.no' 
   OR username = 'brukernavn';
Eksempel med Teiteland:
UPDATE "user" 
SET is_admin = TRUE 
WHERE email = 'even.teigland@gmail.com';
---
Andre nyttige setninger
Låse opp bruker:
UPDATE "user" 
SET is_locked = FALSE, failed_login_attempts = 0
WHERE email = 'epost@domene.no';
Sjekke alle admins:
SELECT username, email, is_admin FROM "user" WHERE is_admin = TRUE;

---

-- Migrer alle Users til Players (unngår duplikater)
INSERT INTO player (name, is_dummy)
SELECT u.username, FALSE
FROM "user" u
WHERE NOT EXISTS (
    SELECT 1 FROM player p WHERE p.name = u.username
);
Kjør deretter:
-- Verifiser migreringen
SELECT p.id, p.name, p.is_dummy, u.username
FROM player p
LEFT JOIN "user" u ON p.name = u.username
ORDER BY p.id;

