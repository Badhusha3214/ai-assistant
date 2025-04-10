# Setting Up the Voice Assistant on Ubuntu ARM64

This guide will help you set up the voice assistant on Ubuntu ARM64 systems.

## Prerequisites

1. Ubuntu on ARM64 architecture
2. Python 3.7 or newer
3. PIP package manager
4. A valid Picovoice access key

## Installation Steps

### 1. Install Required System Packages

```bash
# Update package lists
sudo apt update

# Install required packages
sudo apt install -y python3-dev python3-pip portaudio19-dev libatomic1
```

### 2. Create and Activate Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

### 3. Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install the required packages
pip install pvporcupine pyaudio python-dotenv google-generativeai pyttsx3 SpeechRecognition
```

### 4. Configure the Environment

1. Edit the `.env` file and set the following variables:

```
PVPORCUPINE_ACCESS_KEY=your_access_key_here
AUDIO_DEVICE_INDEX=0  # You might need to change this based on your setup
USE_SYSTEM_LIBRARIES=true  # Try this if you have issues with the default libraries
```

2. List available audio devices:
   
```bash
# Run the assistant to see available audio devices
python main.py
```

3. Note the device ID of your microphone and update `AUDIO_DEVICE_INDEX` in the `.env` file if needed.

### 5. Generate a Custom Wake Word (Optional)

If the built-in wake words don't work on your ARM64 system, you can create a custom one:

1. Go to [Picovoice Console](https://console.picovoice.ai/)
2. Sign in with your account
3. Navigate to "Wake Word" section
4. Create a new wake word for ARM64 platform
5. Download the model file (.ppn)
6. Set the path to this file in the `.env`:

```
ARM64_MODEL_PATH=/path/to/downloaded/model.ppn
```

### 6. Run the Assistant

```bash
# Make sure you're in the project directory with virtual environment activated
python main.py
```

## Troubleshooting

### If you encounter library loading errors:

Try installing the Porcupine systemwide:

```bash
sudo pip3 install pvporcupine
```

### If audio device detection fails:

Check available audio devices with:

```bash
python -c "import pyaudio; p = pyaudio.PyAudio(); info = p.get_host_api_info_by_index(0); num_devices = info.get('deviceCount'); [print(f'Device {i}: {p.get_device_info_by_host_api_device_index(0, i).get(\"name\")}') for i in range(num_devices) if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0]; p.terminate()"
```

Then update the `AUDIO_DEVICE_INDEX` in your `.env` file.

### If wake word detection still fails:

1. Try a different wake word from the available list
2. Use a custom keyword file generated for ARM64
3. Ensure you're in a quiet environment with a good microphone
