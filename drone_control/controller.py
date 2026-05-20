import time
import logging
from dronekit import connect, VehicleMode
from pymavlink import mavutil

logger = logging.getLogger(__name__)


class DroneController:

    def __init__(self, connection_string, baud=57600):
        self.connection_string = connection_string
        self.baud = baud
        self.vehicle = None
        self.default_altitude = 5
        self.velocity = 0.5

    def connect(self):
        logger.info(f"Connecting to: {self.connection_string}")
        try:
            self.vehicle = connect(
                self.connection_string,
                baud=self.baud,
                wait_ready=True,
                timeout=60
            )
            logger.info(" Connection established!")
            return True
        except Exception as e:
            logger.error(f" Connection error: {e}")
            return False

    def _set_mode(self, mode_name):
        """Switching mode via MAVLink directly."""
        try:
            mode_id = self.vehicle._master.mode_mapping()[mode_name]
            self.vehicle._master.mav.set_mode_send(
                self.vehicle._master.target_system,
                mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                mode_id
            )
            # Wait for switching maximum 5 seconds
            start = time.time()
            while self.vehicle.mode.name != mode_name:
                if time.time() - start > 5:
                    logger.warning(f"Timeout switching to {mode_name}")
                    return False
                time.sleep(0.1)
            return True
        except Exception as e:
            logger.error(f"Error switching mode: {e}")
            return False

    def arm_and_takeoff(self, target_altitude=None):
        if target_altitude is None:
            target_altitude = self.default_altitude

        logger.info("Checking pre-flight conditions...")

        # Wait for readiness
        start = time.time()
        while not self.vehicle.is_armable:
            if time.time() - start > 30:
                logger.error("Drone is not ready to arm!")
                return
            logger.info("Waiting for drone readiness...")
            time.sleep(1)

        # Switch to GUIDED via MAVLink directly
        logger.info("Switching to GUIDED mode...")
        self._set_mode("GUIDED")
        logger.info(f"Mode: {self.vehicle.mode.name}")

        # Arming
        logger.info("Arming motors...")
        self.vehicle.armed = True

        start = time.time()
        while not self.vehicle.armed:
            if time.time() - start > 15:
                logger.error("Failed to arm!")
                return
            logger.info("Waiting for arming...")
            time.sleep(0.3)

        logger.info(" Armed!")

        # IMMEDIATE takeoff - no delay!
        logger.info(f" Takeoff to {target_altitude} m...")
        self.vehicle.simple_takeoff(target_altitude)

        # Wait for altitude
        start = time.time()
        while True:
            alt = self.vehicle.location.global_relative_frame.alt
            logger.info(f"Altitude: {alt:.1f} m")

            if alt >= target_altitude * 0.95:
                logger.info(" Target altitude reached!")
                break

            if not self.vehicle.armed:
                logger.error(" Drone disarmed during takeoff!")
                # Try again
                logger.info("Retrying takeoff...")
                time.sleep(1)
                self._set_mode("GUIDED")
                time.sleep(0.5)
                self.vehicle.armed = True
                time.sleep(0.5)
                self.vehicle.simple_takeoff(target_altitude)

            if time.time() - start > 30:
                logger.error("Takeoff timeout!")
                break

            time.sleep(0.5)

    def send_velocity(self, vx, vy, vz, duration=1):
        """Sending velocity command."""
        msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
            0, 0, 0,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            0b0000111111000111,
            0, 0, 0,
            vx, vy, vz,
            0, 0, 0,
            0, 0
        )
        start_time = time.time()
        while time.time() - start_time < duration:
            self.vehicle.send_mavlink(msg)
            time.sleep(0.1)

    def move_forward(self, duration=2):
        logger.info(" Moving forward")
        self.send_velocity(self.velocity, 0, 0, duration)

    def move_backward(self, duration=2):
        logger.info(" Moving backward")
        self.send_velocity(-self.velocity, 0, 0, duration)

    def move_left(self, duration=2):
        logger.info(" Moving left")
        self.send_velocity(0, -self.velocity, 0, duration)

    def move_right(self, duration=2):
        logger.info(" Moving right")
        self.send_velocity(0, self.velocity, 0, duration)

    def move_up(self, duration=2):
        logger.info(" Moving up")
        self.send_velocity(0, 0, -self.velocity, duration)

    def move_down(self, duration=2):
        logger.info(" Moving down")
        self.send_velocity(0, 0, self.velocity, duration)

    def stop(self):
        logger.info(" Stopping")
        self.send_velocity(0, 0, 0, 1)

    def yaw_left(self, degrees=45):
        logger.info(f" Yaw left by {degrees}°")
        self._condition_yaw(-degrees)

    def yaw_right(self, degrees=45):
        logger.info(f" Yaw right by {degrees}°")
        self._condition_yaw(degrees)

    def _condition_yaw(self, heading, relative=True):
        is_relative = 1 if relative else 0
        direction = 1 if heading >= 0 else -1
        msg = self.vehicle.message_factory.command_long_encode(
            0, 0,
            mavutil.mavlink.MAV_CMD_CONDITION_YAW,
            0,
            abs(heading), 10, direction, is_relative,
            0, 0, 0
        )
        self.vehicle.send_mavlink(msg)
        time.sleep(abs(heading) / 10)

    def land(self):
        logger.info(" Landing...")
        self._set_mode("LAND")
        while self.vehicle.armed:
            alt = self.vehicle.location.global_relative_frame.alt
            logger.info(f"Altitude during landing: {alt:.1f} m")
            time.sleep(1)
        logger.info(" Landing completed!")

    def return_to_launch(self):
        logger.info(" Return to launch (RTL)...")
        self._set_mode("RTL")

    def emergency_stop(self):
        logger.warning(" EMERGENCY STOP!")
        self.vehicle.armed = False

    def disconnect(self):
        if self.vehicle:
            self.vehicle.close()
            logger.info("Connection closed")