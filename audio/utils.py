import os
import wave

def get_audio_duration(filepath):
    """Get duration of audio file in seconds"""
    try:
        with wave.open(filepath, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / float(rate)
            return duration
    except Exception as e:
        print(f"Error getting audio duration: {e}")
        return 0

def validate_audio_file(filepath):
    """Validate that the audio file exists and is readable"""
    if not os.path.exists(filepath):
        return False, "File does not exist"

    try:
        with wave.open(filepath, 'rb') as wf:
            if wf.getnframes() == 0:
                return False, "Audio file is empty"
            return True, "Valid audio file"
    except Exception as e:
        return False, f"Invalid audio file: {e}"

def format_duration(seconds):
    """Format duration in seconds to MM:SS format"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"