import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QPushButton, QTextEdit, QLabel, QFileDialog,
                             QMessageBox, QProgressBar, QSplitter, QFrame)
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
        self.setWindowTitle("Meeting Assistant")
        self.setGeometry(100, 100, 1000, 700)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel("Meeting Assistant")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        # Recording controls
        controls_layout = QHBoxLayout()

        self.record_button = QPushButton("Start Recording")
        self.record_button.setMinimumHeight(50)
        self.record_button.clicked.connect(self.toggle_recording)
        controls_layout.addWidget(self.record_button)

        self.status_label = QLabel("Ready to record")
        self.status_label.setAlignment(Qt.AlignCenter)
        controls_layout.addWidget(self.status_label)

        main_layout.addLayout(controls_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Content splitter
        splitter = QSplitter(Qt.Horizontal)

        # Transcript section
        transcript_frame = QFrame()
        transcript_layout = QVBoxLayout(transcript_frame)

        transcript_label = QLabel("Transcript")
        transcript_label.setFont(QFont("Arial", 12, QFont.Bold))
        transcript_layout.addWidget(transcript_label)

        self.transcript_text = QTextEdit()
        self.transcript_text.setPlaceholderText("Transcript will appear here after recording...")
        transcript_layout.addWidget(self.transcript_text)

        splitter.addWidget(transcript_frame)

        # Summary section
        summary_frame = QFrame()
        summary_layout = QVBoxLayout(summary_frame)

        summary_label = QLabel("Summary")
        summary_label.setFont(QFont("Arial", 12, QFont.Bold))
        summary_layout.addWidget(summary_label)

        self.summary_text = QTextEdit()
        self.summary_text.setPlaceholderText("Summary will appear here after processing...")
        summary_layout.addWidget(self.summary_text)

        splitter.addWidget(summary_frame)

        main_layout.addWidget(splitter)

        # Save controls
        save_layout = QHBoxLayout()

        self.save_md_button = QPushButton("Save as Markdown")
        self.save_md_button.clicked.connect(self.save_as_markdown)
        self.save_md_button.setEnabled(False)
        save_layout.addWidget(self.save_md_button)

        self.save_txt_button = QPushButton("Save as Text")
        self.save_txt_button.clicked.connect(self.save_as_text)
        self.save_txt_button.setEnabled(False)
        save_layout.addWidget(self.save_txt_button)

        main_layout.addLayout(save_layout)

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
                self.record_button.setText("Stop Recording")
                self.record_button.setStyleSheet("background-color: #f44336;")
                self.status_label.setText("Recording...")
                self.transcript_text.clear()
                self.summary_text.clear()
                self.save_md_button.setEnabled(False)
                self.save_txt_button.setEnabled(False)
            else:
                QMessageBox.warning(self, "Error", "Failed to start recording")
        else:
            # Stop recording
            audio_file = self.recorder.stop_recording()
            self.record_button.setText("Start Recording")
            self.record_button.setStyleSheet("")
            self.status_label.setText("Processing...")

            if audio_file:
                # Start processing in worker thread
                self.start_processing(audio_file)
            else:
                QMessageBox.warning(self, "Error", "Failed to save recording")
                self.status_label.setText("Ready to record")

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
        self.status_label.setText("Processing complete!")

        self.save_md_button.setEnabled(True)
        self.save_txt_button.setEnabled(True)

    def on_processing_error(self, error_message):
        """Handle processing errors"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready to record")
        QMessageBox.critical(self, "Processing Error", error_message)

    def on_progress_update(self, message):
        """Update progress status"""
        self.status_label.setText(message)

    def save_as_markdown(self):
        """Save summary as markdown file"""
        if not self.current_summary:
            QMessageBox.warning(self, "Warning", "No summary to save")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Summary as Markdown", "", "Markdown files (*.md)"
        )

        if filename:
            filepath = self.file_manager.save_summary_as_markdown(
                self.current_summary, os.path.basename(filename)
            )
            if filepath:
                QMessageBox.information(self, "Success", f"Summary saved to:\n{filepath}")
            else:
                QMessageBox.critical(self, "Error", "Failed to save file")

    def save_as_text(self):
        """Save summary as text file"""
        if not self.current_summary:
            QMessageBox.warning(self, "Warning", "No summary to save")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Summary as Text", "", "Text files (*.txt)"
        )

        if filename:
            filepath = self.file_manager.save_summary_as_text(
                self.current_summary, os.path.basename(filename)
            )
            if filepath:
                QMessageBox.information(self, "Success", f"Summary saved to:\n{filepath}")
            else:
                QMessageBox.critical(self, "Error", "Failed to save file")

    def closeEvent(self, event):
        """Handle application close event"""
        if self.recorder.is_recording:
            self.recorder.stop_recording()
        self.recorder.cleanup()

        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()

        event.accept()