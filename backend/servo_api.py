#!/usr/bin/env python3
"""
Brice Controller API Server
Serveur Flask pour contrôler le servo et gérer les horaires
"""

from flask import Flask, request, jsonify
import json
import os
from datetime import datetime
import logging
import threading
import time

# Importer les fonctions du servo depuis servo.py
try:
    from servo import activate_servo
except ImportError:
    print("❌ Erreur: Impossible d'importer servo.py")
    print("💡 Assurez-vous que servo.py existe dans le même dossier")
    # Fonction de fallback si servo.py n'existe pas
    def activate_servo():
        print("⚠️ Fonction servo simulée (servo.py non trouvé)")
        return True

# Configuration de l'app Flask
app = Flask(__name__)

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuration
SCHEDULE_FILE = 'schedule.json'

# Variables globales pour le scheduler
scheduler_running = False
last_activation = {"midi": None, "soir": None}

def log_request():
    """Log les détails de la requête"""
    print(f"🌐 {request.method} {request.url} depuis {request.remote_addr}")
    if request.is_json and request.get_json():
        print(f"📊 Data: {request.get_json()}")

def check_and_activate_servo():
    """Vérifie les horaires et active le servo si nécessaire"""
    global last_activation
    
    try:
        if not os.path.exists(SCHEDULE_FILE):
            return
        
        with open(SCHEDULE_FILE, 'r') as f:
            schedule_data = json.load(f)
        
        current_time = datetime.now()
        current_time_str = current_time.strftime("%H:%M")
        current_date = current_time.strftime("%Y-%m-%d")
        
        # Vérifier midi
        if schedule_data.get("midi", {}).get("enabled", False):
            midi_time = schedule_data["midi"]["time"]
            if current_time_str == midi_time:
                # Éviter les activations multiples le même jour
                if last_activation["midi"] != current_date:
                    print(f"🌅 MIDI - Activation du servo à {midi_time}")
                    if activate_servo():
                        last_activation["midi"] = current_date
                        print(f"✅ Servo activé automatiquement (MIDI) à {midi_time}")
        
        # Vérifier soir
        if schedule_data.get("soir", {}).get("enabled", False):
            soir_time = schedule_data["soir"]["time"]
            if current_time_str == soir_time:
                # Éviter les activations multiples le même jour
                if last_activation["soir"] != current_date:
                    print(f"🌙 SOIR - Activation du servo à {soir_time}")
                    if activate_servo():
                        last_activation["soir"] = current_date
                        print(f"✅ Servo activé automatiquement (SOIR) à {soir_time}")
                
    except Exception as e:
        print(f"❌ Erreur vérification horaires: {e}")

def run_scheduler():
    """Lance le scheduler en arrière-plan"""
    global scheduler_running
    
    scheduler_running = True
    print("📅 Scheduler démarré - vérification toutes les minutes")
    
    while scheduler_running:
        try:
            check_and_activate_servo()
        except Exception as e:
            print(f"❌ Erreur dans le scheduler: {e}")
        
        # Attendre 30 secondes avant la prochaine vérification
        for _ in range(30):
            if not scheduler_running:
                break
            time.sleep(1)
    
    print("📅 Scheduler arrêté")

def start_scheduler():
    """Démarre le scheduler dans un thread séparé"""
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

# ============================================
# ROUTES PRINCIPALES
# ============================================

@app.route('/')
def home():
    """Page d'accueil"""
    return jsonify({
        "message": "Brice Controller API",
        "version": "1.0.0",
        "scheduler": "active" if scheduler_running else "inactive",
        "endpoints": {
            "test": "/test",
            "servo": "/api/servo/press",
            "schedule": "/api/schedule",
            "scheduler": "/api/scheduler/status",
            "ice_maker": "/api/ice_maker/status"
        }
    })

@app.route('/test')
def test():
    """Test de connectivité"""
    log_request()
    print("✅ Test de connectivité réussi")
    
    return jsonify({
        "status": "success", 
        "message": "Brice is ready!",
        "timestamp": datetime.now().isoformat(),
        "scheduler": "active" if scheduler_running else "inactive",
        "version": "1.0.0"
    })

@app.route('/api/servo/press', methods=['POST'])
def servo_press():
    """Action du servo - appui sur le bouton"""
    log_request()
    
    try:
        # Gérer le cas où il n'y a pas de JSON (curl simple)
        data = {}
        if request.is_json:
            data = request.get_json() or {}
        
        action = data.get('action', 'manual_press')
        
        print(f"🔧 Activation manuelle du servo - Action: {action}")
        
        # Activer le servo
        servo_success = activate_servo()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if servo_success:
            print(f"✅ Servo activé avec succès à {timestamp}")
            response = {
                "status": "success", 
                "message": "Briced",
                "action": action,
                "timestamp": timestamp,
                "servo_activated": True
            }
        else:
            print(f"❌ Échec activation servo à {timestamp}")
            response = {
                "status": "error", 
                "message": "Servo activation failed",
                "action": action,
                "timestamp": timestamp,
                "servo_activated": False
            }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Erreur servo: {e}")
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    """Récupère les horaires"""
    log_request()
    
    try:
        if os.path.exists(SCHEDULE_FILE):
            with open(SCHEDULE_FILE, 'r') as f:
                schedule = json.load(f)
            print(f"📅 Horaires chargés depuis {SCHEDULE_FILE}")
        else:
            # Horaires par défaut
            schedule = {
                "midi": {"time": "12:00", "enabled": True},
                "soir": {"time": "19:00", "enabled": True}
            }
            print("📅 Horaires par défaut utilisés")
        
        return jsonify({
            "status": "success", 
            "schedule": schedule
        })
        
    except Exception as e:
        print(f"❌ Erreur lecture horaires: {e}")
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/api/schedule', methods=['POST'])
def save_schedule():
    """Sauvegarde les horaires"""
    log_request()
    
    try:
        # Accepter du JSON ou du form data
        data = None
        
        if request.is_json:
            data = request.get_json()
        elif request.content_type == 'application/x-www-form-urlencoded':
            # Convertir form data en dict
            data = request.form.to_dict()
        
        if not data:
            return jsonify({
                "status": "error", 
                "message": "Aucune donnée reçue"
            }), 400
        
        # Sauvegarder dans le fichier JSON
        with open(SCHEDULE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Horaires sauvegardés: {data}")
        
        return jsonify({
            "status": "success", 
            "message": "Schedule saved successfully"
        })
        
    except Exception as e:
        print(f"❌ Erreur sauvegarde horaires: {e}")
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/api/scheduler/status')
def scheduler_status():
    """Statut du scheduler"""
    log_request()
    
    try:
        current_time = datetime.now().strftime("%H:%M")
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        schedule_info = {}
        if os.path.exists(SCHEDULE_FILE):
            with open(SCHEDULE_FILE, 'r') as f:
                schedule_info = json.load(f)
        
        return jsonify({
            "status": "success",
            "scheduler_running": scheduler_running,
            "current_time": current_time,
            "current_date": current_date,
            "schedule": schedule_info,
            "last_activation": last_activation,
            "message": "Scheduler actif" if scheduler_running else "Scheduler arrêté"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/api/ice_maker/status')
def ice_maker_status():
    """Statut du générateur de glaçons (pour compatibilité avec l'app Xamarin)"""
    log_request()
    
    # Pour l'instant, retourner un statut par défaut
    return jsonify({
        "status": "success",
        "ice_maker_led": "UNKNOWN",
        "message": "Capteur LED non configuré"
    })

@app.route('/api/status')
def api_status():
    """Statut général de l'API"""
    log_request()
    
    return jsonify({
        "status": "success",
        "message": "Brice API is running",
        "timestamp": datetime.now().isoformat(),
        "scheduler_running": scheduler_running,
        "servo_available": True,
        "endpoints": {
            "home": "/",
            "test": "/test",
            "servo": "/api/servo/press (POST)",
            "schedule_get": "/api/schedule (GET)",
            "schedule_post": "/api/schedule (POST)",
            "scheduler": "/api/scheduler/status (GET)",
            "ice_maker": "/api/ice_maker/status (GET)",
            "status": "/api/status (GET)"
        }
    })

# ============================================
# ROUTES DE DEBUG
# ============================================

@app.route('/debug/info')
def debug_info():
    """Informations de debug"""
    log_request()
    
    import socket
    hostname = socket.gethostname()
    
    return jsonify({
        "hostname": hostname,
        "working_directory": os.getcwd(),
        "schedule_file_exists": os.path.exists(SCHEDULE_FILE),
        "scheduler_running": scheduler_running,
        "last_activation": last_activation,
        "request_info": {
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get('User-Agent'),
            "method": request.method
        }
    })

# ============================================
# GESTION DES ERREURS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Endpoint not found",
        "available_endpoints": [
            "GET /",
            "GET /test",
            "POST /api/servo/press",
            "GET /api/schedule",
            "POST /api/schedule",
            "GET /api/scheduler/status",
            "GET /api/ice_maker/status",
            "GET /api/status",
            "GET /debug/info"
        ]
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "status": "error",
        "message": f"Method {request.method} not allowed for this endpoint"
    }), 405

@app.errorhandler(500)
def internal_error(error):
    print(f"❌ Erreur 500: {error}")
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500

# ============================================
# DÉMARRAGE DU SERVEUR
# ============================================

if __name__ == '__main__':
    print("=" * 60)
    print("Démarrage de Brice")
    print("=" * 60)
    
    # Vérifier que servo.py est accessible
    try:
        activate_servo
        print("✅ Module servo.py chargé avec succès")
    except NameError:
        print("⚠️ Attention: servo.py non trouvé, mode simulation activé")
    
    # Vérifier le dossier de travail
    print(f"📁 Dossier de travail: {os.getcwd()}")
    
    # Vérifier les fichiers
    if os.path.exists('servo.py'):
        print("✅ servo.py trouvé")
    else:
        print("⚠️ servo.py non trouvé")
    
    if os.path.exists(SCHEDULE_FILE):
        print(f"✅ {SCHEDULE_FILE} trouvé")
        try:
            with open(SCHEDULE_FILE, 'r') as f:
                schedule = json.load(f)
            print(f"📅 Horaires actuels: {schedule}")
        except:
            print("⚠️ Erreur lecture schedule.json")
    else:
        print(f"⚠️ {SCHEDULE_FILE} non trouvé")
    
    # Démarrer le scheduler
    print("📅 Démarrage du scheduler automatique...")
    start_scheduler()
    
    print("🌐 Serveur accessible sur:")
    print("   - Local: http://localhost:5000")
    print("   - Réseau: http://0.0.0.0:5000")
    print("   - IP LAN: http://YOUR_RPI_IP:5000")
    print("   - Tailscale: http://YOUR_RPI_TAILSCALE_IP:5000")
    print()
    print("📋 Endpoints disponibles:")
    print("   - GET  /                        (accueil)")
    print("   - GET  /test                    (test de connectivité)")
    print("   - POST /api/servo/press         (actionner le servo)")
    print("   - GET  /api/schedule            (récupérer horaires)")
    print("   - POST /api/schedule            (sauvegarder horaires)")
    print("   - GET  /api/scheduler/status    (statut scheduler)")
    print("   - GET  /api/ice_maker/status    (statut générateur)")
    print("   - GET  /api/status              (statut de l'API)")
    print("   - GET  /debug/info              (informations debug)")
    print()
    print("🔧 Pour arrêter: Ctrl+C")
    print("📊 Pour voir les logs: sudo journalctl -u brice-de-glace -f")
    print("📅 Scheduler automatique: ACTIF")
    print("=" * 60)
    
    # Lancer le serveur Flask
    try:
        app.run(
            host='0.0.0.0',  # Écouter sur toutes les interfaces
            port=5000, 
            debug=False,     # Mettre True pour plus de logs en développement
            threaded=True
        )
    except Exception as e:
        print(f"❌ Impossible de démarrer le serveur: {e}")
        print("💡 Vérifiez que le port 5000 n'est pas déjà utilisé")
    finally:
        scheduler_running = False