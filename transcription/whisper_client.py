import whisper
import warnings
import librosa
import numpy as np
from datetime import datetime
from config.settings import Config
from .fast_speaker_detector import FastSpeakerDetector

# Suppress warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")
warnings.filterwarnings("ignore", message="PySoundFile failed. Trying audioread instead.")
warnings.filterwarnings("ignore", category=FutureWarning, module="librosa")

class WhisperTranscriber:
    def __init__(self, enable_speaker_detection=None):
        self.local_model = None
        self.speaker_detector = None
        # Use config setting if not explicitly specified
        if enable_speaker_detection is None:
            enable_speaker_detection = Config.ENABLE_SPEAKER_DIARIZATION
        self.enable_speaker_detection = enable_speaker_detection
        self._load_local_model()
        if enable_speaker_detection:
            self._load_speaker_detector()

    def _load_local_model(self):
        """Load local Whisper model"""
        try:
            print(f"Loading Whisper model: {Config.WHISPER_MODEL}")
            self.local_model = whisper.load_model(Config.WHISPER_MODEL)
            print("Whisper model loaded successfully")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            self.local_model = None

    def _load_speaker_detector(self):
        """Load fast speaker detector"""
        try:
            self.speaker_detector = FastSpeakerDetector()
        except Exception as e:
            print(f"Error loading speaker detector: {e}")
            self.speaker_detector = None

    def transcribe_audio(self, audio_filepath, progress_callback=None):
        """Transcribe audio file to text using local Whisper model with optional fast speaker detection"""
        if not self.local_model:
            return None, "Local Whisper model not loaded"

        try:
            if progress_callback:
                progress_callback("Loading audio file...", 0)

            # Step 1: Fast Speaker Detection (if enabled)
            speaker_segments = []
            if self.enable_speaker_detection and self.speaker_detector:
                if progress_callback:
                    progress_callback("Fast speaker detection...", 5)

                try:
                    print("Starting fast speaker detection (estimated 3-8 minutes)...")
                    speaker_segments = self.speaker_detector.detect_speakers(audio_filepath, progress_callback)
                    print(f"Fast speaker detection completed! Found {len(set([s['speaker'] for s in speaker_segments]))} speakers")

                    if progress_callback:
                        progress_callback("Speaker detection complete", 20)

                except Exception as e:
                    print(f"Speaker detection failed, continuing without speaker labels: {e}")
                    speaker_segments = []
                    if progress_callback:
                        progress_callback("Continuing without speaker labels...", 20)

            # Step 2: Load audio file (try different backends)
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
                progress_callback("Processing audio for transcription...", 25)

            # Step 3: Split audio into chunks (30 seconds each)
            chunk_length = 30 * sr  # 30 seconds in samples
            total_chunks = len(audio) // chunk_length + (1 if len(audio) % chunk_length > 0 else 0)

            if total_chunks == 0:
                total_chunks = 1

            audio_chunks_info = []

            # Step 4: Transcribe each chunk
            for i in range(total_chunks):
                start_idx = i * chunk_length
                end_idx = min((i + 1) * chunk_length, len(audio))
                chunk = audio[start_idx:end_idx]

                # Calculate progress (25% for setup, 65% for processing, 10% for finalization)
                progress = 25 + int((i / total_chunks) * 65)

                if progress_callback:
                    progress_callback(f"Transcribing chunk {i + 1}/{total_chunks}...", progress)

                # Transcribe chunk
                result = self.local_model.transcribe(chunk)
                chunk_text = result["text"].strip()

                if chunk_text:
                    # Calculate chunk timing
                    start_time = start_idx / sr
                    end_time = end_idx / sr

                    audio_chunks_info.append({
                        'start_time': start_time,
                        'end_time': end_time,
                        'transcript': chunk_text
                    })

            if progress_callback:
                progress_callback("Finalizing transcript...", 90)

            # Step 5: Combine transcription with speaker information
            if speaker_segments and self.speaker_detector:
                # Assign speakers to chunks
                speaker_chunks = self.speaker_detector.assign_speakers_to_chunks(speaker_segments, audio_chunks_info)
                # Format transcript with speaker labels
                transcript = self.speaker_detector.format_transcript_with_speakers(speaker_chunks)
            else:
                # No speaker detection, join chunks normally
                transcript = " ".join([chunk['transcript'] for chunk in audio_chunks_info]).strip()

            # Step 6: Save transcript to file
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