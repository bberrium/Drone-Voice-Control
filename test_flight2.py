from dronekit import connect, VehicleMode
import time

print("Подключаемся...")
vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True)

print(f"Текущий режим: {vehicle.mode.name}")

# --- ВАЖНО: сначала режим GUIDED, потом армирование ---
print("\nПереключаем режим GUIDED...")
vehicle.mode = VehicleMode("GUIDED")

# Ждём пока режим точно переключился
while vehicle.mode.name != "GUIDED":
    print(f"  Ждём GUIDED... текущий: {vehicle.mode.name}")
    time.sleep(0.5)
print("✅ Режим GUIDED активен!")

# Армируем
print("Армируем моторы...")
vehicle.armed = True

while not vehicle.armed:
    print("  Ждём армирования...")
    time.sleep(0.5)
print("✅ Моторы армированы!")

# СРАЗУ взлёт — без задержки!
print("🚀 Взлёт до 5 метров!")
vehicle.simple_takeoff(5)

# Ждём набора высоты
timeout = 30  # максимум 30 секунд
start = time.time()

while True:
    alt = vehicle.location.global_relative_frame.alt
    mode = vehicle.mode.name
    armed = vehicle.armed
    print(f"  Высота: {alt:.1f} м | Режим: {mode} | Армирован: {armed}")
    
    if alt >= 4.8:
        print("✅ Высота достигнута!")
        break
    
    if time.time() - start > timeout:
        print("❌ Таймаут взлёта!")
        break
        
    if not armed:
        print("❌ Дрон разоружился! Пробуем снова...")
        break
        
    time.sleep(0.5)

# --- ВИСИМ 3 СЕКУНДЫ ---
if vehicle.armed:
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
print("Готово!")
