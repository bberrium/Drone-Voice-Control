from dronekit import connect, VehicleMode
import time

print("Подключаемся...")
vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True)

# --- ВЗЛЁТ ---
print("\nПереключаем режим GUIDED...")
vehicle.mode = VehicleMode("GUIDED")

print("Армируем моторы...")
vehicle.armed = True

while not vehicle.armed:
    print("  Ждём армирования...")
    time.sleep(1)

print("🚀 Взлёт до 5 метров!")
vehicle.simple_takeoff(5)

# Ждём набора высоты
while True:
    alt = vehicle.location.global_relative_frame.alt
    print(f"  Высота: {alt:.1f} м")
    if alt >= 4.8:
        print("✅ Высота достигнута!")
        break
    time.sleep(0.5)

# --- ВИСИМ 3 СЕКУНДЫ ---
print("Зависаем на 3 секунды...")
time.sleep(3)

# --- ПОСАДКА ---
print("🛬 Посадка...")
vehicle.mode = VehicleMode("LAND")

while vehicle.armed:
    alt = vehicle.location.global_relative_frame.alt
    print(f"  Высота при посадке: {alt:.1f} м")
    time.sleep(1)

print("✅ Посадка выполнена!")
vehicle.close()
