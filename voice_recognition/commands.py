# Словарь поддерживаемых команд (английский)
VOICE_COMMANDS_EN = {
    # Взлёт / посадка
    "takeoff": "TAKEOFF",
    "take off": "TAKEOFF",
    "launch": "TAKEOFF",
    "land": "LAND",
    "landing": "LAND",

    # Остановка
    "stop": "STOP",
    "halt": "STOP",
    "hover": "STOP",
    "freeze": "STOP",

    # Направления
    "forward": "FORWARD",
    "go forward": "FORWARD",
    "move forward": "FORWARD",

    "backward": "BACKWARD",
    "go back": "BACKWARD",
    "move back": "BACKWARD",

    "left": "LEFT",
    "go left": "LEFT",
    "move left": "LEFT",

    "right": "RIGHT",
    "go right": "RIGHT",
    "move right": "RIGHT",

    # Высота
    "up": "UP",
    "go up": "UP",
    "ascend": "UP",
    "climb": "UP",

    "down": "DOWN",
    "go down": "DOWN",
    "descend": "DOWN",

    # Экстренная остановка
    "emergency": "EMERGENCY_STOP",
    "abort": "EMERGENCY_STOP",
    "emergency stop": "EMERGENCY_STOP",

    # Разворот
    "turn left": "YAW_LEFT",
    "rotate left": "YAW_LEFT",
    "turn right": "YAW_RIGHT",
    "rotate right": "YAW_RIGHT",

    # Возврат
    "return": "RTL",
    "return home": "RTL",
    "come back": "RTL",
}

# Русский вариант
VOICE_COMMANDS_RU = {
    "взлёт": "TAKEOFF",
    "взлет": "TAKEOFF",
    "старт": "TAKEOFF",
    "посадка": "LAND",
    "садись": "LAND",
    "стоп": "STOP",
    "зависни": "STOP",
    "вперёд": "FORWARD",
    "вперед": "FORWARD",
    "назад": "BACKWARD",
    "влево": "LEFT",
    "налево": "LEFT",
    "вправо": "RIGHT",
    "направо": "RIGHT",
    "вверх": "UP",
    "выше": "UP",
    "вниз": "DOWN",
    "ниже": "DOWN",
    "домой": "RTL",
    "возврат": "RTL",
    "аварийная остановка": "EMERGENCY_STOP",
}

def get_command(recognized_text, language="en"):
    """
    Преобразует распознанный текст в команду.
    
    Args:
        recognized_text: строка с распознанной речью
        language: "en" или "ru"
    
    Returns:
        строка команды или None
    """
    text = recognized_text.lower().strip()
    commands = VOICE_COMMANDS_EN if language == "en" else VOICE_COMMANDS_RU

    # Точное совпадение
    if text in commands:
        return commands[text]

    # Поиск по частичному совпадению
    for phrase, command in commands.items():
        if phrase in text:
            return command

    return None