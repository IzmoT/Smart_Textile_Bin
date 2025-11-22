# **Firmware: Textile Bin Monitor Unit**

This folder contains the C++ firmware for the Arduino-based monitoring unit.

## **🔌 Hardware Wiring**

The prototype utilizes an **Arduino Uno** with the following pin mapping:

| Component | Pin | Notes |
| :---- | :---- | :---- |
| **HC-SR04 Trig** | 6 | Ultrasonic Sensor Trigger |
| **HC-SR04 Echo** | 5 | Ultrasonic Sensor Echo |
| **DHT11 Data** | 7 | Temperature & Humidity |
| **LED Red** | 8 | Indicator: Bin Full (\< 30cm space) |
| **LED Yellow** | 9 | Indicator: Half Full |
| **LED Green** | 10 | Indicator: Empty (\> 80cm space) |

## **🔋 Power Management Logic**

To ensure suitability for off-grid locations (e.g., forests, collection points), the firmware implements a power-saving strategy:

1. **Wake Up:** System wakes from deep sleep.  
2. **Measure:** Takes 5 samples from ultrasonic sensor to average out noise.  
3. **UX:** Flashes LEDs briefly to indicate status to service personnel.  
4. **Transmit:** Sends JSON-formatted telemetry via Serial (Simulating 4G modem).  
5. **Sleep:** Enters LowPower.powerDown mode for \~1 hour (configurable).

*Note: For the demo version, the sleep cycle is reduced to \~8 seconds.*

## **📦 Dependencies**

* DHT Sensor Library by Adafruit  
* LowPower by Rocket Scream Electronics