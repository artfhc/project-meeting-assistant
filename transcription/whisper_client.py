import whisper
import warnings
import librosa
import numpy as np
from datetime import datetime
from config.settings import Config

# Suppress warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")
warnings.filterwarnings("ignore", message="PySoundFile failed. Trying audioread instead.")
warnings.filterwarnings("ignore", category=FutureWarning, module="librosa")

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

    def transcribe_audio(self, audio_filepath, progress_callback=None):
        """Transcribe audio file to text using local Whisper model with chunked processing"""
        if not self.local_model:
            return None, "Local Whisper model not loaded"

        try:
            if progress_callback:
                progress_callback("Loading audio file...", 0)

            # Load audio file (try different backends)
            try:
                audio, sr = librosa.load(audio_filepath, sr=16000)  # Whisper expects 16kHz
            except Exception as e:
                # Fallback: let Whisper handle the audio loading directly
                print(f"Librosa failed to load audio: {e}. Using direct Whisper processing...")
                result = self.local_model.transcribe(audio_filepath)
                transcript = result["text"].strip()
                transcript_filepath = self._save_transcript(transcript)
                if progress_callback:
                    progress_callback("Transcription complete!", 100)
                return transcript, transcript_filepath

            if progress_callback:
                progress_callback("Processing audio...", 5)

            # Split audio into chunks (30 seconds each)
            chunk_length = 30 * sr  # 30 seconds in samples
            total_chunks = len(audio) // chunk_length + (1 if len(audio) % chunk_length > 0 else 0)

            if total_chunks == 0:
                total_chunks = 1

            transcript_parts = []

            for i in range(total_chunks):
                start_idx = i * chunk_length
                end_idx = min((i + 1) * chunk_length, len(audio))
                chunk = audio[start_idx:end_idx]

                # Calculate progress (5% for loading, 90% for processing, 5% for saving)
                progress = 5 + int((i / total_chunks) * 90)

                if progress_callback:
                    progress_callback(f"Transcribing chunk {i + 1}/{total_chunks}...", progress)

                # Transcribe chunk
                result = self.local_model.transcribe(chunk)
                chunk_text = result["text"].strip()

                if chunk_text:
                    transcript_parts.append(chunk_text)

            if progress_callback:
                progress_callback("Finalizing transcript...", 95)

            # Join all transcript parts
            transcript = " ".join(transcript_parts).strip()

            # Save transcript to file
            transcript_filepath = self._save_transcript(transcript)

            if progress_callback:
                progress_callback("Transcription complete!", 100)

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