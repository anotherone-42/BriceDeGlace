#!/usr/bin/env python3
"""
Module de contrôle du servo SG90
Contient les fonctions pour actionner le servo moteur
"""

import RPi.GPIO as GPIO
import time

# Configuration
SERVO_PIN = 18  # GPIO 18 (Pin 12 physique)

def activate_servo():
    """
    Active le servo moteur SG90 pour simuler un appui sur bouton
    Séquence simple: 90° (repos) -> 0° (appui) -> 90° (repos)
    
    Returns:
        bool: True si succès, False sinon
    """
    try:
        print("🔧 Activation du servo SG90...")
        
        # Configuration GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SERVO_PIN, GPIO.OUT)
        
        # Créer un signal PWM à 50Hz
        pwm = GPIO.PWM(SERVO_PIN, 50)
        pwm.start(0)
        
        # Position de repos -> Appui -> Retour repos
        pwm.ChangeDutyCycle(7.5)  # 90° repos
        time.sleep(0.3)
        pwm.ChangeDutyCycle(2.5)  # 0° appui
        time.sleep(0.5)           # Temps d'appui
        pwm.ChangeDutyCycle(7.5)  # 90° retour repos
        time.sleep(0.3)
        
        # Arrêt et nettoyage
        pwm.stop()
        GPIO.cleanup()
        
        print("✅ Appui effectué")
        return True
        
    except Exception as e:
        print(f"❌ Erreur servo: {e}")
        try:
            GPIO.cleanup()
        except:
            pass
        return False

if __name__ == "__main__":
    print("Test du servo")
    activate_servo()
