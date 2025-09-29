import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

    # Audio Recording Settings
    SAMPLE_RATE = 44100
    CHANNELS = 1
    CHUNK_SIZE = 1024
    AUDIO_FORMAT = 'mp3'

    # File Paths
    OUTPUT_DIR = 'outputs'
    AUDIO_DIR = os.path.join(OUTPUT_DIR, 'audio')
    TRANSCRIPT_DIR = os.path.join(OUTPUT_DIR, 'transcripts')
    SUMMARY_DIR = os.path.join(OUTPUT_DIR, 'summaries')

    # Whisper Settings (Local Only)
    WHISPER_MODEL = 'base'  # tiny, base, small, medium, large

    # OpenAI Settings
    OPENAI_MODEL = 'gpt-4o-mini'  # or 'gpt-4' for better quality

    @classmethod
    def create_directories(cls):
        """Create necessary output directories"""
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.AUDIO_DIR, exist_ok=True)
        os.makedirs(cls.TRANSCRIPT_DIR, exist_ok=True)
        os.makedirs(cls.SUMMARY_DIR, exist_ok=True)