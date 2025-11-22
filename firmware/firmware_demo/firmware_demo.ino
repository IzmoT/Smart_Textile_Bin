/*
 * Bioeconomy IoT Project: Textile Bin Monitor (TEST / DEMO VERSION)
 * * CHANGES FOR DEMO:
 * - Sleep time reduced from 1 hour to ~8 seconds.
 * - Allows rapid testing of sensor logic and connectivity.
 * * Hardware:
 * - Arduino Uno
 * - HC-SR04 Ultrasonic Sensor
 * - DHT11 Temperature & Humidity Sensor
 * - 3x LEDs (Green, Yellow, Red)
 */

#include <DHT.h>
#include "LowPower.h" // Ensure this library is installed via Library Manager

// --- Configuration ---
#define DHTPIN 7
#define DHTTYPE DHT11
#define TRIGGER_PIN 6
#define ECHO_PIN 5
#define LED_GREEN 10
#define LED_YELLOW 9
#define LED_RED 8

// --- DEMO SETTING ---
// In production, this would be 450 (approx 1 hour).
// For testing, we use 1 (approx 8 seconds).
const int SLEEP_CYCLES = 1; 

DHT dht(DHTPIN, DHTTYPE);

// Function to read distance from ultrasonic sensor
long readUltrasonicDistance(int triggerPin, int echoPin) {
  pinMode(triggerPin, OUTPUT);
  digitalWrite(triggerPin, LOW);
  delayMicroseconds(2);
  digitalWrite(triggerPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(triggerPin, LOW);
  pinMode(echoPin, INPUT);
  return pulseIn(echoPin, HIGH);
}

void setup() {
  // Initialize Serial for debugging and data transmission
  Serial.begin(9600);
  
  // Initialize LEDs
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  
  // Initialize DHT Sensor
  dht.begin();
  
  Serial.println("--- SYSTEM STARTUP (DEMO MODE) ---");
  delay(1000);
}

void loop() {
  // ==================================================
  // PHASE 1: WAKE UP & MEASURE
  // ==================================================
  
  // 1. Measure Distance (Fill Level)
  long totalDuration = 0;
  int validReadings = 0;
  
  // Take 3 samples for the demo (faster than 5 or 10)
  for (int i = 0; i < 3; i++) {
    long duration = readUltrasonicDistance(TRIGGER_PIN, ECHO_PIN);
    if (duration > 0) {
      totalDuration += duration;
      validReadings++;
    }
    delay(30);
  }
  
  float avgDistance = 0;
  if (validReadings > 0) {
    // Calculate cm: duration * 0.034 / 2 (or 0.01723)
    avgDistance = 0.01723 * (totalDuration / (float)validReadings);
  }

  // 2. Measure Environment
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  // Handle sensor errors (e.g., if DHT is disconnected)
  if (isnan(humidity) || isnan(temperature)) {
    humidity = 0.0;
    temperature = 0.0;
  }

  // ==================================================
  // PHASE 2: VISUAL FEEDBACK (Traffic Lights)
  // ==================================================
  
  // Reset LEDs first
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);

  // Logic: 
  // > 80cm = Empty (Green)
  // 30-80cm = Half-full (Yellow)
  // < 30cm = Full (Red)
  // Note: You can adjust these values for your desk testing environment.
  if (avgDistance > 80) {
    digitalWrite(LED_GREEN, HIGH); 
  } else if (avgDistance > 30 && avgDistance <= 80) {
    digitalWrite(LED_YELLOW, HIGH); 
  } else {
    digitalWrite(LED_RED, HIGH); 
  }

  // ==================================================
  // PHASE 3: DATA TRANSMISSION (JSON)
  // ==================================================
  
  // Create a JSON-formatted string
  Serial.print("{\"distance_cm\": ");
  Serial.print(avgDistance);
  Serial.print(", \"temperature_c\": ");
  Serial.print(temperature);
  Serial.print(", \"humidity_pct\": ");
  Serial.print(humidity);
  Serial.println("}");

  // IMPORTANT: Wait for Serial data to be fully transmitted 
  // before putting the processor to sleep.
  delay(500); 

  // ==================================================
  // PHASE 4: POWER SAVING (DEMO SLEEP)
  // ==================================================
  
  // Turn OFF LEDs to simulate power saving mode
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);

  // Sleep for the configured amount of cycles
  // In this demo: 1 cycle * 8s = ~8 seconds sleep
  for (int i = 0; i < SLEEP_CYCLES; i++) {
    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);  
  }
  
  // After waking up, the loop starts again from the top.
}