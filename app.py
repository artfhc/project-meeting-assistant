#!/usr/bin/env python3
"""
Meeting Assistant Desktop Application

A PyQt5 desktop application for recording, transcribing, and summarizing meetings.

Features:
- Audio recording using laptop microphone
- Automatic transcription using OpenAI Whisper
- AI-powered summarization using Claude or OpenAI
- Export summaries to Markdown or Text files

Usage:
    python app.py

Requirements:
    - Python 3.7+
    - PyQt5
    - OpenAI API key (optional, for API-based transcription)
    - Anthropic API key (optional, for Claude summarization)
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MeetingAssistantWindow
from config.settings import Config

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []

    try:
        import pyaudio
    except ImportError:
        missing_deps.append("pyaudio")

    try:
        import whisper
    except ImportError:
        missing_deps.append("openai-whisper")

    try:
        from PyQt5.QtWidgets import QApplication
    except ImportError:
        missing_deps.append("PyQt5")

    return missing_deps

def check_system_requirements():
    """Check if system meets requirements"""
    warnings = []

    # Check available disk space for Whisper models
    import shutil
    free_space_gb = shutil.disk_usage(".").free / (1024**3)
    if free_space_gb < 2:
        warnings.append("Low disk space detected. Whisper models require at least 2GB of free space.")

    # Check for OpenAI API key
    if not Config.OPENAI_API_KEY:
        warnings.append("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file for summarization to work.")

    return warnings

def setup_environment():
    """Setup application environment"""
    # Create necessary directories
    Config.create_directories()

    # Set high DPI attributes for better scaling
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

def main():
    """Main application entry point"""
    print("Starting Meeting Assistant...")

    # Check dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        print(f"Error: Missing required dependencies: {', '.join(missing_deps)}")
        print("Please install missing dependencies using:")
        print("pip install -r requirements.txt")
        sys.exit(1)

    # Setup environment
    setup_environment()

    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Meeting Assistant")
    app.setApplicationVersion("1.0.0")

    # Check system requirements and show warnings
    system_warnings = check_system_requirements()
    if system_warnings:
        warning_message = "System Requirements:\n\n" + "\n".join(system_warnings)
        warning_message += "\n\nThe application may still work but performance could be affected."

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("System Warning")
        msg_box.setText(warning_message)
        msg_box.exec_()

    # Create and show main window
    try:
        main_window = MeetingAssistantWindow()
        main_window.show()

        print("Meeting Assistant started successfully!")
        print("Features:")
        print("- Local transcription with Whisper (no internet required)")
        print("- AI-powered summarization with OpenAI GPT")
        print("You can now:")
        print("1. Click 'Start Recording' to begin recording audio")
        print("2. Click 'Stop Recording' to end recording and process with local Whisper + OpenAI")
        print("3. View the transcript and AI-generated summary")
        print("4. Save the summary as Markdown or Text file")

        # Start the application event loop
        sys.exit(app.exec_())

    except Exception as e:
        print(f"Error starting application: {e}")

        # Show error dialog
        error_app = QApplication(sys.argv)
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Application Error")
        msg_box.setText(f"Failed to start Meeting Assistant:\n\n{str(e)}")
        msg_box.exec_()

        sys.exit(1)

if __name__ == "__main__":
    main()