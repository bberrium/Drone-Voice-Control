# test_sitl.py — запускаем и проверяем
import dronekit_sitl
from dronekit import connect

# Запуск симулятора
sitl = dronekit_sitl.start_default()
connection_string = sitl.connection_string()
print(f"Подключаемся к: {connection_string}")

# Подключение
vehicle = connect(connection_string, wait_ready=True)
print(f"Версия: {vehicle.version}")
print(f"Батарея: {vehicle.battery}")

vehicle.close()
sitl.stop()
print("Тест пройден!")

