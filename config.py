import os
from dotenv import load_dotenv

load_dotenv()

# Wake Word Settings
WAKE_WORD = "bumblebee"  # Changed to bumblebee
PVPORCUPINE_ACCESS_KEY = os.getenv("PVPORCUPINE_ACCESS_KEY")

# Audio Settings
AUDIO_DEVICE_INDEX = 0
SAMPLE_RATE = 16000
CHANNELS = 1

# AI Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
