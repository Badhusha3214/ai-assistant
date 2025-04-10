import serial
import time
import threading
import queue
import re

class ServoInterface:
    def __init__(self, port="/dev/ttyACM0", baud_rate=9600):
        """Initialize servo interface with Arduino"""
        self.port = port
        self.baud_rate = baud_rate
        self.serial_conn = None
        self.connected = False
        self.command_queue = queue.Queue()
        self.motion_patterns = {
            "greeting": self._pattern_greeting,
            "thinking": self._pattern_thinking,
            "listening": self._pattern_listening,
            "confused": self._pattern_confused
        }
        
    def connect(self):
        """Attempt to connect to the Arduino"""
        try:
            self.serial_conn = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            self.connected = True
            print(f"Connected to Arduino on {self.port}")
            
            # Start command processing thread
            self.running = True
            self.command_thread = threading.Thread(target=self._process_command_queue)
            self.command_thread.daemon = True
            self.command_thread.start()
            
            return True
        except Exception as e:
            print(f"Failed to connect to Arduino: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from Arduino"""
        if self.connected:
            self.running = False
            time.sleep(0.5)
            self.serial_conn.close()
            self.connected = False
            print("Disconnected from Arduino")
    
    def rotate_horizontal(self, angle):
        """Rotate servo horizontally to specified angle"""
        if not self.connected:
            print("Not connected to Arduino")
            return
        
        try:
            angle = int(angle)
            if 0 <= angle <= 180:
                self.command_queue.put(f"rotate:H,{angle}")
            else:
                print("Horizontal angle must be between 0 and 180 degrees")
        except ValueError:
            print("Angle must be a number")
    
    def rotate_vertical(self, angle):
        """Rotate servo vertically to specified angle"""
        if not self.connected:
            print("Not connected to Arduino")
            return
        
        try:
            angle = int(angle)
            if 45 <= angle <= 135:
                self.command_queue.put(f"rotate:V,{angle}")
            else:
                print("Vertical angle must be between 45 and 135 degrees")
        except ValueError:
            print("Angle must be a number")
    
    def scan(self):
        """Perform scanning motion"""
        if self.connected:
            self.command_queue.put("scan")
    
    def center(self):
        """Move to center position"""
        if self.connected:
            self.command_queue.put("center")
    
    def nod(self):
        """Perform nodding motion"""
        if self.connected:
            self.command_queue.put("nod")
    
    def motion_pattern(self, pattern_name):
        """Execute a predefined motion pattern"""
        if not self.connected:
            print("Not connected to Arduino")
            return
            
        if pattern_name in self.motion_patterns:
            self.motion_patterns[pattern_name]()
        else:
            print(f"Unknown motion pattern: {pattern_name}")
    
    def _pattern_greeting(self):
        """Execute greeting motion pattern"""
        self.command_queue.put("center")
        time.sleep(0.5)
        self.command_queue.put("nod")
    
    def _pattern_thinking(self):
        """Execute thinking motion pattern"""
        self.rotate_horizontal(60)
        time.sleep(0.5)
        self.rotate_horizontal(120)
        time.sleep(0.5)
        self.rotate_horizontal(90)
    
    def _pattern_listening(self):
        """Execute listening motion pattern"""
        self.rotate_vertical(80)
        time.sleep(0.2)
        self.rotate_vertical(100)
        time.sleep(0.2)
        self.rotate_vertical(90)
    
    def _pattern_confused(self):
        """Execute confused motion pattern"""
        self.rotate_horizontal(70)
        time.sleep(0.3)
        self.rotate_horizontal(110)
        time.sleep(0.3)
        self.rotate_horizontal(90)
        self.nod()
    
    def react_to_emotions(self, text):
        """React to emotions in text with appropriate motions"""
        text = text.lower()
        
        if re.search(r"(hello|hi|greet|welcome)", text):
            self.motion_pattern("greeting")
        elif re.search(r"(hmm|let me think|thinking|consider)", text):
            self.motion_pattern("thinking")
        elif re.search(r"(not sure|don't know|confused|unclear)", text):
            self.motion_pattern("confused")
    
    def _process_command_queue(self):
        """Process command queue in background thread"""
        while self.running:
            try:
                if not self.command_queue.empty():
                    command = self.command_queue.get()
                    self._send_command(command)
                    self.command_queue.task_done()
                time.sleep(0.1)
            except Exception as e:
                print(f"Error processing command: {e}")
    
    def _send_command(self, command):
        """Send command to Arduino"""
        try:
            self.serial_conn.write(f"{command}\n".encode())
            time.sleep(0.1)
            
            # Read response from Arduino
            response = self.serial_conn.readline().decode().strip()
            if response:
                print(f"Arduino: {response}")
        except Exception as e:
            print(f"Error sending command: {e}")
            self.connected = False

# Example usage
if __name__ == "__main__":
    # For Windows: typically COM3, COM4, etc.
    # For Linux/Mac: typically /dev/ttyACM0 or /dev/ttyUSB0
    servo = ServoInterface(port="COM3")  # Change to your Arduino port
    
    if servo.connect():
        try:
            print("Testing servo movements...")
            servo.center()
            time.sleep(1)
            servo.scan()
            time.sleep(2)
            servo.nod()
            time.sleep(1)
            
            print("Testing motion patterns...")
            servo.motion_pattern("greeting")
            time.sleep(2)
            servo.motion_pattern("thinking")
            time.sleep(2)
            
            print("Returning to center position...")
            servo.center()
        finally:
            servo.disconnect()
    else:
        print("Failed to connect to Arduino. Please check the port and connection.")
