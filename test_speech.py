import speech_recognition as sr

recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Калибровка
print("Калибровка микрофона...")
with microphone as source:
    recognizer.adjust_for_ambient_noise(source, duration=2)
    print("Говорите команду:")
    audio = recognizer.listen(source)

# Распознавание
try:
    text = recognizer.recognize_google(audio, language="en-US")
    print(f"Вы сказали: {text}")
except sr.UnknownValueError:
    print("Не удалось распознать")
except sr.RequestError:
    print("Ошибка сети")