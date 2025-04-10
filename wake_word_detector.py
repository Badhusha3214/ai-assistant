import pvporcupine
import struct
import pyaudio
import time
import os
import platform
import subprocess
from config import (
    PVPORCUPINE_ACCESS_KEY, WAKE_WORD, CUSTOM_KEYWORD_PATH, 
    FALLBACK_WAKE_WORDS, IS_UBUNTU, IS_ARM64, ARM64_MODEL_PATH,
    USE_SYSTEM_LIBRARIES, AUDIO_DEVICE_INDEX, USE_API_ONLY_MODE
)

class WakeWordDetector:
    @staticmethod
    def list_wake_words():
        try:
            keywords = pvporcupine.KEYWORDS
            print("\nAvailable wake words:")
            print("---------------------")
            for i, keyword in enumerate(keywords, 1):
                print(f"{i}. {keyword}")
            return keywords
        except Exception as e:
            print(f"Error listing wake words: {e}")
            return []
    
    @staticmethod
    def test_porcupine_installation():
        """Test if Porcupine can be initialized with a simple keyword"""
        print("Testing Porcupine installation...")
        try:
            # Try with 'porcupine' - available on all platforms
            test_keyword = "porcupine"
            test_porcupine = pvporcupine.create(
                access_key=PVPORCUPINE_ACCESS_KEY,
                keywords=[test_keyword]
            )
            test_porcupine.delete()
            if USE_API_ONLY_MODE:
                print("✓ Porcupine API connection successful!")
            else:
                print("✓ Porcupine test successful!")
            return True
        except Exception as e:
            print(f"✗ Porcupine test failed: {e}")
            if "AccessKey" in str(e):
                print("The issue appears to be with your access key. Please check it's valid and properly formatted.")
            elif "library" in str(e).lower() and IS_ARM64:
                print("ARM64 library issue detected. Make sure libpv_porcupine is installed for ARM64.")
                print("Try: 'sudo apt-get install -y libatomic1'")
                print("See UBUNTU_ARM64_SETUP.md for detailed instructions.")
                print("Alternatively, set USE_API_ONLY_MODE=true in your .env file to use cloud-based processing.")
            return False
    
    @staticmethod
    def get_audio_devices():
        """List available audio devices"""
        print("\nChecking audio devices...")
        try:
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            num_devices = info.get('deviceCount')
            
            for i in range(num_devices):
                if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
                    name = p.get_device_info_by_host_api_device_index(0, i).get('name')
                    print(f"Input Device id {i} - {name}")
            p.terminate()
        except Exception as e:
            print(f"Error checking audio devices: {e}")

    def __init__(self, retry_count=3):
        self.porcupine = None
        self.pa = None
        self.audio_stream = None
        self.active_wake_word = None
        
        # List audio devices for debugging
        self.get_audio_devices()
        
        # Handle API-only mode first if enabled
        if USE_API_ONLY_MODE:
            print("\n*** Using Porcupine in API-only mode ***")
            success = self._initialize_with_api_mode()
            if success:
                return
            else:
                raise ValueError("API-only mode initialization failed. Check your network and access key.")
        
        # Special handling for ARM64
        if IS_ARM64:
            print("\n*** Running on ARM64 Ubuntu - using specialized configuration ***")
            if self._initialize_for_arm64():
                return
            
            # If ARM64 special initialization failed, suggest API mode
            print("\nWake word detection failed on ARM64. Please review UBUNTU_ARM64_SETUP.md")
            print("This is a known issue on some ARM64 systems.")
            print("Consider using API-only mode by setting USE_API_ONLY_MODE=true in your .env file.")
            raise ValueError("ARM64 wake word detection failed")
        
        # Test basic Porcupine functionality first
        self.test_porcupine_installation()
        
        # Get available keywords
        available_keywords = self.list_wake_words()
        
        # Try with primary wake word
        if WAKE_WORD in available_keywords:
            success = self._initialize_with_keyword([WAKE_WORD])
            if success:
                self.active_wake_word = WAKE_WORD
                return
        
        # Try with custom keyword path if available
        if CUSTOM_KEYWORD_PATH and os.path.exists(CUSTOM_KEYWORD_PATH):
            print(f"\nTrying with custom keyword file at: {CUSTOM_KEYWORD_PATH}")
            success = self._initialize_with_keyword_file(CUSTOM_KEYWORD_PATH)
            if success:
                self.active_wake_word = "custom_keyword"
                return
        
        # Try fallback wake words
        print("\nTrying fallback wake words...")
        for fallback_word in FALLBACK_WAKE_WORDS:
            if fallback_word in available_keywords:
                print(f"Trying fallback wake word: {fallback_word}")
                success = self._initialize_with_keyword([fallback_word])
                if success:
                    self.active_wake_word = fallback_word
                    print(f"\n*** Using fallback wake word: '{fallback_word}' ***")
                    print(f"*** Please say '{fallback_word}' instead of '{WAKE_WORD}' ***")
                    return
        
        # If primary wake word is available but failed, retry with delay
        if WAKE_WORD in available_keywords:
            for attempt in range(retry_count):
                print(f"\nRetrying initialization with '{WAKE_WORD}' (attempt {attempt+1}/{retry_count})...")
                time.sleep(1)  # Add delay between attempts
                success = self._initialize_with_keyword([WAKE_WORD])
                if success:
                    self.active_wake_word = WAKE_WORD
                    return
        
        # If everything fails, try one more time with sanitized access key
        print("\nTrying with sanitized access key...")
        sanitized_key = PVPORCUPINE_ACCESS_KEY.strip()
        if self._initialize_with_sanitized_key("porcupine", sanitized_key):
            self.active_wake_word = "porcupine"
            print(f"\n*** Using fallback wake word: 'porcupine' ***")
            print(f"*** Please say 'porcupine' instead of '{WAKE_WORD}' ***")
            return
            
        # If we get here, all initialization attempts failed
        print(f"\nFailed to initialize wake word detector after multiple attempts.")
        print("Please ensure your access key is valid and the wake word is supported.")
        raise ValueError(f"Could not initialize wake word detector with any wake word")
    
    def _initialize_for_arm64(self):
        """Special initialization for ARM64 architecture"""
        try:
            # First try with system libraries if enabled
            if USE_SYSTEM_LIBRARIES:
                print("Trying with system libraries...")
                # Try each fallback keyword
                for keyword in FALLBACK_WAKE_WORDS:
                    try:
                        print(f"Trying ARM64 system initialization with '{keyword}'")
                        self.porcupine = pvporcupine.create(
                            access_key=PVPORCUPINE_ACCESS_KEY,
                            keywords=[keyword],
                            library_path="/usr/local/lib/libpv_porcupine.so"
                        )
                        self._setup_audio_stream()
                        self.active_wake_word = keyword
                        print(f"\n*** ARM64: Using wake word '{keyword}' with system library ***")
                        return True
                    except Exception as e:
                        print(f"ARM64 system library attempt with {keyword} failed: {e}")
            
            # Try with custom model path if provided
            if ARM64_MODEL_PATH and os.path.exists(ARM64_MODEL_PATH):
                print(f"Trying with ARM64 custom model at: {ARM64_MODEL_PATH}")
                self.porcupine = pvporcupine.create(
                    access_key=PVPORCUPINE_ACCESS_KEY,
                    keyword_paths=[ARM64_MODEL_PATH]
                )
                self._setup_audio_stream()
                self.active_wake_word = "custom_arm64"
                print("\n*** Using custom ARM64 model ***")
                return True
                
            return False
        except Exception as e:
            print(f"ARM64 initialization error: {e}")
            return False
    
    def _initialize_with_keyword(self, keywords):
        try:
            print(f"\nInitializing wake word detector with '{keywords[0]}'")
            self.porcupine = pvporcupine.create(
                access_key=PVPORCUPINE_ACCESS_KEY,
                keywords=keywords
            )
            self._setup_audio_stream()
            return True
        except Exception as e:
            print(f"Error initializing with keyword: {e}")
            return False
    
    def _initialize_with_sanitized_key(self, keyword, access_key):
        try:
            print(f"\nInitializing with sanitized key and '{keyword}'")
            self.porcupine = pvporcupine.create(
                access_key=access_key,
                keywords=[keyword]
            )
            self._setup_audio_stream()
            return True
        except Exception as e:
            print(f"Error with sanitized key: {e}")
            return False
            
    def _initialize_with_keyword_file(self, keyword_path):
        try:
            print(f"\nInitializing wake word detector with custom keyword file")
            self.porcupine = pvporcupine.create(
                access_key=PVPORCUPINE_ACCESS_KEY,
                keyword_paths=[keyword_path]
            )
            self._setup_audio_stream()
            return True
        except Exception as e:
            print(f"Error initializing with keyword file: {e}")
            return False
    
    def _initialize_with_api_mode(self):
        """Initialize using cloud-based API processing"""
        try:
            # Try to initialize with API mode with primary wake word
            print(f"\nInitializing API mode with '{WAKE_WORD}'")
            self.porcupine = pvporcupine.create(
                access_key=PVPORCUPINE_ACCESS_KEY,
                keywords=[WAKE_WORD]
            )
            self._setup_audio_stream()
            self.active_wake_word = WAKE_WORD
            print("✓ API-mode initialization successful!")
            return True
        except Exception as e:
            print(f"✗ API-mode initialization failed: {e}")
            
            # Try fallback wake words with API mode
            for fallback_word in FALLBACK_WAKE_WORDS:
                if fallback_word != WAKE_WORD:  # Skip if it's the one we already tried
                    try:
                        print(f"\nTrying API mode with fallback wake word '{fallback_word}'")
                        self.porcupine = pvporcupine.create(
                            access_key=PVPORCUPINE_ACCESS_KEY,
                            keywords=[fallback_word]
                        )
                        self._setup_audio_stream()
                        self.active_wake_word = fallback_word
                        print(f"✓ API mode initialized with '{fallback_word}'")
                        return True
                    except Exception as e2:
                        print(f"✗ API mode with '{fallback_word}' failed: {e2}")
            
            return False
            
    def _setup_audio_stream(self):
        try:
            self.pa = pyaudio.PyAudio()
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                input_device_index=AUDIO_DEVICE_INDEX,
                frames_per_buffer=self.porcupine.frame_length
            )
        except Exception as e:
            print(f"Error setting up audio stream: {e}")
            # Try again without specifying device index
            try:
                print("Retrying with default audio device...")
                self.audio_stream = self.pa.open(
                    rate=self.porcupine.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=self.porcupine.frame_length
                )
            except Exception as e2:
                print(f"Failed to set up audio stream with default device: {e2}")
                raise

    def listen(self):
        try:
            pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
            keyword_index = self.porcupine.process(pcm)
            
            # Only return True if specifically our wake word is detected
            return keyword_index == 0
        except Exception as e:
            print(f"Error in wake word detection: {e}")
            return False
    
    def get_active_wake_word(self):
        """Returns the wake word that was successfully initialized"""
        return self.active_wake_word

    def cleanup(self):
        if self.audio_stream:
            self.audio_stream.close()
        if self.pa:
            self.pa.terminate()
        if self.porcupine:
            self.porcupine.delete()
