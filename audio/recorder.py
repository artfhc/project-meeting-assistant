import pyaudio
import wave
import threading
import time
from datetime import datetime
from config.settings import Config

class AudioRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        self.frames = []
        self.stream = None
        self.recording_thread = None

    def start_recording(self):
        """Start audio recording in a separate thread"""
        if self.is_recording:
            return False

        self.frames = []
        self.is_recording = True

        # Configure audio stream
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=Config.CHANNELS,
            rate=Config.SAMPLE_RATE,
            input=True,
            frames_per_buffer=Config.CHUNK_SIZE
        )

        # Start recording in separate thread
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.start()

        return True

    def stop_recording(self):
        """Stop audio recording and return the filename"""
        if not self.is_recording:
            return None

        self.is_recording = False

        # Wait for recording thread to finish
        if self.recording_thread:
            self.recording_thread.join()

        # Stop and close the stream
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        filepath = f"{Config.AUDIO_DIR}/{filename}"

        # Save the recording
        self._save_recording(filepath)

        return filepath

    def _record_audio(self):
        """Internal method to continuously record audio"""
        while self.is_recording:
            try:
                data = self.stream.read(Config.CHUNK_SIZE, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                print(f"Error during recording: {e}")
                break

    def _save_recording(self, filepath):
        """Save recorded frames to WAV file"""
        try:
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(Config.CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(Config.SAMPLE_RATE)
                wf.writeframes(b''.join(self.frames))
            print(f"Recording saved to: {filepath}")
        except Exception as e:
            print(f"Error saving recording: {e}")

    def cleanup(self):
        """Clean up audio resources"""
        if self.is_recording:
            self.stop_recording()

        if self.audio:
            self.audio.terminate()