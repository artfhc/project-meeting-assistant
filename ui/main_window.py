import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QPushButton, QTextEdit, QLabel, QFileDialog,
                             QMessageBox, QProgressBar, QSplitter, QFrame, QStatusBar)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPalette

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio.recorder import AudioRecorder
from transcription.whisper_client import WhisperTranscriber
from transcription.cleaner import TranscriptCleaner
from summarization.summarizer import MeetingSummarizer
from storage.file_manager import FileManager
from storage.db import MeetingDatabase
from config.settings import Config

class WorkerThread(QThread):
    """Worker thread for processing audio transcription and summarization"""
    finished = pyqtSignal(str, str)  # transcript, summary
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, audio_file):
        super().__init__()
        self.audio_file = audio_file

    def run(self):
        try:
            # Transcribe audio
            self.progress.emit("Transcribing audio...")
            transcriber = WhisperTranscriber()
            transcript, transcript_file = transcriber.transcribe_audio(self.audio_file)

            if not transcript:
                self.error.emit("Failed to transcribe audio")
                return

            # Clean transcript
            cleaner = TranscriptCleaner()
            cleaned_transcript = cleaner.clean_transcript(transcript)

            # Generate summary
            self.progress.emit("Generating summary...")
            summarizer = MeetingSummarizer()
            summary, summary_file = summarizer.summarize_transcript(cleaned_transcript)

            if not summary:
                self.error.emit("Failed to generate summary")
                return

            self.finished.emit(cleaned_transcript, summary)

        except Exception as e:
            self.error.emit(f"Error processing audio: {str(e)}")

class MeetingAssistantWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.recorder = AudioRecorder()
        self.file_manager = FileManager()
        self.db = MeetingDatabase()
        self.worker_thread = None
        self.current_transcript = ""
        self.current_summary = ""

        self.init_ui()
        self.setup_style()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Meeting Recorder")
        self.setGeometry(100, 100, 1200, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Top button controls
        top_controls_layout = QHBoxLayout()

        self.record_button = QPushButton("Record")
        self.record_button.setMinimumHeight(40)
        self.record_button.setMinimumWidth(120)
        self.record_button.clicked.connect(self.toggle_recording)
        top_controls_layout.addWidget(self.record_button)

        self.open_file_button = QPushButton("Open File")
        self.open_file_button.setMinimumHeight(40)
        self.open_file_button.setMinimumWidth(120)
        self.open_file_button.clicked.connect(self.open_audio_file)
        top_controls_layout.addWidget(self.open_file_button)

        self.save_summary_button = QPushButton("Save Summary")
        self.save_summary_button.setMinimumHeight(40)
        self.save_summary_button.setMinimumWidth(120)
        self.save_summary_button.clicked.connect(self.save_summary)
        self.save_summary_button.setEnabled(False)
        top_controls_layout.addWidget(self.save_summary_button)

        # Add stretch to push buttons to the left
        top_controls_layout.addStretch()

        main_layout.addLayout(top_controls_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Content splitter (horizontal)
        splitter = QSplitter(Qt.Horizontal)

        # Left side - Transcript section
        transcript_frame = QFrame()
        transcript_layout = QVBoxLayout(transcript_frame)

        transcript_label = QLabel("Transcript")
        transcript_label.setFont(QFont("Arial", 14, QFont.Bold))
        transcript_layout.addWidget(transcript_label)

        self.transcript_text = QTextEdit()
        self.transcript_text.setPlaceholderText("Transcript will appear here after recording...")
        transcript_layout.addWidget(self.transcript_text)

        # Clean Transcript button
        self.clean_transcript_button = QPushButton("Clean Transcript")
        self.clean_transcript_button.setMinimumHeight(35)
        self.clean_transcript_button.clicked.connect(self.clean_transcript)
        self.clean_transcript_button.setEnabled(False)
        transcript_layout.addWidget(self.clean_transcript_button)

        splitter.addWidget(transcript_frame)

        # Right side - Summary section
        summary_frame = QFrame()
        summary_layout = QVBoxLayout(summary_frame)

        summary_label = QLabel("## Meeting Summary")
        summary_label.setFont(QFont("Arial", 14, QFont.Bold))
        summary_layout.addWidget(summary_label)

        self.summary_text = QTextEdit()
        self.summary_text.setPlaceholderText("### Key Points\n\n### Decisions\n\n### Action Items\n\n### Open Questions")
        summary_layout.addWidget(self.summary_text)

        splitter.addWidget(summary_frame)

        # Set equal sizes for both panels
        splitter.setSizes([600, 600])

        main_layout.addWidget(splitter)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Recording stopped")
        self.setStatusBar(self.status_bar)

        # Add transcription status to status bar
        self.transcription_status = QLabel("Ready")
        self.status_bar.addPermanentWidget(self.transcription_status)

    def setup_style(self):
        """Setup application styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
                font-size: 11pt;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QLabel {
                color: #333;
            }
        """)

    def toggle_recording(self):
        """Start or stop audio recording"""
        if not self.recorder.is_recording:
            # Start recording
            success = self.recorder.start_recording()
            if success:
                self.record_button.setText("Stop")
                self.record_button.setStyleSheet("background-color: #f44336;")
                self.status_bar.showMessage("Recording...")
                self.transcript_text.clear()
                self.summary_text.clear()
                self.save_summary_button.setEnabled(False)
                self.clean_transcript_button.setEnabled(False)
            else:
                QMessageBox.warning(self, "Error", "Failed to start recording")
        else:
            # Stop recording
            audio_file = self.recorder.stop_recording()
            self.record_button.setText("Record")
            self.record_button.setStyleSheet("")
            self.status_bar.showMessage("Recording stopped")

            if audio_file:
                # Start processing in worker thread
                self.start_processing(audio_file)
            else:
                QMessageBox.warning(self, "Error", "Failed to save recording")
                self.status_bar.showMessage("Recording stopped")

    def start_processing(self, audio_file):
        """Start processing audio in worker thread"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        self.worker_thread = WorkerThread(audio_file)
        self.worker_thread.finished.connect(self.on_processing_finished)
        self.worker_thread.error.connect(self.on_processing_error)
        self.worker_thread.progress.connect(self.on_progress_update)
        self.worker_thread.start()

    def on_processing_finished(self, transcript, summary):
        """Handle completed processing"""
        self.current_transcript = transcript
        self.current_summary = summary

        self.transcript_text.setText(transcript)
        self.summary_text.setText(summary)

        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Recording stopped")
        self.transcription_status.setText(f"Transcribed with Whisper-{Config.WHISPER_MODEL} (local)")

        self.save_summary_button.setEnabled(True)
        self.clean_transcript_button.setEnabled(True)

    def on_processing_error(self, error_message):
        """Handle processing errors"""
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Recording stopped")
        self.transcription_status.setText("Error")
        QMessageBox.critical(self, "Processing Error", error_message)

    def on_progress_update(self, message):
        """Update progress status"""
        self.transcription_status.setText(message)

    def open_audio_file(self):
        """Open and process an existing audio file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Audio File", "", "Audio files (*.wav *.mp3 *.m4a *.flac *.ogg)"
        )

        if filename:
            self.start_processing(filename)

    def save_summary(self):
        """Save summary with file dialog"""
        if not self.current_summary:
            QMessageBox.warning(self, "Warning", "No summary to save")
            return

        filename, selected_filter = QFileDialog.getSaveFileName(
            self, "Save Summary", "", "Markdown files (*.md);;Text files (*.txt)"
        )

        if filename:
            if selected_filter == "Markdown files (*.md)":
                filepath = self.file_manager.save_summary_as_markdown(
                    self.current_summary, os.path.basename(filename)
                )
            else:
                filepath = self.file_manager.save_summary_as_text(
                    self.current_summary, os.path.basename(filename)
                )

            if filepath:
                QMessageBox.information(self, "Success", f"Summary saved to:\n{filepath}")
            else:
                QMessageBox.critical(self, "Error", "Failed to save file")

    def clean_transcript(self):
        """Clean and improve the transcript text"""
        if not self.current_transcript:
            QMessageBox.warning(self, "Warning", "No transcript to clean")
            return

        from transcription.cleaner import TranscriptCleaner
        cleaner = TranscriptCleaner()
        cleaned_text = cleaner.clean_transcript(self.current_transcript)

        self.transcript_text.setText(cleaned_text)
        self.current_transcript = cleaned_text

        # Regenerate summary with cleaned transcript
        if cleaned_text:
            from summarization.summarizer import MeetingSummarizer
            summarizer = MeetingSummarizer()
            summary, _ = summarizer.summarize_transcript(cleaned_text)
            if summary:
                self.current_summary = summary
                self.summary_text.setText(summary)

    def closeEvent(self, event):
        """Handle application close event"""
        if self.recorder.is_recording:
            self.recorder.stop_recording()
        self.recorder.cleanup()

        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()

        event.accept()