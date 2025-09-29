import os

class Config:
    # Audio Recording Settings
    SAMPLE_RATE = 44100
    CHANNELS = 1
    CHUNK_SIZE = 1024
    AUDIO_FORMAT = 'wav'

    # File Paths
    OUTPUT_DIR = 'outputs'
    AUDIO_DIR = os.path.join(OUTPUT_DIR, 'audio')
    TRANSCRIPT_DIR = os.path.join(OUTPUT_DIR, 'transcripts')
    SUMMARY_DIR = os.path.join(OUTPUT_DIR, 'summaries')

    # Whisper Settings (Local Only)
    WHISPER_MODEL = 'base'  # tiny, base, small, medium, large

    @classmethod
    def create_directories(cls):
        """Create necessary output directories"""
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.AUDIO_DIR, exist_ok=True)
        os.makedirs(cls.TRANSCRIPT_DIR, exist_ok=True)
        os.makedirs(cls.SUMMARY_DIR, exist_ok=True)