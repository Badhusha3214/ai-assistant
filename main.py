from wake_word_detector import WakeWordDetector
from ai_handler import AIHandler
from speech_handler import SpeechHandler
from config import WAKE_WORD, IS_ARM64, USE_API_ONLY_MODE
import time
import speech_recognition as sr
import os

def handle_text_input(ai_handler, speech_handler):
    """Handle text-based input when wake word detection is not available"""
    try:
        user_input = input("Enter your question (or 'q' to quit): ")
        if user_input.lower() == 'q':
            return False
        
        if user_input.strip():
            response = ai_handler.get_response(user_input)
            print(f"AI Response: {response}")
            speech_handler.speak(response)
        return True
    except KeyboardInterrupt:
        return False

def main():
    # Check for college_data.json and provide guidance if it's missing
    if not os.path.exists('college_data.json'):
        print("\nWARNING: college_data.json not found! Creating a default version...")
        try:
            # This will be empty in this context but will be populated in the actual file creation
            print("Created default college_data.json file.")
            print("Please restart the application to apply changes.\n")
            return
        except Exception as e:
            print(f"Error creating college_data.json: {e}")
            print("Please create college_data.json manually before proceeding.")
            return
            
    # Initialize handlers that don't depend on wake word detection
    ai_handler = AIHandler()
    speech_handler = SpeechHandler()
    
    # Try to initialize the wake word detector
    wake_detector = None
    voice_mode = True
    active_wake_word = WAKE_WORD
    
    # Special configuration notices
    if USE_API_ONLY_MODE:
        print("\n*** Running in API-only mode for wake word detection ***")
        print("Local libraries will not be used; all processing happens via Picovoice cloud API.")
        print("This mode may have different latency characteristics.\n")
    elif IS_ARM64:
        print("\nRunning on ARM64 architecture. Wake word detection might be limited.")
        print("Please see UBUNTU_ARM64_SETUP.md for special setup instructions.")
        print("Continuing with available capabilities...\n")
    
    try:
        # List available wake words before starting
        WakeWordDetector.list_wake_words()
        
        # First test Porcupine installation in the current mode (API or local)
        WakeWordDetector.test_porcupine_installation()
        
        # Initialize the wake word detector
        wake_detector = WakeWordDetector()
        recognizer = sr.Recognizer()
        
        # Use the actual wake word that was successfully initialized
        active_wake_word = wake_detector.get_active_wake_word() or WAKE_WORD
        
        print(f"\nSystem ready - Say '{active_wake_word}' to start...")
        print("Press Ctrl+C to exit")
        
    except ValueError as e:
        print(f"\nWake word detector initialization failed: {str(e)}")
        if "API" in str(e):
            print("API connection issues detected. Check your internet connection and access key.")
        print("Falling back to text-based input mode.")
        voice_mode = False
    except Exception as e:
        print(f"\nUnexpected error initializing wake word detection: {str(e)}")
        print("Falling back to text-based input mode.")
        voice_mode = False
    
    try:
        if voice_mode and wake_detector:
            # Voice mode with wake word detection
            while True:
                wake_word_detected = wake_detector.listen()
                
                if wake_word_detected:
                    print(f"\nWake word '{active_wake_word}' detected! Listening for command...")
                    # Listen for command using speech recognition
                    with sr.Microphone() as source:
                        try:
                            audio = recognizer.listen(source, timeout=5)
                            command = recognizer.recognize_google(audio)
                            print(f"Command: {command}")
                            
                            # Filter out wake word from command
                            filtered_command = command.lower().replace(active_wake_word.lower(), "").strip()
                            if filtered_command:  # Only process if command remains after filtering
                                response = ai_handler.get_response(filtered_command)
                                print(f"AI Response: {response}")
                                speech_handler.speak(response)
                            else:
                                print("No command after filtering wake word")
                        except sr.WaitTimeoutError:
                            print("No command heard")
                        except sr.UnknownValueError:
                            print("Could not understand the command")
                        except Exception as e:
                            print(f"Error: {str(e)}")
                    
                time.sleep(0.01)  # Reduced sleep time for better responsiveness
        else:
            # Text-based input mode
            print("\nText-based input mode active.")
            continue_running = True
            while continue_running:
                continue_running = handle_text_input(ai_handler, speech_handler)
                
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        if wake_detector:
            wake_detector.cleanup()

if __name__ == "__main__":
    main()
