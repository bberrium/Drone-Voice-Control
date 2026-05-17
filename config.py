# Настройки подключения
# Для симулятора SITL:
CONNECTION_STRING = "tcp:127.0.0.1:5760"

# Для реального дрона через USB:
# CONNECTION_STRING = "/dev/ttyUSB0"  # Linux
# CONNECTION_STRING = "COM3"           # Windows

# Для подключения через телеметрию (3DR Radio):
# CONNECTION_STRING = "/dev/ttyUSB0,57600"

BAUD_RATE = 57600

# Параметры полёта
DEFAULT_ALTITUDE = 5   # метры
VELOCITY = 0.5         # м/с для перемещения

# Язык распознавания
LANGUAGE = "en-US"     # или "ru-RU" для русского