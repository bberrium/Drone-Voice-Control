import speech_recognition as sr
import threading
import queue
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceRecognizer:
    """
    Класс для непрерывного распознавания голосовых команд.
    Поддерживает Google Speech API и Vosk (offline).
    """

    def __init__(self, language="en-US", use_offline=False):
        self.language = language
        self.use_offline = use_offline
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.command_queue = queue.Queue()
        self.is_listening = False
        self._thread = None

        # Настройка чувствительности микрофона
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

        # Калибровка микрофона
        self._calibrate()

        if use_offline:
            self._init_vosk()

    def _calibrate(self):
        """Калибровка микрофона под уровень шума."""
        logger.info("Калибровка микрофона...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        logger.info(f"Калибровка завершена. "
                   f"Energy threshold: {self.recognizer.energy_threshold}")

    def _init_vosk(self):
        """Инициализация Vosk для offline распознавания."""
        try:
            from vosk import Model, KaldiRecognizer
            import json

            model_path = "vosk-model-small-en-us"  # Скачать модель заранее
            self.vosk_model = Model(model_path)
            self.vosk_recognizer = KaldiRecognizer(self.vosk_model, 16000)
            logger.info("Vosk модель загружена успешно")
        except Exception as e:
            logger.error(f"Ошибка загрузки Vosk: {e}")
            self.use_offline = False

    def recognize_google(self, audio):
        """Распознавание через Google Speech API."""
        try:
            text = self.recognizer.recognize_google(
                audio,
                language=self.language
            )
            return text.lower()
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            logger.error(f"Ошибка Google API: {e}")
            return None

    def recognize_vosk(self, audio):
        """Offline распознавание через Vosk."""
        try:
            import json
            raw_data = audio.get_raw_data(
                convert_rate=16000,
                convert_width=2
            )
            if self.vosk_recognizer.AcceptWaveform(raw_data):
                result = json.loads(self.vosk_recognizer.Result())
                return result.get("text", "").lower()
        except Exception as e:
            logger.error(f"Ошибка Vosk: {e}")
        return None

    def _listen_loop(self):
        """Основной цикл прослушивания в отдельном потоке."""
        logger.info("🎤 Начало прослушивания команд...")

        with self.microphone as source:
            while self.is_listening:
                try:
                    logger.info("Слушаю...")
                    audio = self.recognizer.listen(
                        source,
                        timeout=5,
                        phrase_time_limit=4
                    )

                    # Выбор метода распознавания
                    if self.use_offline:
                        text = self.recognize_vosk(audio)
                    else:
                        text = self.recognize_google(audio)

                    if text:
                        logger.info(f"Распознано: '{text}'")
                        self.command_queue.put(text)

                except sr.WaitTimeoutError:
                    # Тайм-аут — продолжаем слушать
                    continue
                except Exception as e:
                    logger.error(f"Ошибка в цикле прослушивания: {e}")

    def start(self):
        """Запуск прослушивания в фоновом потоке."""
        self.is_listening = True
        self._thread = threading.Thread(
            target=self._listen_loop,
            daemon=True
        )
        self._thread.start()
        logger.info("Распознавание речи запущено")

    def stop(self):
        """Остановка прослушивания."""
        self.is_listening = False
        if self._thread:
            self._thread.join(timeout=3)
        logger.info("Распознавание речи остановлено")

    def get_command(self, timeout=0.1):
        """
        Получение команды из очереди.
        
        Returns:
            строка с распознанным текстом или None
        """
        try:
            return self.command_queue.get(timeout=timeout)
        except queue.Empty:
            return None

