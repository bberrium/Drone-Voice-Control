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
        logger.info(f"Подключение к: {self.connection_string}")
        try:
            self.vehicle = connect(
                self.connection_string,
                baud=self.baud,
                wait_ready=True,
                timeout=60
            )
            logger.info("✅ Подключение установлено!")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка подключения: {e}")
            return False

    def _set_mode(self, mode_name):
        """Переключение режима через MAVLink напрямую."""
        try:
            mode_id = self.vehicle._master.mode_mapping()[mode_name]
            self.vehicle._master.mav.set_mode_send(
                self.vehicle._master.target_system,
                mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
                mode_id
            )
            # Ждём переключения максимум 5 секунд
            start = time.time()
            while self.vehicle.mode.name != mode_name:
                if time.time() - start > 5:
                    logger.warning(f"Таймаут переключения в {mode_name}")
                    return False
                time.sleep(0.1)
            return True
        except Exception as e:
            logger.error(f"Ошибка переключения режима: {e}")
            return False

    def arm_and_takeoff(self, target_altitude=None):
        if target_altitude is None:
            target_altitude = self.default_altitude

        logger.info("Проверка предполётных условий...")

        # Ждём готовности
        start = time.time()
        while not self.vehicle.is_armable:
            if time.time() - start > 30:
                logger.error("Дрон не готов к армированию!")
                return
            logger.info("Ожидание готовности дрона...")
            time.sleep(1)

        # Переключаем в GUIDED через MAVLink напрямую
        logger.info("Переключение в режим GUIDED...")
        self._set_mode("GUIDED")
        logger.info(f"Режим: {self.vehicle.mode.name}")

        # Армируем
        logger.info("Армирование моторов...")
        self.vehicle.armed = True

        start = time.time()
        while not self.vehicle.armed:
            if time.time() - start > 15:
                logger.error("Не удалось армировать!")
                return
            logger.info("Ожидание армирования...")
            time.sleep(0.3)

        logger.info("✅ Армировано!")

        # НЕМЕДЛЕННО взлёт — без задержки!
        logger.info(f"🚀 Взлёт до {target_altitude} м...")
        self.vehicle.simple_takeoff(target_altitude)

        # Ждём высоту
        start = time.time()
        while True:
            alt = self.vehicle.location.global_relative_frame.alt
            logger.info(f"Высота: {alt:.1f} м")

            if alt >= target_altitude * 0.95:
                logger.info("✅ Целевая высота достигнута!")
                break

            if not self.vehicle.armed:
                logger.error("❌ Дрон разоружился во время взлёта!")
                # Пробуем ещё раз
                logger.info("Повторная попытка взлёта...")
                time.sleep(1)
                self._set_mode("GUIDED")
                time.sleep(0.5)
                self.vehicle.armed = True
                time.sleep(0.5)
                self.vehicle.simple_takeoff(target_altitude)

            if time.time() - start > 30:
                logger.error("Таймаут взлёта!")
                break

            time.sleep(0.5)

    def send_velocity(self, vx, vy, vz, duration=1):
        """Отправка команды скорости."""
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
        logger.info("➡️ Движение вперёд")
        self.send_velocity(self.velocity, 0, 0, duration)

    def move_backward(self, duration=2):
        logger.info("⬅️ Движение назад")
        self.send_velocity(-self.velocity, 0, 0, duration)

    def move_left(self, duration=2):
        logger.info("⬅️ Движение влево")
        self.send_velocity(0, -self.velocity, 0, duration)

    def move_right(self, duration=2):
        logger.info("➡️ Движение вправо")
        self.send_velocity(0, self.velocity, 0, duration)

    def move_up(self, duration=2):
        logger.info("⬆️ Подъём вверх")
        self.send_velocity(0, 0, -self.velocity, duration)

    def move_down(self, duration=2):
        logger.info("⬇️ Снижение вниз")
        self.send_velocity(0, 0, self.velocity, duration)

    def stop(self):
        logger.info("⏹️ Остановка")
        self.send_velocity(0, 0, 0, 1)

    def yaw_left(self, degrees=45):
        logger.info(f"↺ Разворот влево на {degrees}°")
        self._condition_yaw(-degrees)

    def yaw_right(self, degrees=45):
        logger.info(f"↻ Разворот вправо на {degrees}°")
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
        logger.info("🛬 Посадка...")
        self._set_mode("LAND")
        while self.vehicle.armed:
            alt = self.vehicle.location.global_relative_frame.alt
            logger.info(f"Высота при посадке: {alt:.1f} м")
            time.sleep(1)
        logger.info("✅ Посадка выполнена!")

    def return_to_launch(self):
        logger.info("🏠 Возврат домой (RTL)...")
        self._set_mode("RTL")

    def emergency_stop(self):
        logger.warning("🚨 АВАРИЙНАЯ ОСТАНОВКА!")
        self.vehicle.armed = False

    def disconnect(self):
        if self.vehicle:
            self.vehicle.close()
            logger.info("Соединение закрыто")
