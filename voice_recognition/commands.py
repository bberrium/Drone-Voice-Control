# Dictionary of supported commands (English)
VOICE_COMMANDS_EN = {
    # Takeoff / landing
    "takeoff": "TAKEOFF",
    "take off": "TAKEOFF",
    "launch": "TAKEOFF",
    "land": "LAND",
    "landing": "LAND",

    # Stop
    "stop": "STOP",
    "halt": "STOP",
    "hover": "STOP",
    "freeze": "STOP",

    # Directions
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

    # Altitude
    "up": "UP",
    "go up": "UP",
    "ascend": "UP",
    "climb": "UP",

    "down": "DOWN",
    "go down": "DOWN",
    "descend": "DOWN",

    # Emergency stop
    "emergency": "EMERGENCY_STOP",
    "abort": "EMERGENCY_STOP",
    "emergency stop": "EMERGENCY_STOP",

    # Yaw / Turn
    "turn left": "YAW_LEFT",
    "rotate left": "YAW_LEFT",
    "turn right": "YAW_RIGHT",
    "rotate right": "YAW_RIGHT",

    # Return
    "return": "RTL",
    "return home": "RTL",
    "come back": "RTL",
}

# Russian variant (commands kept in original language for recognition)
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
    Converts recognized text into a command.
    
    Args:
        recognized_text: string with recognized speech
        language: "en" or "ru"
    
    Returns:
        command string or None
    """
    text = recognized_text.lower().strip()
    commands = VOICE_COMMANDS_EN if language == "en" else VOICE_COMMANDS_RU

    # Exact match
    if text in commands:
        return commands[text]

    # Partial match search
    for phrase, command in commands.items():
        if phrase in text:
            return command

    return None