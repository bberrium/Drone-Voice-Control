#!/usr/bin/env python3
"""
Drone Control with Voice — main module.
Implementation based on IEEE 7993759 article.
"""

import time
import logging
import signal
import sys

from config import CONNECTION_STRING, BAUD_RATE, LANGUAGE, DEFAULT_ALTITUDE
from voice_recognition.recognizer import VoiceRecognizer
from voice_recognition.commands import get_command
from drone_control.controller import DroneController

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('drone_voice.log')
    ]
)
logger = logging.getLogger(__name__)


class VoiceDroneSystem:
    """
    Main voice drone control system.
    """

    def __init__(self):
        self.drone = DroneController(CONNECTION_STRING, BAUD_RATE)
        self.recognizer = VoiceRecognizer(language=LANGUAGE)
        self.is_running = False
        self.is_flying = False

        # Mapping commands to functions
        self.command_handlers = {
            "TAKEOFF":        self._handle_takeoff,
            "LAND":           self._handle_land,
            "STOP":           self._handle_stop,
            "FORWARD":        self._handle_forward,
            "BACKWARD":       self._handle_backward,
            "LEFT":           self._handle_left,
            "RIGHT":          self._handle_right,
            "UP":             self._handle_up,
            "DOWN":           self._handle_down,
            "YAW_LEFT":       self._handle_yaw_left,
            "YAW_RIGHT":      self._handle_yaw_right,
            "RTL":            self._handle_rtl,
            "EMERGENCY_STOP": self._handle_emergency,
        }

    # ─── Command Handlers ───────────────────────────────────────

    def _handle_takeoff(self):
        if not self.is_flying:
            self.drone.arm_and_takeoff(DEFAULT_ALTITUDE)
            self.is_flying = True
        else:
            logger.warning("Drone is already in the air!")

    def _handle_land(self):
        if self.is_flying:
            self.drone.land()
            self.is_flying = False
        else:
            logger.warning("Drone is already on the ground!")

    def _handle_stop(self):
        if self.is_flying:
            self.drone.stop()

    def _handle_forward(self):
        if self.is_flying:
            self.drone.move_forward()

    def _handle_backward(self):
        if self.is_flying:
            self.drone.move_backward()

    def _handle_left(self):
        if self.is_flying:
            self.drone.move_left()

    def _handle_right(self):
        if self.is_flying:
            self.drone.move_right()

    def _handle_up(self):
        if self.is_flying:
            self.drone.move_up()

    def _handle_down(self):
        if self.is_flying:
            self.drone.move_down()

    def _handle_yaw_left(self):
        if self.is_flying:
            self.drone.yaw_left()

    def _handle_yaw_right(self):
        if self.is_flying:
            self.drone.yaw_right()

    def _handle_rtl(self):
        if self.is_flying:
            self.drone.return_to_launch()
            self.is_flying = False

    def _handle_emergency(self):
        self.drone.emergency_stop()
        self.is_flying = False

    # ─── Main Loop ──────────────────────────────────────────────

    def process_voice_command(self, recognized_text):
        """Processing recognized text."""
        logger.info(f"Processing: '{recognized_text}'")

        # Determine language based on settings
        lang = "ru" if "RU" in LANGUAGE.upper() else "en"
        command = get_command(recognized_text, language=lang)

        if command:
            logger.info(f" Command: {command}")
            handler = self.command_handlers.get(command)
            if handler:
                try:
                    handler()
                except Exception as e:
                    logger.error(f"Error executing command {command}: {e}")
        else:
            logger.info(f" Command not recognized: '{recognized_text}'")

    def run(self):
        """Main system execution loop."""
        logger.info("=" * 50)
        logger.info(" Voice drone control system")
        logger.info("=" * 50)

        # Connecting to drone
        if not self.drone.connect():
            logger.error("Failed to connect to drone. Exiting.")
            return

        # Start speech recognition
        self.recognizer.start()
        self.is_running = True

        logger.info(" System ready! Speak commands...")
        print("\nAvailable commands:")
        print("  takeoff/взлёт | land/посадка | stop/стоп")
        print("  forward/вперёд | backward/назад")
        print("  left/влево | right/вправо")
        print("  up/вверх | down/вниз")
        print("  return/домой | emergency/аварийная остановка")
        print("\nPress Ctrl+C to exit\n")

        try:
            while self.is_running:
                # Get recognized text
                recognized_text = self.recognizer.get_command(timeout=0.5)

                if recognized_text:
                    self.process_voice_command(recognized_text)

                time.sleep(0.05)

        except KeyboardInterrupt:
            logger.info("Interrupt signal received")
        finally:
            self.shutdown()

    def shutdown(self):
        """Safe shutdown."""
        logger.info("Shutting down system...")
        self.is_running = False

        # Safe landing if in the air
        if self.is_flying:
            logger.warning("Executing emergency landing...")
            self.drone.land()

        self.recognizer.stop()
        self.drone.disconnect()
        logger.info("System stopped")


def main():
    system = VoiceDroneSystem()

    # System signal handling
    def signal_handler(sig, frame):
        system.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    system.run()


if __name__ == "__main__":
    main()