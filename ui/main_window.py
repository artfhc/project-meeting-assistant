import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QPushButton, QTextEdit, QLabel, QFileDialog,
                             QMessageBox, QProgressBar, QSplitter, QFrame, QStatusBar, QComboBox)
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

class TranscriptionWorkerThread(QThread):
    """Worker thread for processing audio transcription only"""
    finished = pyqtSignal(str)  # transcript only
    error = pyqtSignal(str)
    progress = pyqtSignal(str, int)  # message, percentage

    def __init__(self, audio_file):
        super().__init__()
        self.audio_file = audio_file

    def run(self):
        try:
            # Transcribe audio with progress callback
            transcriber = WhisperTranscriber()

            def progress_callback(message, percentage):
                self.progress.emit(message, percentage)

            transcript, transcript_file = transcriber.transcribe_audio(self.audio_file, progress_callback)

            if not transcript:
                self.error.emit("Failed to transcribe audio")
                return

            # Clean transcript
            self.progress.emit("Cleaning transcript...", 98)
            cleaner = TranscriptCleaner()
            cleaned_transcript = cleaner.clean_transcript(transcript)

            self.progress.emit("Complete!", 100)
            self.finished.emit(cleaned_transcript)

        except Exception as e:
            self.error.emit(f"Error processing audio: {str(e)}")

class SummarizationWorkerThread(QThread):
    """Worker thread for generating summary from transcript"""
    finished = pyqtSignal(str)  # summary only
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, transcript, prompt_template):
        super().__init__()
        self.transcript = transcript
        self.prompt_template = prompt_template

    def run(self):
        try:
            # Generate summary
            self.progress.emit("Generating summary...")
            summarizer = MeetingSummarizer()
            summary, summary_file = summarizer.summarize_transcript(self.transcript, self.prompt_template)

            if not summary:
                self.error.emit("Failed to generate summary")
                return

            self.finished.emit(summary)

        except Exception as e:
            self.error.emit(f"Error generating summary: {str(e)}")

class MeetingAssistantWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.recorder = AudioRecorder()
        self.file_manager = FileManager()
        self.db = MeetingDatabase()
        self.transcription_worker = None
        self.summarization_worker = None
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

        self.open_file_button = QPushButton("Open Audio File")
        self.open_file_button.setMinimumHeight(40)
        self.open_file_button.setMinimumWidth(120)
        self.open_file_button.clicked.connect(self.open_audio_file)
        top_controls_layout.addWidget(self.open_file_button)

        self.generate_summary_button = QPushButton("Generate Summary")
        self.generate_summary_button.setMinimumHeight(40)
        self.generate_summary_button.setMinimumWidth(140)
        self.generate_summary_button.clicked.connect(self.generate_summary)
        self.generate_summary_button.setEnabled(False)
        self.generate_summary_button.setStyleSheet("background-color: #dc3545; color: white;")
        top_controls_layout.addWidget(self.generate_summary_button)

        self.save_summary_button = QPushButton("Save Summary")
        self.save_summary_button.setMinimumHeight(40)
        self.save_summary_button.setMinimumWidth(120)
        self.save_summary_button.clicked.connect(self.save_summary)
        self.save_summary_button.setEnabled(False)
        top_controls_layout.addWidget(self.save_summary_button)

        # Add stretch to push buttons to the left and dropdown to the right
        top_controls_layout.addStretch()

        # Prompt selector dropdown in top right corner
        self.prompt_selector = QComboBox()
        self.prompt_selector.addItems(list(Config.SUMMARIZATION_PROMPTS.keys()))
        self.prompt_selector.setMinimumHeight(40)
        self.prompt_selector.setMinimumWidth(200)
        self.prompt_selector.setStyleSheet("""
            QComboBox {
                color: white;
                background-color: #444444;
                border: 1px solid #666666;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12pt;
            }
            QComboBox::drop-down {
                border: none;
                background-color: transparent;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                color: white;
                background-color: #444444;
                border: 1px solid #666666;
                border-radius: 8px;
                selection-background-color: #555555;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                border-radius: 4px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #555555;
            }
        """)
        top_controls_layout.addWidget(self.prompt_selector)

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

        # Add transcription status to status bar (left side)
        self.transcription_status = QLabel("Ready")
        self.status_bar.addPermanentWidget(self.transcription_status)

        # Add percentage display to status bar (right side)
        self.percentage_label = QLabel("")
        self.percentage_label.setMinimumWidth(80)
        self.percentage_label.setAlignment(Qt.AlignRight)
        self.percentage_label.setStyleSheet("font-weight: bold; color: #007ACC;")
        self.status_bar.addPermanentWidget(self.percentage_label)

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
                self.percentage_label.setText("")  # Clear percentage
                self.save_summary_button.setEnabled(False)
                self.clean_transcript_button.setEnabled(False)
                self.generate_summary_button.setEnabled(False)
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
        """Start transcription in worker thread"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)  # Percentage progress

        self.transcription_worker = TranscriptionWorkerThread(audio_file)
        self.transcription_worker.finished.connect(self.on_transcription_finished)
        self.transcription_worker.error.connect(self.on_transcription_error)
        self.transcription_worker.progress.connect(self.on_progress_update)
        self.transcription_worker.start()

    def on_transcription_finished(self, transcript):
        """Handle completed transcription"""
        self.current_transcript = transcript
        self.transcript_text.setText(transcript)

        self.progress_bar.setVisible(False)
        self.percentage_label.setText("")  # Clear percentage
        self.status_bar.showMessage("Recording stopped")
        self.transcription_status.setText(f"Transcribed with Whisper-{Config.WHISPER_MODEL} (local)")

        # Enable buttons after transcription is complete
        self.clean_transcript_button.setEnabled(True)
        self.generate_summary_button.setEnabled(True)

        # Clear any existing summary
        self.summary_text.clear()
        self.current_summary = ""
        self.save_summary_button.setEnabled(False)

    def on_transcription_error(self, error_message):
        """Handle transcription errors"""
        self.progress_bar.setVisible(False)
        self.percentage_label.setText("")  # Clear percentage
        self.status_bar.showMessage("Recording stopped")
        self.transcription_status.setText("Error")
        QMessageBox.critical(self, "Transcription Error", error_message)

    def generate_summary(self):
        """Generate summary from current transcript"""
        if not self.current_transcript:
            QMessageBox.warning(self, "Warning", "No transcript available to summarize")
            return

        # Get selected prompt
        selected_prompt_name = self.prompt_selector.currentText()
        selected_prompt = Config.SUMMARIZATION_PROMPTS[selected_prompt_name]

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.generate_summary_button.setEnabled(False)

        self.summarization_worker = SummarizationWorkerThread(self.current_transcript, selected_prompt)
        self.summarization_worker.finished.connect(self.on_summarization_finished)
        self.summarization_worker.error.connect(self.on_summarization_error)
        self.summarization_worker.progress.connect(self.on_progress_update)
        self.summarization_worker.start()

    def on_summarization_finished(self, summary):
        """Handle completed summarization"""
        self.current_summary = summary
        self.summary_text.setText(summary)

        self.progress_bar.setVisible(False)
        self.transcription_status.setText(f"Summary generated with {Config.OPENAI_MODEL}")

        # Enable buttons after summarization is complete
        self.generate_summary_button.setEnabled(True)
        self.save_summary_button.setEnabled(True)

    def on_summarization_error(self, error_message):
        """Handle summarization errors"""
        self.progress_bar.setVisible(False)
        self.transcription_status.setText("Summary generation failed")
        self.generate_summary_button.setEnabled(True)
        QMessageBox.critical(self, "Summarization Error", error_message)

    def on_progress_update(self, message, percentage=None):
        """Update progress status and percentage"""
        self.transcription_status.setText(message)
        if percentage is not None:
            self.progress_bar.setValue(percentage)
            self.percentage_label.setText(f"{percentage}%")

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

        # Clear summary since transcript changed - user needs to regenerate manually
        self.summary_text.clear()
        self.current_summary = ""
        self.save_summary_button.setEnabled(False)

    def closeEvent(self, event):
        """Handle application close event"""
        if self.recorder.is_recording:
            self.recorder.stop_recording()
        self.recorder.cleanup()

        if self.transcription_worker and self.transcription_worker.isRunning():
            self.transcription_worker.quit()
            self.transcription_worker.wait()

        if self.summarization_worker and self.summarization_worker.isRunning():
            self.summarization_worker.quit()
            self.summarization_worker.wait()

        event.accept()