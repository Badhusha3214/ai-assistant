from wake_word_detector import WakeWordDetector
from ai_handler import AIHandler
from speech_handler import SpeechHandler
from config import WAKE_WORD
import time
import speech_recognition as sr

def main():
    # List available wake words before starting
    WakeWordDetector.list_wake_words()
    
    wake_detector = WakeWordDetector()
    ai_handler = AIHandler()
    speech_handler = SpeechHandler()
    recognizer = sr.Recognizer()
    
    print(f"\nSystem ready - Say '{WAKE_WORD}' to start...")
    print("Press Ctrl+C to exit")
    
    try:
        while True:
            wake_word_detected = wake_detector.listen()
            
            if wake_word_detected:
                print(f"\nWake word '{WAKE_WORD}' detected! Listening for command...")
                # Listen for command using speech recognition
                with sr.Microphone() as source:
                    try:
                        audio = recognizer.listen(source, timeout=5)
                        command = recognizer.recognize_google(audio)
                        print(f"Command: {command}")
                        
                        # Filter out wake word from command
                        filtered_command = command.lower().replace(WAKE_WORD, "").strip()
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
            
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        wake_detector.cleanup()

if __name__ == "__main__":
    main()
