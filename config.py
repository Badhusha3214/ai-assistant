import os
import platform
import subprocess
from dotenv import load_dotenv

load_dotenv()

# System detection
SYSTEM_TYPE = platform.system().lower()
IS_UBUNTU = "linux" in SYSTEM_TYPE and os.path.exists("/etc/lsb-release")

# Check if running on ARM64
IS_ARM64 = False
if IS_UBUNTU:
    try:
        arch = subprocess.check_output("uname -m", shell=True).decode().strip()
        IS_ARM64 = arch in ["aarch64", "arm64"]
    except:
        # Fall back to platform module detection
        IS_ARM64 = "aarch64" in platform.machine().lower() or "arm64" in platform.machine().lower()

# Porcupine API mode settings
USE_API_ONLY_MODE = os.getenv("USE_API_ONLY_MODE", "false").lower() == "true"

# Wake Word Settings
WAKE_WORD = "bumblebee"  # Primary wake word
# Different fallback options for ARM64 or API mode
if USE_API_ONLY_MODE:
    FALLBACK_WAKE_WORDS = ["porcupine", "alexa", "computer", "jarvis", "bumblebee"]
elif IS_ARM64:
    FALLBACK_WAKE_WORDS = ["porcupine", "alexa", "computer", "jarvis"]
else:
    FALLBACK_WAKE_WORDS = ["porcupine", "picovoice"]

PVPORCUPINE_ACCESS_KEY = os.getenv("PVPORCUPINE_ACCESS_KEY")
# Path to custom keyword file (ppn file) - set to None or empty string if not using
CUSTOM_KEYWORD_PATH = os.getenv("CUSTOM_KEYWORD_PATH", "")

# Default model paths for ARM64
ARM64_MODEL_PATH = os.getenv("ARM64_MODEL_PATH", "")
USE_SYSTEM_LIBRARIES = os.getenv("USE_SYSTEM_LIBRARIES", "false").lower() == "true"

# Audio Settings
AUDIO_DEVICE_INDEX = int(os.getenv("AUDIO_DEVICE_INDEX", "0"))
SAMPLE_RATE = 16000
CHANNELS = 1

# AI Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
