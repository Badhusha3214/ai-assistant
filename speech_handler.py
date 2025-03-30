import pyttsx3

class SpeechHandler:
    def __init__(self):
        self.engine = pyttsx3.init()
        
        # Get available voices
        voices = self.engine.getProperty('voices')
        # Select female voice (usually index 1)
        for voice in voices:
            # Look for a female Indian English voice
            if "female" in voice.name.lower() and ("indian" in voice.name.lower() or "en_in" in voice.id.lower()):
                self.engine.setProperty('voice', voice.id)
                break
        
        # Configure voice properties
        self.engine.setProperty('rate', 145)     # Slightly slower for clarity
        self.engine.setProperty('volume', 0.9)   # Volume level
        
    def speak(self, text):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Speech Error: {str(e)}")
            # Fallback to default voice if error occurs
            self.engine.setProperty('voice', self.engine.getProperty('voices')[0].id)
            self.engine.say(text)
            self.engine.runAndWait()
