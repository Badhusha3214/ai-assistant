#include <Servo.h>

// Define servo pins
#define SERVO_PIN_HORIZONTAL 9
#define SERVO_PIN_VERTICAL 10

// Create servo objects
Servo horizontalServo;
Servo verticalServo;

// Define motion constraints
const int MIN_ANGLE_HORIZONTAL = 0;
const int MAX_ANGLE_HORIZONTAL = 180;
const int MIN_ANGLE_VERTICAL = 45;
const int MAX_ANGLE_VERTICAL = 135;

// Current position tracking
int currentHorizontalAngle = 90; // Center position
int currentVerticalAngle = 90;   // Center position
int smoothingFactor = 5;         // Lower = smoother but slower

// Command processing
String inputString = "";
bool stringComplete = false;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Initialize servo motors
  horizontalServo.attach(SERVO_PIN_HORIZONTAL);
  verticalServo.attach(SERVO_PIN_VERTICAL);
  
  // Move to center position
  horizontalServo.write(currentHorizontalAngle);
  verticalServo.write(currentVerticalAngle);
  
  // Print welcome message
  Serial.println("AI Assistant Servo Controller");
  Serial.println("Available commands:");
  Serial.println("- rotate:H,angle (0-180 degrees)");
  Serial.println("- rotate:V,angle (45-135 degrees)");
  Serial.println("- scan (performs scanning motion)");
  Serial.println("- center (moves to center position)");
  Serial.println("- nod (performs nodding motion)");
}

void loop() {
  // Process serial commands
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;
    
    // Process when newline is received
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
  
  // Process complete commands
  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
}

void processCommand(String command) {
  command.trim();
  
  if (command.startsWith("rotate:H,")) {
    // Horizontal rotation command
    int angle = command.substring(9).toInt();
    rotateHorizontal(angle);
  } 
  else if (command.startsWith("rotate:V,")) {
    // Vertical rotation command
    int angle = command.substring(9).toInt();
    rotateVertical(angle);
  }
  else if (command == "scan") {
    // Perform scanning motion
    performScan();
  }
  else if (command == "center") {
    // Return to center position
    moveToCenter();
  }
  else if (command == "nod") {
    // Perform nodding motion
    performNod();
  }
  else {
    Serial.println("Unknown command: " + command);
  }
}

void rotateHorizontal(int targetAngle) {
  // Constrain target angle to valid range
  targetAngle = constrain(targetAngle, MIN_ANGLE_HORIZONTAL, MAX_ANGLE_HORIZONTAL);
  
  // Smoothly move to target angle
  while (abs(currentHorizontalAngle - targetAngle) > 1) {
    if (currentHorizontalAngle < targetAngle) {
      currentHorizontalAngle += 1;
    } else {
      currentHorizontalAngle -= 1;
    }
    
    horizontalServo.write(currentHorizontalAngle);
    delay(smoothingFactor);
  }
  
  Serial.println("Horizontal position: " + String(currentHorizontalAngle));
}

void rotateVertical(int targetAngle) {
  // Constrain target angle to valid range
  targetAngle = constrain(targetAngle, MIN_ANGLE_VERTICAL, MAX_ANGLE_VERTICAL);
  
  // Smoothly move to target angle
  while (abs(currentVerticalAngle - targetAngle) > 1) {
    if (currentVerticalAngle < targetAngle) {
      currentVerticalAngle += 1;
    } else {
      currentVerticalAngle -= 1;
    }
    
    verticalServo.write(currentVerticalAngle);
    delay(smoothingFactor);
  }
  
  Serial.println("Vertical position: " + String(currentVerticalAngle));
}

void performScan() {
  Serial.println("Scanning surroundings...");
  
  // Move from left to right
  rotateHorizontal(MIN_ANGLE_HORIZONTAL + 10);
  delay(500);
  rotateHorizontal(MAX_ANGLE_HORIZONTAL - 10);
  delay(500);
  
  // Return to center
  rotateHorizontal(90);
  
  Serial.println("Scan complete");
}

void moveToCenter() {
  Serial.println("Moving to center position...");
  rotateHorizontal(90);
  rotateVertical(90);
  Serial.println("Centered");
}

void performNod() {
  Serial.println("Nodding...");
  
  // Save current vertical position
  int originalVertical = currentVerticalAngle;
  
  // Perform nodding motion
  rotateVertical(originalVertical + 15);
  delay(300);
  rotateVertical(originalVertical - 15);
  delay(300);
  rotateVertical(originalVertical);
  
  Serial.println("Nod complete");
}
