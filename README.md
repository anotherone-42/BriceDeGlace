# BriceDeGlace

Application mobile avec backend Flask pour lancer une machine à glaçons automatiquement en fonction de l'heure. (oui, vraiment...)  
J'utilise:  
une Raspberry Pi 3 Model B+ [link](https://www.amazon.fr/dp/B0BNJPL4MW?ref=ppx_yo2ov_dt_b_fed_asin_title),  
une alim 5V 3000mA [link](https://www.amazon.fr/dp/B01M58O9M9?ref=ppx_yo2ov_dt_b_fed_asin_title),   
un cervo-moteur [link](https://www.amazon.fr/-/en/Lightweight-Digital-Airplane-Compatible-Raspberry/dp/B0DSPYZ4SH?dib=eyJ2IjoiMSJ9.ZsMzvmnSFrxXo0Q3IGJOFNhiQbcuiW6ZppOSfn85HPXE1LPD_0W0mQSuA19cSkQSdzyk7O6Vc3FWdJqFvmdLDFRq8oErJE0XmiXFPjmqxA-B_XpTi-kWZQ3y0XfPT8E8b_sW698bQR5gk1fKFLf5aSmjvlHgGC9ndkglvHwY322wEvYSeBWIJlOCtUKhQp19SUdqMCy4WuI72zeZngIns8_Ep6cZtJgeZDI-OM0jf0WzVfs6775hT5v3bkstvcptvh-ks1mTP_culljxbh1KD5MCdnEs9Ch8kHkguEuCw-c.pGdqe7OXmV_RRn7furPyuz-6bAIpyhG1IUpSw2wite4&dib_tag=se&keywords=5V%2BServo&qid=1756139796&sr=8-15&th=1)   
et des fichiers 3D:  
maintient du cervo [link](https://www.thingiverse.com/thing:2806324),  
bras 1 [link](https://www.thingiverse.com/thing:104561),  
bras 2 [link](https://www.thingiverse.com/thing:421726)  

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
