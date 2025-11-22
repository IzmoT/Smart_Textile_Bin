# **IoT-Enabled Smart Logistics System for Bioeconomy**

**Status:** Prototype / MVP **Tech Stack:** Arduino (C++), Python, MQTT, Scikit-Learn, GenAI (LLMs), Streamlit

## **🌍 Project Overview**

This project demonstrates a complete **IoT (Internet of Things) solution for optimizing textile recycling logistics**.  
In a circular economy, logistics costs and carbon emissions from collecting recyclable materials are significant bottlenecks. Traditional "fixed-schedule" collection results in trucks visiting empty bins or overflowing bins waiting for days.  
**This solution replaces static schedules with data-driven, predictive on-demand logistics.**

## **🚀 Key Features**

* **Smart Hardware:** Low-power IoT device measuring fill levels and environmental conditions (temp/humidity) to prevent material spoilage.  
* **Edge Gateway:** Decoupled architecture using MQTT and local Data Lake storage (CSV) for robust data handling.  
* **Predictive Analytics:** Linear Regression model that forecasts the exact date a bin will reach capacity.  
* **Generative AI Agent:** An integrated LLM agent (via OpenRouter API) that analyzes sensor trends and drafts actionable email reports for logistics coordinators.  
* **Digital Twin Dashboard:** A real-time Streamlit interface for monitoring assets and operational status.

## **🏗️ System Architecture**

`graph TD`  
    `Sensors[Sensors] -->|Wiring| Arduino[Arduino Uno]`  
    `Arduino -->|Serial/JSON| Gateway[Python Edge Gateway]`  
      
    `Gateway -->|MQTT Protocol| MQTT[MQTT Broker <br/> Cloud/Test]`  
    `Gateway -->|CSV Write| CSV[Local CSV Data Lake]`  
      
    `CSV -->|Read History| Analytics[Analytics Engine <br/> Pandas & Scikit-Learn]`  
      
    `Analytics -->|Prediction| Dashboard[Streamlit Dashboard]`  
      
    `Dashboard -->|Context| AI[GenAI Agent]`  
    `AI -->|Report| Dashboard`

## **📂 Repository Structure**

* **firmware/**: C++ code for Arduino (Sensors, Power Management, JSON serialization).  
* **edge\_gateway/**: Python script acting as a bridge between Hardware and Cloud/Storage.  
* **analytics/**: Data simulation tools, Predictive Models, and AI Agent logic.  
* **dashboard/**: The user interface (Streamlit web app).

## **⚡ Quick Start**

### **1\. Prerequisites**

* Python 3.8+  
* Arduino IDE (for flashing firmware)  
* (Optional) OpenRouter API Key for AI features

### **2\. Installation**

`# Clone repository`  
`git clone <repository-url>`  
`cd Textile_Bin`

`# Install dependencies`  
`pip install pandas numpy matplotlib scikit-learn pyserial paho-mqtt streamlit openai`

### **3\. Running the Demo (Simulation Mode)**

You can run the full system without hardware using the built-in data generator.

1. **Generate historical data:**  
   `python analytics/generate_mock_data.py`

2. **Launch the Dashboard:**  
   `streamlit run dashboard/dashboard_app.py`

### **4\. Running with Hardware**

1. Connect Arduino via USB.  
2. Update SERIAL\_PORT in edge\_gateway/gateway.py.  
3. Run python edge\_gateway/gateway.py.  
4. The dashboard will automatically detect live data.

## **🧠 Design Philosophy**

This project emphasizes **resource efficiency** both in hardware (Sleep modes) and software (modular architecture). It demonstrates how modern AI tools can be integrated into industrial processes to support human decision-making rather than replacing it.