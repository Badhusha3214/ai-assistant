import pvporcupine
import struct
import pyaudio
from config import PVPORCUPINE_ACCESS_KEY, WAKE_WORD

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

    def __init__(self):
        available_keywords = self.list_wake_words()
        if WAKE_WORD not in available_keywords:
            print(f"\nWarning: '{WAKE_WORD}' is not in available keywords!")
            print("Please choose from the available keywords above.")
            raise ValueError(f"Invalid wake word: {WAKE_WORD}")
        
        print(f"\nInitializing wake word detector with '{WAKE_WORD}'")
        self.porcupine = pvporcupine.create(
            access_key=PVPORCUPINE_ACCESS_KEY,
            keywords=[WAKE_WORD]
        )
        self.pa = pyaudio.PyAudio()
        self.audio_stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

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

    def cleanup(self):
        self.audio_stream.close()
        self.pa.terminate()
        self.porcupine.delete()
