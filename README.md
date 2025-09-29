# Meeting Assistant

A desktop application for recording, transcribing, and summarizing meetings using AI.

## Features

- **Audio Recording**: Record audio using your laptop microphone and save as WAV files
- **Automatic Transcription**: Convert audio to text using OpenAI Whisper (local - no API required)
- **AI-Powered Summarization**: Generate intelligent meeting summaries using OpenAI GPT models
- **Export Options**: Save summaries as Markdown or plain text files
- **Clean UI**: Built with PyQt5 for a modern, cross-platform desktop experience
- **Hybrid Approach**: Local transcription + cloud summarization for best of both worlds

## Requirements

- Python 3.7 or higher
- Microphone access
- OpenAI API key (for summarization)

## Installation

### macOS Installation

1. **Install system dependencies**
   ```bash
   # Install Homebrew if you haven't already
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

   # Install PortAudio (required for PyAudio)
   brew install portaudio
   ```

2. **Install Python dependencies**
   ```bash
   cd meeting-assistant
   pip install -r requirements.txt
   ```

3. **Configure API key**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

### Linux Installation

1. **Install system dependencies**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install python3-pyqt5 portaudio19-dev python3-dev

   # CentOS/RHEL/Fedora
   sudo yum install python3-qt5 portaudio-devel python3-devel
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Windows Installation

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Note: PyAudio wheels are usually available for Windows, so no additional system dependencies are needed.

## Configuration

### API Key Setup

1. **Get an OpenAI API key**:
   - Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - Create a new API key
   - Copy the key

2. **Configure the application**:
   ```bash
   cp .env.example .env
   # Edit .env and paste your API key:
   OPENAI_API_KEY=your_actual_api_key_here
   ```

### Settings

You can modify settings in `config/settings.py`:

- **Audio quality settings** (sample rate, channels, chunk size)
- **Whisper model size** (tiny, base, small, medium, large)
  - `tiny`: Fastest, lowest accuracy (~39 MB)
  - `base`: Good balance (~74 MB) - **Default**
  - `small`: Better accuracy (~244 MB)
  - `medium`: High accuracy (~769 MB)
  - `large`: Best accuracy (~1550 MB)
- **OpenAI model** (gpt-3.5-turbo or gpt-4)
  - `gpt-3.5-turbo`: Faster, cheaper - **Default**
  - `gpt-4`: Better quality, more expensive

## Usage

1. **Start Recording**: Click the "Start Recording" button to begin recording audio
2. **Stop Recording**: Click "Stop Recording" when finished
3. **Wait for Processing**: The app will automatically transcribe the audio using local Whisper and generate an AI summary
4. **Review Results**: View the transcript and summary in the application
5. **Save Summary**: Use "Save as Markdown" or "Save as Text" to export the summary

## Project Structure

```
meeting-assistant/
│
├── app.py                  # Main entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .env.example           # Environment variables template
│
├── config/
│   └── settings.py        # Configuration settings
│
├── ui/
│   ├── main_window.py     # PyQt5 main window
│   └── resources/         # UI assets
│
├── audio/
│   ├── recorder.py        # Audio recording functionality
│   └── utils.py          # Audio utilities
│
├── transcription/
│   ├── whisper_client.py  # Whisper transcription
│   └── cleaner.py        # Transcript cleaning
│
├── summarization/
│   ├── summarizer.py     # AI summarization
│   └── prompts.py        # Summarization prompts
│
├── storage/
│   ├── file_manager.py   # File operations
│   └── db.py            # Meeting database
│
└── outputs/              # Generated files (created automatically)
    ├── audio/           # Recorded audio files
    ├── transcripts/     # Transcript files
    └── summaries/       # Summary files
```

## Troubleshooting

### Common Issues

1. **Audio Recording Issues**
   - Ensure microphone permissions are granted
   - Check that no other application is using the microphone
   - On macOS, you may need to grant microphone access in System Preferences

2. **Whisper Model Loading**
   - First run may take time to download the Whisper model
   - For faster transcription, use a smaller model (tiny/base) in settings

3. **Processing Errors**
   - First run may take time to download the Whisper model
   - Ensure you have sufficient disk space for the model files
   - Check that the audio file was recorded successfully

4. **PyQt5 Installation Issues**
   - On Linux: `sudo apt-get install python3-pyqt5`
   - On macOS: `brew install pyqt5`
   - On Windows: Use the pip installation

### Performance Tips

- Choose smaller Whisper models (tiny/base) for faster processing
- Use larger models (medium/large) for better accuracy with complex audio
- Close other audio applications while recording
- The app works completely offline - no internet required

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.