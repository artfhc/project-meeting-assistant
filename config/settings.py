import os
import yaml
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

    # Summarization Prompts (loaded from YAML)
    _summarization_prompts = None

    @classmethod
    def get_summarization_prompts(cls):
        """Load summarization prompts from YAML file"""
        if cls._summarization_prompts is None:
            prompts_file = os.path.join(os.path.dirname(__file__), 'prompts.yaml')
            try:
                with open(prompts_file, 'r', encoding='utf-8') as f:
                    cls._summarization_prompts = yaml.safe_load(f)
            except Exception as e:
                print(f"Error loading prompts from {prompts_file}: {e}")
                # Fallback to a basic prompt
                cls._summarization_prompts = {
                    "Meeting Summary": "Please summarize the following meeting transcript:\n\n{transcript}"
                }
        return cls._summarization_prompts

    @property
    def SUMMARIZATION_PROMPTS(self):
        """Property to maintain compatibility with existing code"""
        return self.get_summarization_prompts()

    @classmethod
    def create_directories(cls):
        """Create necessary output directories"""
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.AUDIO_DIR, exist_ok=True)
        os.makedirs(cls.TRANSCRIPT_DIR, exist_ok=True)
        os.makedirs(cls.SUMMARY_DIR, exist_ok=True)