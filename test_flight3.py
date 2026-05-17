from dronekit import connect, VehicleMode
from pymavlink import mavutil
import time

print("Подключаемся...")
vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True)
print(f"Подключено! Режим: {vehicle.mode.name}")

# --- Функция принудительного переключения режима ---
def set_mode(vehicle, mode_name):
    """Переключение режима через MAVLink напрямую"""
    mode_id = vehicle._master.mode_mapping()[mode_name]
    vehicle._master.mav.set_mode_send(
        vehicle._master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id
    )
    # Ждём переключения
    timeout = 10
    start = time.time()
    while vehicle.mode.name != mode_name:
        if time.time() - start > timeout:
            print(f"❌ Не удалось переключить в {mode_name}")
            return False
        time.sleep(0.2)
    return True

# --- Переключаем в GUIDED ---
print("\nПереключаем в GUIDED...")
success = set_mode(vehicle, "GUIDED")

if success:
    print(f"✅ Режим: {vehicle.mode.name}")
else:
    print("Пробуем другой способ...")
    vehicle.mode = VehicleMode("GUIDED")
    time.sleep(3)
    print(f"Режим сейчас: {vehicle.mode.name}")

# --- Армируем ---
print("Армируем моторы...")
vehicle.armed = True

start = time.time()
while not vehicle.armed:
    if time.time() - start > 15:
        print("❌ Не удалось армировать")
        break
    print(f"  Ждём... режим={vehicle.mode.name}")
    time.sleep(0.5)

if vehicle.armed:
    print("✅ Армировано!")

    # СРАЗУ взлёт
    print("🚀 Взлёт!")
    vehicle.simple_takeoff(5)

    # Ждём высоту
    start = time.time()
    while True:
        alt = vehicle.location.global_relative_frame.alt
        print(f"  Высота: {alt:.1f} м | Режим: {vehicle.mode.name}")

        if alt >= 4.8:
            print("✅ Высота 5м достигнута!")
            break

        if not vehicle.armed:
            print("❌ Дрон разоружился")
            break

        if time.time() - start > 30:
            print("❌ Таймаут")
            break

        time.sleep(0.5)

# Посадка если в воздухе
if vehicle.armed:
    print("🛬 Посадка...")
    set_mode(vehicle, "LAND")
    while vehicle.armed:
        alt = vehicle.location.global_relative_frame.alt
        print(f"  Высота: {alt:.1f} м")
        time.sleep(1)
    print("✅ Сели!")

vehicle.close()
print("Готово!")
