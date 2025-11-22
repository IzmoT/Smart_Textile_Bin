import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# --- CONFIGURATION ---
# Generoidaan dataa tähän kansioon, jotta dashboard löytää sen helposti
OUTPUT_DIR = "../edge_gateway/data" 
FILE_PREFIX = "sensor_data_" # Käytetään samaa etuliitettä kuin oikea gateway
DAYS_TO_SIMULATE = 90 # Simuloidaan 3 kuukautta (tulee useampi tiedosto)
BIN_DEPTH_CM = 100

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"[INFO] Created directory: {directory}")

def generate_synthetic_data():
    """
    Generates synthetic sensor data spanning multiple months.
    Saves data into separate monthly CSV files (just like the real Gateway).
    """
    np.random.seed(42)
    ensure_directory_exists(OUTPUT_DIR)
    
    # 1. Generate timestamps
    end_date = datetime.now()
    start_date = end_date - timedelta(days=DAYS_TO_SIMULATE)
    timestamps = [start_date + timedelta(hours=i) for i in range(DAYS_TO_SIMULATE * 24)]
    
    # 2. Generate data points
    data = []
    current_fill_pct = 0
    
    print(f"[INFO] Generating {len(timestamps)} data points...")

    for ts in timestamps:
        # Simulation logic (same as before)
        hourly_deposit = np.random.uniform(0.1, 0.3) 
        if ts.weekday() >= 5: 
            hourly_deposit *= 2.5
            
        current_fill_pct += hourly_deposit
        
        if current_fill_pct >= 100:
            current_fill_pct = 0 
            
        distance_cm = BIN_DEPTH_CM - (current_fill_pct / 100 * BIN_DEPTH_CM)
        distance_cm += np.random.uniform(-1, 1)
        
        data.append({
            "timestamp": ts, # Keep as object for grouping
            "distance_cm": round(distance_cm, 1),
            "temperature_c": round(np.random.uniform(15, 25), 1), 
            "humidity_pct": round(np.random.uniform(40, 60), 1)
        })
        
    # 3. Split into monthly files
    df_all = pd.DataFrame(data)
    
    # Create a grouping key (Year-Month)
    df_all['month_group'] = df_all['timestamp'].dt.strftime('%Y-%m')
    
    # Loop through groups and save files
    for month, group_df in df_all.groupby('month_group'):
        # Drop helper column
        save_df = group_df.drop(columns=['month_group'])
        
        # Format timestamp back to string for CSV
        save_df['timestamp'] = save_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        filename = f"{FILE_PREFIX}{month}.csv"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        save_df.to_csv(filepath, index=False)
        print(f"[SUCCESS] Saved {len(save_df)} rows to: {filepath}")

if __name__ == "__main__":
    generate_synthetic_data()