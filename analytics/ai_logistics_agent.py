import os
import sys
from openai import OpenAI

# ==========================================
# CONFIGURATION
# ==========================================

# Valitse palveluntarjoaja: "openrouter" (Oikea AI) tai "mock" (Simulaatio)
PROVIDER = "openrouter" 

# Aseta OpenRouter API-avaimesi tähän (tai käytä ympäristömuuttujaa)
# SUOSITUS: Älä jätä avainta koodiin jos laitat sen GitHubiin!
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "LIITA_SINUN_OPENROUTER_KEY_TAHAN")

# Mallin valinta (Käytetään ilmaista/halpaa mallia)
# "google/gemini-2.0-flash-exp:free" on usein ilmainen ja erittäin nopea
MODEL_ID = "google/gemini-2.0-flash-exp:free" 

# ==========================================
# AI CLIENT FACTORY
# ==========================================

def get_ai_client():
    """
    Luo yhteyden OpenRouterin rajapintaan.
    """
    if PROVIDER == "openrouter":
        if not OPENROUTER_API_KEY or "LIITA_SINUN" in OPENROUTER_API_KEY:
            print("[ERROR] OpenRouter API key is missing!")
            return None
            
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
    return None

# ==========================================
# LOGIC
# ==========================================

def generate_logistics_report(context):
    """
    Generates a professional logistics email based on sensor data.
    
    Args:
        context (dict): Contains 'current_fill', 'trend', 'prediction_date'
    Returns:
        str: The generated email draft.
    """
    
    # 1. Määritellään rooli ja tehtävä (System Prompt)
    system_prompt = """
    You are 'EcoLogistics AI', an expert logistics coordinator for a circular economy company.
    Your job is to analyze sensor data from textile bins and write short, actionable emails to the driver team.
    Keep the tone professional, efficient, and operational.
    """
    
    # 2. Syötetään data ja ohjeet (User Prompt)
    user_prompt = f"""
    Please draft a status email based on this sensor data:

    --- SENSOR DATA ---
    Bin ID:           #TX-105 (Location: K-Market Loimaa)
    Current Level:    {context.get('current_fill', 'N/A')}
    7-Day Trend:      {context.get('trend', 'Stable')}
    Est. Full Date:   {context.get('prediction_date', 'Unknown')}
    Temperature:      {context.get('temperature', 'N/A')}
    -------------------
    
    INSTRUCTIONS:
    - If level > 80%: Mark subject as [URGENT].
    - If level < 50%: Mark subject as [LOW PRIORITY] and suggest skipping.
    - If temperature > 25C: Warn about potential hygiene risks (mold/odors).
    - Clearly state the recommended action (Pickup tomorrow / Skip / Monitor).
    - Keep it under 100 words.
    """
    
    print(f"[AI AGENT] Connecting to OpenRouter ({MODEL_ID})...")

    # 3. Mock Response (Varajärjestelmä, jos netti ei toimi)
    if PROVIDER == "mock":
        return f"""
        [MOCK RESPONSE]
        Subject: Status Update Bin #TX-105
        Bin is at {context.get('current_fill')}. Trend is {context.get('trend')}.
        Recommended action: Pickup on {context.get('prediction_date')}.
        """

    # 4. Oikea API-kutsu
    client = get_ai_client()
    if not client:
        return "[ERROR] Could not initialize AI client. Check API Key."

    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            # headers={"HTTP-Referer": "http://localhost:8501", "X-Title": "Bioeconomy IoT"},
        )
        return response.choices[0].message.content
        
    except Exception as e:
        return f"[ERROR] AI Generation failed: {e}"

# ==========================================
# TESTIAJO (Jos ajetaan suoraan tätä tiedostoa)
# ==========================================
if __name__ == "__main__":
    # Testikonteksti
    test_context = {
        "current_fill": "85.5%",
        "trend": "+12% / day",
        "prediction_date": "2025-10-25",
        "temperature": "18.5 C"
    }
    
    print("--- TESTING AI AGENT ---")
    report = generate_logistics_report(test_context)
    print("\n--- GENERATED REPORT ---\n")
    print(report)