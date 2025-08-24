# BriceDeGlace

Application mobile avec backend Flask pour lancer une machine à glaçons automatiquement en fonction de l'heure. (oui, vraiment...)

## Structure du projet

```
BriceDeGlace/
├── backend/                    # Serveur Flask (API REST)
│   ├── servo_api.py
│   ├── schedule.json
│   └── servo.py
├── mobile/                     # Application Xamarin
│   ├── BriceDeGlace.sln
│   ├── BriceDeGlace/
│   └── BriceDeGlace.Android/
└── README.md
```

## Installation et lancement

### Backend (Serveur Flask)

```bash
# Aller dans le dossier backend
cd backend

# Installer les dépendances (recommandé : créer un environnement virtuel)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

pip install flask

# Lancer le serveur
python servo_api.py
```

Le serveur sera accessible sur `http://localhost:5000` (ou le port configuré).

### Application Mobile (Xamarin)

1. Ouvrez `mobile/BriceDeGlace.sln` dans Visual Studio ou Visual Studio for Mac
2. Configurez l'URL de votre serveur Flask dans le code dans mobile/BriceDeGlace/MainPage.cs
3. Compilez et lancez sur émulateur ou appareil

J'ai utilisé les nuggets suivants:

| NuGet   | NETStandard.Library | Newtonsoft.Json | Xamarin.Essentials | Xamarin.FFImageLoading.Forms | Xamarin.Forms |
|---------|---------------------|-----------------|--------------------|------------------------------|---------------|
| Version | 2.0.3               | 13.0.3          | 1.8.1              | 2.4.11.982                   | 5.0.0.2662    |

## Configuration

### Configuration Mobile

Modifiez l'URL du serveur dans votre code Xamarin pour pointer vers votre serveur Flask.
