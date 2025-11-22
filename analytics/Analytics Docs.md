# **Analytics & AI Agent**

This module handles the intelligence layer of the IoT system.

## **📊 Predictive Modeling**

* **File:** predict\_emptying.py (Logic embedded in Dashboard)  
* **Method:** Uses **Linear Regression** (Scikit-Learn) to calculate the fill rate (% per day) based on the current filling cycle.  
* **Goal:** To predict the exact date when the bin will reach 100% capacity, allowing for Just-In-Time logistics.

## **🤖 AI Logistics Agent**

* **File:** ai\_logistics\_agent.py  
* **Function:** Acts as a "Virtual Assistant" for the logistics coordinator.  
* **Tech:** Uses **LLM APIs** (via OpenRouter/OpenAI).  
* **Workflow:**  
  1. Receives statistical context (Current fill, Trend, Temp).  
  2. Constructs a prompt with a specific persona ("Logistics Expert").  
  3. Generates a concise, human-readable email draft suggesting actions (e.g., "Schedule pickup tomorrow due to rapid filling").

## **🎲 Data Simulation**

* **File:** generate\_mock\_data.py  
* **Purpose:** Generates realistic historical CSV data for testing the dashboard without waiting months for real sensor data.  
* **Features:** Simulates weekly patterns (higher filling rates on weekends) and environmental fluctuations.