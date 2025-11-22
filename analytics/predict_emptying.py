import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from datetime import datetime
import glob
import os

# --- CONFIGURATION ---
# Paths relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REAL_DATA_DIR = os.path.join(BASE_DIR, "..", "edge_gateway", "data")
MOCK_FILE = os.path.join(BASE_DIR, "mock_sensor_history.csv")
BIN_DEPTH_CM = 100 

def load_data_smart():
    """
    Smart loader: Tries to find real data folder first, then falls back to mock file.
    """
    # 1. Try Real Data (Merge all CSVs in folder)
    real_files = glob.glob(os.path.join(REAL_DATA_DIR, "sensor_data_*.csv"))
    
    if real_files:
        print(f"[INFO] Found {len(real_files)} real data files. Merging...")
        try:
            df_list = [pd.read_csv(f) for f in real_files]
            df = pd.concat(df_list, ignore_index=True)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            return df
        except Exception as e:
            print(f"[ERROR] Failed to read real data: {e}")

    # 2. Fallback to Mock
    if os.path.exists(MOCK_FILE):
        print(f"[INFO] Using simulation data: {MOCK_FILE}")
        df = pd.read_csv(MOCK_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    
    return None

def analyze_data(df):
    # Calculate Fill %
    df['fill_level_pct'] = ((BIN_DEPTH_CM - df['distance_cm']) / BIN_DEPTH_CM) * 100
    df['fill_level_pct'] = df['fill_level_pct'].clip(0, 100)
    
    # Identify Current Cycle (Last time < 5%)
    emptied_indices = df[df['fill_level_pct'] < 5].index
    start_idx = emptied_indices[-1] if len(emptied_indices) > 0 else 0
    cycle_data = df.iloc[start_idx:].copy()
    
    # Regression
    start_time = cycle_data['timestamp'].iloc[0]
    cycle_data['days_elapsed'] = (cycle_data['timestamp'] - start_time).dt.total_seconds() / (24 * 3600)
    
    X = cycle_data['days_elapsed'].values.reshape(-1, 1)
    y = cycle_data['fill_level_pct'].values.reshape(-1, 1)
    
    model = LinearRegression()
    model.fit(X, y)
    
    fill_rate = model.coef_[0][0]
    
    print(f"--- ANALYSIS RESULT ---")
    print(f"Current Fill: {y[-1][0]:.1f} %")
    print(f"Fill Rate:    {fill_rate:.1f} % / day")
    
    if fill_rate > 0.1:
        days_to_full = (100 - model.intercept_[0]) / fill_rate
        days_left = days_to_full - cycle_data['days_elapsed'].iloc[-1]
        print(f"Full in:      {days_left:.1f} days")
    else:
        print("Status:       Not filling up.")

if __name__ == "__main__":
    df = load_data_smart()
    if df is not None:
        analyze_data(df)
    else:
        print("[ERROR] No data found.")