# AI Assistant Installation Guide

This guide will help you set up the AI assistant on your system.

## Requirements

- Python 3.7 or newer
- Internet connection for API calls
- Microphone for voice input (optional)
- Speakers for voice output

## Installation Steps

### 1. Install Python Dependencies

```bash
# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install pvporcupine pyaudio python-dotenv google-generativeai pyttsx3 SpeechRecognition
```

### 2. Configure Environment Variables

Create a `.env` file in the project directory with the following content:

```
PVPORCUPINE_ACCESS_KEY=your_picovoice_key_here
GEMINI_API_KEY=your_gemini_api_key_here
# Set to true if you want to use Porcupine in cloud API-only mode
USE_API_ONLY_MODE=false
```

You'll need to:
1. Get a Picovoice access key from: https://console.picovoice.ai/
2. Get a Gemini API key from: https://aistudio.google.com/app/apikey

### 3. Prepare College Data

The system uses `college_data.json` for college information. Make sure this file exists in the project directory.

### 4. Launch the Assistant

```bash
python main.py
```

## Running Modes

### Local Processing Mode (Default)
By default, the system attempts to use local libraries for wake word detection, which provides better performance and works offline.

### API-Only Mode
If you're experiencing issues with local libraries, especially on ARM64 systems, you can run in API-only mode:

1. In your `.env` file, set:
```
USE_API_ONLY_MODE=true
```

API-only mode advantages:
- Works on systems where local libraries fail to load
- No need to install platform-specific dependencies
- Same wake words available on all platforms

API-only mode limitations:
- Requires internet connection
- May have higher latency
- Counts against your Picovoice API usage quotas

## Running on Different Platforms

### Windows
- No special configuration needed

### macOS
- You may need to grant microphone permissions

### Linux
- Install PortAudio: `sudo apt-get install portaudio19-dev`
- Install PyAudio: `pip install pyaudio`

### Ubuntu ARM64
- See `UBUNTU_ARM64_SETUP.md` for detailed instructions
- Consider using API-only mode if you encounter issues with local libraries

## Troubleshooting

### Wake Word Detection Issues
- Check your Picovoice access key
- Try API-only mode by setting `USE_API_ONLY_MODE=true` in your `.env` file
- Try with different wake words
- Ensure microphone permissions are granted
- On ARM64, follow the ARM64-specific setup guide

### Speech Recognition Issues
- Ensure you have a working internet connection
- Check microphone settings
- Speak clearly and reduce background noise

### API Errors
- Verify API keys are valid
- Check for proper JSON formatting in college_data.json
- Ensure internet connectivity for API calls

## Running in Text-Only Mode

If voice recognition doesn't work on your system, the assistant will automatically fall back to text input mode.
