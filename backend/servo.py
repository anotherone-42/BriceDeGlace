#!/usr/bin/env python3
"""
SG90 servo control module
Contains functions to operate the servo motor
"""

import RPi.GPIO as GPIO
import time

# Configuration
SERVO_PIN = 18  # GPIO 18 (physical pin 12)

def activate_servo():
    """
    Activates the SG90 servo motor to simulate a button press
    Simple sequence: 90° (rest) -> 0° (press) -> 90° (rest)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print("🔧 Activating SG90 servo...")

        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SERVO_PIN, GPIO.OUT)

        # Create a 50Hz PWM signal
        pwm = GPIO.PWM(SERVO_PIN, 50)
        pwm.start(0)

        # Rest position -> Press -> Return to rest
        pwm.ChangeDutyCycle(7.5)  # 90° rest position
        time.sleep(0.3)
        pwm.ChangeDutyCycle(2.5)  # 0° press
        time.sleep(0.5)           # Press duration
        pwm.ChangeDutyCycle(7.5)  # 90° return to rest
        time.sleep(0.3)

        # Stop and cleanup
        pwm.stop()
        GPIO.cleanup()

        print("✅ Button press completed")
        return True

    except Exception as e:
        print(f"❌ Servo error: {e}")
        try:
            GPIO.cleanup()
        except:
            pass
        return False

if __name__ == "__main__":
    print("Servo test")
    activate_servo()
