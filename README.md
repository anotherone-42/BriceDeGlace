# BriceDeGlace
XMR address for donations: 4AJtFkiynSSiRrzcNeD2PkhRnLvd35zPt1PCng5NCDfAExn9cZ9jPnY6Bc3RkadLPLEyMCa7aWcXyL725mmrZ3BcNdSCYuH  
  
Mobile application with Flask backend to automatically launch an ice machine based on time. (yes, really...)  
I use:  
a Raspberry Pi 3 Model B+ [link](https://www.amazon.fr/dp/B0BNJPL4MW?ref=ppx_yo2ov_dt_b_fed_asin_title),  
a 5V 3000mA power supply [link](https://www.amazon.fr/dp/B01M58O9M9?ref=ppx_yo2ov_dt_b_fed_asin_title),  
a servo motor [link](https://www.amazon.fr/dp/B0BZPP3R5S?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1)  
and 3D files:  
servo mount [link](https://www.thingiverse.com/thing:2806324),  
arm 1 [link](https://www.thingiverse.com/thing:104561),  
  
Servo connections:  
+5V servo => +5V RPI  
GND servo => GND RPI  
Signal servo => GPIO 18 (pin 12) RPI  
RPi3 Model B IO Pins [link](https://raspberry-projects.com/pi/pi-hardware/raspberry-pi-3-model-b/rpi3-model-b-io-pins)  
  
<img width="598" height="539" alt="image" src="https://github.com/user-attachments/assets/a3df4ffe-565e-4674-81ef-c2d6e45afcbf" />  
  
## Project Structure
  
```
BriceDeGlace/
├── backend/ # Flask Server (REST API)
│ ├── servo_api.py
│ ├── schedule.json
│ └── servo.py
├── mobile/ # Xamarin Application
│ ├── BriceDeGlace.sln
│ ├── BriceDeGlace/
│ └── BriceDeGlace.Android/
└── README.md
```
  
## Installation and Launch

### Backend (Flask Server)

```bash
# Go to the backend folder
cd backend

# Install dependencies (recommended: create a virtual environment)
python -m venv venv
source venv/bin/activate # Linux/Mac
# or venv\Scripts\activate # Windows

pip install flask schedule RPi.GPIO

# Launch the server
python servo_api.py
```

The server will be accessible at `http://localhost:5000` (or the configured port).  

### Mobile Application (Xamarin)

1. Open `mobile/BriceDeGlace.sln` in Visual Studio or Visual Studio for Mac  
2. Configure your Flask server URL in the code in mobile/BriceDeGlace/MainPage.cs  
3. Compile and run on emulator or device  

I used the following NuGet packages:  

| NuGet | Version |
|------------------------------|------------|
| NETStandard.Library | 2.0.3 |
| Newtonsoft.Json | 13.0.3 |
| Xamarin.Essentials | 1.8.1 |
| Xamarin.FFImageLoading.Forms | 2.4.11.982 |
| Xamarin.Forms | 5.0.0.2662 |

## Configuration

### Mobile Configuration

Modify the server URL in your Xamarin code to point to your Flask server.  
`/mobile/BriceDeGlace/MainPage.cs`
