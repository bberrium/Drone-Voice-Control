from dronekit import connect, VehicleMode
import time

print("Подключаемся к симулятору...")
vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True)

print(f"✅ Подключено!")
print(f"Версия: {vehicle.version}")
print(f"Батарея: {vehicle.battery}")
print(f"GPS: {vehicle.gps_0}")
print(f"Режим: {vehicle.mode.name}")
print(f"Армирован: {vehicle.armed}")

vehicle.close()
print("Тест пройден!")
