## 🗂️ Projekt Struktur

```bash
growvolution.org/
├── admin_api/              # Package der Admin API
    ├── ...                 # Inspiriert von website/
├── website/                # Package der Flask-App
    ├── data/               # Flask SQLAlchemy Daten der Seite
    ├── logic/              # Strukturierte Logik der Routes
    ├── routing/            # Routing der Seite (übergibt Handling an 'logic/')
    ├── socket/             # Flask SocketIO Package
        ├── events/         # Eventhandling
        ├── messages/       # Gezielt Nachrichten an aktive Clients senden
    ├── static/
        ├── css/            # Eigene Styles
        ├── js/             # Frontend Logik
        ├── img/            # Bilder
    ├── subsites/           # Subsites der Seite (für subdomains)
        ├── learning/       # Lernplattform (in Planung)
            ├── ...         # Aufbau ähnlich wie website/
        ├── people/         # Für Interna (Verein, ...)
            ├── ...         # wie website/
        ├── banking/        # Banking-System (in Planung)
            ├── ...         # wie website/
    ├── templates/          # HTML Templates (Jinja2)
    ├── utils/              # Tools der App
    ├── ...
├── shared/                 # Geteilte Basismodule beider Apps
    ├── ...
├── docker/                 # Dev Container System
    ├── ...
├── .md/                    # Markdown Hilfen & Erklärungen
    ├── PICTURES.md         # Auf der Seite verwendete Bilder (CC0)
    ├── ...
├── requirements.txt        # Abhängigkeiten
├── run.sh                  # Wird von systemd geladen -> startet die Admin API
├── ...                             
```

Schau dich gern ein wenig um, ich bin sehr bemüht es übersichtlich und tragfähig für den weiteren Ausbau zu halten.
Wenn du Fragen oder Feedback hast, bin ich immer offen dafür! ✌🏼
