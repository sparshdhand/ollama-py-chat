import whisper
import os
import warnings
import threading

# Suppress warnings from Whisper/Torch if necessary
warnings.filterwarnings("ignore")

class Transcriber:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Transcriber, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_size="base"):
        """
        Initializes the Whisper model.
        model_size: 'tiny', 'base', 'small', 'medium', 'large'
        """
        if self._initialized:
            return

        print(f"Loading Whisper model '{model_size}'...")
        self.model = whisper.load_model(model_size)
        print("Whisper model loaded.")
        self._initialized = True

    def transcribe(self, audio_path):
        """
        Transcribes the given audio file.
        Returns the transcribed text.
        """
        if not os.path.exists(audio_path):
            return "Error: Audio file not found."

        try:
            result = self.model.transcribe(audio_path)
            return result["text"].strip()
        except Exception as e:
            return f"Error during transcription: {str(e)}"
