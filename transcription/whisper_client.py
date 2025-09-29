import whisper
import warnings
from datetime import datetime
from config.settings import Config

# Suppress the FP16 warning for CPU usage
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

class WhisperTranscriber:
    def __init__(self):
        self.local_model = None
        self._load_local_model()

    def _load_local_model(self):
        """Load local Whisper model"""
        try:
            print(f"Loading Whisper model: {Config.WHISPER_MODEL}")
            self.local_model = whisper.load_model(Config.WHISPER_MODEL)
            print("Whisper model loaded successfully")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            self.local_model = None

    def transcribe_audio(self, audio_filepath):
        """Transcribe audio file to text using local Whisper model"""
        if not self.local_model:
            return None, "Local Whisper model not loaded"

        try:
            print("Transcribing audio with local Whisper model...")
            result = self.local_model.transcribe(audio_filepath)
            transcript = result["text"].strip()

            # Save transcript to file
            transcript_filepath = self._save_transcript(transcript)

            return transcript, transcript_filepath
        except Exception as e:
            error_msg = f"Error transcribing with local model: {e}"
            print(error_msg)
            return None, error_msg

    def _save_transcript(self, transcript):
        """Save transcript to text file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transcript_{timestamp}.txt"
        filepath = f"{Config.TRANSCRIPT_DIR}/{filename}"

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(transcript)
            print(f"Transcript saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"Error saving transcript: {e}")
            return None