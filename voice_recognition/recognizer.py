import speech_recognition as sr
import threading
import queue
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceRecognizer:
    """
    Class for continuous voice command recognition.
    Supports Google Speech API and Vosk (offline).
    """

    def __init__(self, language="en-US", use_offline=False):
        self.language = language
        self.use_offline = use_offline
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.command_queue = queue.Queue()
        self.is_listening = False
        self._thread = None

        # Microphone sensitivity setup
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

        # Microphone calibration
        self._calibrate()

        if use_offline:
            self._init_vosk()

    def _calibrate(self):
        """Calibrating microphone to ambient noise level."""
        logger.info("Calibrating microphone...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        logger.info(f"Calibration completed. "
                   f"Energy threshold: {self.recognizer.energy_threshold}")

    def _init_vosk(self):
        """Initializing Vosk for offline recognition."""
        try:
            from vosk import Model, KaldiRecognizer
            import json

            model_path = "vosk-model-small-en-us"  # Download model in advance
            self.vosk_model = Model(model_path)
            self.vosk_recognizer = KaldiRecognizer(self.vosk_model, 16000)
            logger.info("Vosk model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Vosk: {e}")
            self.use_offline = False

    def recognize_google(self, audio):
        """Recognition via Google Speech API."""
        try:
            text = self.recognizer.recognize_google(
                audio,
                language=self.language
            )
            return text.lower()
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            logger.error(f"Google API Error: {e}")
            return None

    def recognize_vosk(self, audio):
        """Offline recognition via Vosk."""
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
            logger.error(f"Vosk Error: {e}")
        return None

    def _listen_loop(self):
        """Main listening loop in a separate thread."""
        logger.info(" Starting to listen for commands...")

        with self.microphone as source:
            while self.is_listening:
                try:
                    logger.info("Listening...")
                    audio = self.recognizer.listen(
                        source,
                        timeout=5,
                        phrase_time_limit=4
                    )

                    # Choosing recognition method
                    if self.use_offline:
                        text = self.recognize_vosk(audio)
                    else:
                        text = self.recognize_google(audio)

                    if text:
                        logger.info(f"Recognized: '{text}'")
                        self.command_queue.put(text)

                except sr.WaitTimeoutError:
                    # Timeout - continue listening
                    continue
                except Exception as e:
                    logger.error(f"Error in listening loop: {e}")

    def start(self):
        """Start listening in a background thread."""
        self.is_listening = True
        self._thread = threading.Thread(
            target=self._listen_loop,
            daemon=True
        )
        self._thread.start()
        logger.info("Speech recognition started")

    def stop(self):
        """Stop listening."""
        self.is_listening = False
        if self._thread:
            self._thread.join(timeout=3)
        logger.info("Speech recognition stopped")

    def get_command(self, timeout=0.1):
        """
        Getting command from queue.
        
        Returns:
            string with recognized text or None
        """
        try:
            return self.command_queue.get(timeout=timeout)
        except queue.Empty:
            return None