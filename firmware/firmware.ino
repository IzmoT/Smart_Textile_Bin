/*
 * Bioeconomy IoT Project: Textile Bin Monitor (Low Power Version)
 * * Hardware:
 * - Arduino Uno
 * - HC-SR04 Ultrasonic Sensor
 * - DHT11 Temperature & Humidity Sensor
 * - 3x LEDs (Green, Yellow, Red)
 * * Logic:
 * 1. Wake up from deep sleep.
 * 2. Measure fill level and environment data.
 * 3. Show status via LEDs briefly (Visual feedback).
 * 4. Send data via Serial (JSON) to Edge Gateway.
 * 5. Turn off peripherals to save power.
 * 6. Sleep for 1 hour.
 * * Libraries required: 
 * - DHT Sensor Library
 * - LowPower (by Rocket Scream)
 */

#include <DHT.h>
#include "LowPower.h" // Requires "LowPower" library install

// --- Configuration ---
#define DHTPIN 7
#define DHTTYPE DHT11
#define TRIGGER_PIN 6
#define ECHO_PIN 5
#define LED_GREEN 10
#define LED_YELLOW 9
#define LED_RED 8

// Constants
const int SLEEP_CYCLES_PER_HOUR = 450; // 8s * 450 = 3600s = 1 hour

DHT dht(DHTPIN, DHTTYPE);

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
  // Initialize Serial for Edge Gateway communication
  Serial.begin(9600);
  
  // Initialize IO
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  
  // Initialize Sensors
  dht.begin();
  
  // Wait a moment for sensors to stabilize
  delay(2000);
}

void loop() {
  // --- PHASE 1: WAKE UP & MEASURE ---
  
  // 1. Measure Distance (Fill Level)
  long totalDuration = 0;
  int validReadings = 0;
  
  // Take 5 samples to avoid noise
  for (int i = 0; i < 5; i++) {
    long duration = readUltrasonicDistance(TRIGGER_PIN, ECHO_PIN);
    if (duration > 0) {
      totalDuration += duration;
      validReadings++;
    }
    delay(50);
  }
  
  float avgDistance = 0;
  if (validReadings > 0) {
    // 0.01723 = Speed of sound correction factor (cm/microsecond / 2)
    avgDistance = 0.01723 * (totalDuration / (float)validReadings);
  }

  // 2. Measure Environment
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  // Check if DHT reading failed
  if (isnan(humidity) || isnan(temperature)) {
    humidity = 0.0;
    temperature = 0.0;
  }

  // --- PHASE 2: VISUAL FEEDBACK (Traffic Lights) ---
  
  // Reset LEDs
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);

  // Logic: Less distance = More full
  // Thresholds: Empty > 80cm, Full < 30cm
  if (avgDistance > 80) {
    digitalWrite(LED_GREEN, HIGH); // Bin is Empty
  } else if (avgDistance > 30 && avgDistance <= 80) {
    digitalWrite(LED_YELLOW, HIGH); // Bin is Half-full
  } else {
    digitalWrite(LED_RED, HIGH); // Bin is Full
  }

  // --- PHASE 3: DATA TRANSMISSION ---
  
  // Send JSON object to Python Gateway
  // Format: {"d": distance, "t": temp, "h": hum}
  Serial.print("{\"distance_cm\": ");
  Serial.print(avgDistance);
  Serial.print(", \"temperature_c\": ");
  Serial.print(temperature);
  Serial.print(", \"humidity_pct\": ");
  Serial.print(humidity);
  Serial.println("}");

  // Use a short delay to ensure Serial buffer is flushed (sent out) 
  // before going to sleep.
  delay(1000); 

  // --- PHASE 4: PREPARE FOR SLEEP ---
  
  // Turn OFF all LEDs to save battery during the 1-hour sleep
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);

  // --- PHASE 5: DEEP SLEEP ---
  
  // The ATmega328P watchdog timer maxes out at 8 seconds.
  // To sleep for 1 hour (3600s), we need to loop: 3600 / 8 = 450 times.
  
  // For demonstration purposes (so you don't wait an hour while testing), 
  // change this loop to e.g., 4 cycles (32 seconds).
  
  for (int i = 0; i < SLEEP_CYCLES_PER_HOUR; i++) {
    // Power Down is the most energy efficient mode
    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);  
  }
}