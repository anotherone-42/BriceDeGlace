#!/usr/bin/env python3
"""
Brice Controller API Server
Flask server to control the servo and manage schedules
"""

from flask import Flask, request, jsonify
import json
import os
from datetime import datetime
import logging
import threading
import time

# Import servo functions from servo.py
try:
    from servo import activate_servo
except ImportError:
    print("❌ Error: Unable to import servo.py")
    print("💡 Make sure servo.py exists in the same directory")
    # Fallback function if servo.py doesn't exist
    def activate_servo():
        print("⚠️ Simulated servo function (servo.py not found)")
        return True

# Flask app configuration
app = Flask(__name__)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuration
SCHEDULE_FILE = 'schedule.json'

# Global variables for the scheduler
scheduler_running = False
last_activation = {"midi": None, "soir": None}

def log_request():
    """Log request details"""
    print(f"🌐 {request.method} {request.url} from {request.remote_addr}")
    if request.is_json and request.get_json():
        print(f"📊 Data: {request.get_json()}")

def check_and_activate_servo():
    """Check schedules and activate servo if needed"""
    global last_activation

    try:
        if not os.path.exists(SCHEDULE_FILE):
            return

        with open(SCHEDULE_FILE, 'r') as f:
            schedule_data = json.load(f)

        current_time = datetime.now()
        current_time_str = current_time.strftime("%H:%M")
        current_date = current_time.strftime("%Y-%m-%d")

        # Check morning schedule
        if schedule_data.get("midi", {}).get("enabled", False):
            midi_time = schedule_data["midi"]["time"]
            if current_time_str == midi_time:
                # Avoid multiple activations on the same day
                if last_activation["midi"] != current_date:
                    print(f"🌅 MORNING - Activating servo at {midi_time}")
                    if activate_servo():
                        last_activation["midi"] = current_date
                        print(f"✅ Servo activated automatically (MORNING) at {midi_time}")

        # Check evening schedule
        if schedule_data.get("soir", {}).get("enabled", False):
            soir_time = schedule_data["soir"]["time"]
            if current_time_str == soir_time:
                # Avoid multiple activations on the same day
                if last_activation["soir"] != current_date:
                    print(f"🌙 EVENING - Activating servo at {soir_time}")
                    if activate_servo():
                        last_activation["soir"] = current_date
                        print(f"✅ Servo activated automatically (EVENING) at {soir_time}")

    except Exception as e:
        print(f"❌ Error checking schedules: {e}")

def run_scheduler():
    """Run scheduler in background"""
    global scheduler_running

    scheduler_running = True
    print("📅 Scheduler started - checking every minute")

    while scheduler_running:
        try:
            check_and_activate_servo()
        except Exception as e:
            print(f"❌ Error in scheduler: {e}")

        # Wait 30 seconds before next check
        for _ in range(30):
            if not scheduler_running:
                break
            time.sleep(1)

    print("📅 Scheduler stopped")

def start_scheduler():
    """Start scheduler in separate thread"""
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

# ============================================
# MAIN ROUTES
# ============================================

@app.route('/')
def home():
    """Home page"""
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
    """Connectivity test"""
    log_request()
    print("✅ Connectivity test successful")

    return jsonify({
        "status": "success", 
        "message": "Brice is ready!",
        "timestamp": datetime.now().isoformat(),
        "scheduler": "active" if scheduler_running else "inactive",
        "version": "1.0.0"
    })

@app.route('/api/servo/press', methods=['POST'])
def servo_press():
    """Servo action - button press"""
    log_request()

    try:
        # Handle case when no JSON is provided (simple curl)
        data = {}
        if request.is_json:
            data = request.get_json() or {}

        action = data.get('action', 'manual_press')

        print(f"🔧 Manual servo activation - Action: {action}")

        # Activate servo
        servo_success = activate_servo()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if servo_success:
            print(f"✅ Servo activated successfully at {timestamp}")
            response = {
                "status": "success", 
                "message": "Briced",
                "action": action,
                "timestamp": timestamp,
                "servo_activated": True
            }
        else:
            print(f"❌ Servo activation failed at {timestamp}")
            response = {
                "status": "error", 
                "message": "Servo activation failed",
                "action": action,
                "timestamp": timestamp,
                "servo_activated": False
            }

        return jsonify(response)

    except Exception as e:
        print(f"❌ Servo error: {e}")
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    """Retrieve schedules"""
    log_request()

    try:
        if os.path.exists(SCHEDULE_FILE):
            with open(SCHEDULE_FILE, 'r') as f:
                schedule = json.load(f)
            print(f"📅 Schedules loaded from {SCHEDULE_FILE}")
        else:
            # Default schedules
            schedule = {
                "midi": {"time": "12:00", "enabled": True},
                "soir": {"time": "19:00", "enabled": True}
            }
            print("📅 Using default schedules")

        return jsonify({
            "status": "success", 
            "schedule": schedule
        })

    except Exception as e:
        print(f"❌ Error reading schedules: {e}")
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/api/schedule', methods=['POST'])
def save_schedule():
    """Save schedules"""
    log_request()

    try:
        # Accept JSON or form data
        data = None

        if request.is_json:
            data = request.get_json()
        elif request.content_type == 'application/x-www-form-urlencoded':
            # Convert form data to dict
            data = request.form.to_dict()

        if not data:
            return jsonify({
                "status": "error", 
                "message": "No data received"
            }), 400

        # Save to JSON file
        with open(SCHEDULE_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"💾 Schedules saved: {data}")

        return jsonify({
            "status": "success", 
            "message": "Schedule saved successfully"
        })

    except Exception as e:
        print(f"❌ Error saving schedules: {e}")
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/api/scheduler/status')
def scheduler_status():
    """Scheduler status"""
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
            "message": "Scheduler active" if scheduler_running else "Scheduler stopped"
        })

    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/api/ice_maker/status')
def ice_maker_status():
    """Ice maker status (for compatibility with Xamarin app)"""
    log_request()

    # For now, return default status
    return jsonify({
        "status": "success",
        "ice_maker_led": "UNKNOWN",
        "message": "LED sensor not configured"
    })

@app.route('/api/status')
def api_status():
    """General API status"""
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
# DEBUG ROUTES
# ============================================

@app.route('/debug/info')
def debug_info():
    """Debug information"""
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
# ERROR HANDLING
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
# SERVER STARTUP
# ============================================

if __name__ == '__main__':
    print("=" * 60)
    print("Starting Brice")
    print("=" * 60)

    # Check if servo.py is accessible
    try:
        activate_servo
        print("✅ servo.py module loaded successfully")
    except NameError:
        print("⚠️ Warning: servo.py not found, simulation mode activated")

    # Check working directory
    print(f"📁 Working directory: {os.getcwd()}")

    # Check files
    if os.path.exists('servo.py'):
        print("✅ servo.py found")
    else:
        print("⚠️ servo.py not found")

    if os.path.exists(SCHEDULE_FILE):
        print(f"✅ {SCHEDULE_FILE} found")
        try:
            with open(SCHEDULE_FILE, 'r') as f:
                schedule = json.load(f)
            print(f"📅 Current schedules: {schedule}")
        except:
            print("⚠️ Error reading schedule.json")
    else:
        print(f"⚠️ {SCHEDULE_FILE} not found")

    # Start scheduler
    print("📅 Starting automatic scheduler...")
    start_scheduler()

    print("🌐 Server accessible at:")
    print("   - Local: http://localhost:5000")
    print("   - Network: http://0.0.0.0:5000")
    print("   - LAN IP: http://YOUR_RPI_IP:5000")
    print("   - Tailscale: http://YOUR_RPI_TAILSCALE_IP:5000")
    print()
    print("📋 Available endpoints:")
    print("   - GET  /                        (home)")
    print("   - GET  /test                    (connectivity test)")
    print("   - POST /api/servo/press         (activate servo)")
    print("   - GET  /api/schedule            (retrieve schedules)")
    print("   - POST /api/schedule            (save schedules)")
    print("   - GET  /api/scheduler/status    (scheduler status)")
    print("   - GET  /api/ice_maker/status    (ice maker status)")
    print("   - GET  /api/status              (API status)")
    print("   - GET  /debug/info              (debug information)")
    print()
    print("🔧 To stop: Ctrl+C")
    print("📊 To view logs: sudo journalctl -u brice-de-glace -f")
    print("📅 Automatic scheduler: ACTIVE")
    print("=" * 60)

    # Start Flask server
    try:
        app.run(
            host='0.0.0.0',  # Listen on all interfaces
            port=5000, 
            debug=False,     # Set True for more logs in development
            threaded=True
        )
    except Exception as e:
        print(f"❌ Unable to start server: {e}")
        print("💡 Check if port 5000 is already in use")
    finally:
        scheduler_running = False
