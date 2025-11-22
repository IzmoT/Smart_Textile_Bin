import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import os
import sys
import glob

# --- PATH CONFIGURATION ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

try:
    from analytics.ai_logistics_agent import generate_logistics_report
except ImportError:
    st.error("Could not import AI Agent. Check folder structure.")
    def generate_logistics_report(ctx): return "Error: Module not found."

# --- APP SETTINGS ---
st.set_page_config(page_title="Bioeconomy IoT Dashboard", layout="wide", page_icon="♻️")
DATA_FOLDER = os.path.join(parent_dir, "edge_gateway", "data")
BIN_DEPTH_CM = 100

# --- DATA LOADING ENGINE ---

@st.cache_data(ttl=60)
def load_data():
    search_pattern = os.path.join(DATA_FOLDER, "sensor_data_*.csv")
    csv_files = glob.glob(search_pattern)
    
    if not csv_files:
        return None, "No Data Found"
    
    try:
        df_list = []
        for file in csv_files:
            df_chunk = pd.read_csv(file)
            df_list.append(df_chunk)
            
        df = pd.concat(df_list, ignore_index=True)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Calculate Fill Level %
        df['fill_level_pct'] = ((BIN_DEPTH_CM - df['distance_cm']) / BIN_DEPTH_CM) * 100
        df['fill_level_pct'] = df['fill_level_pct'].clip(0, 100)
        
        return df, f"Real/Simulated Data ({len(csv_files)} files)"
        
    except Exception as e:
        st.error(f"Error reading data: {e}")
        return None, "Error"

# --- MAIN DASHBOARD UI ---

st.title("♻️ Smart Bioeconomy Logistics Center")
st.markdown("**System Status:** Monitoring textile collection points via IoT & GenAI.")

# 1. Load Data
df, source_name = load_data()

if df is None:
    st.warning("⚠️ No data found. Run 'analytics/generate_mock_data.py' first.")
    st.stop()

st.sidebar.success(f"Connected: {source_name}")

# 2. Global Metrics (Top Row)
# Haetaan viimeisimmät arvot
latest = df.iloc[-1]
current_fill = latest['fill_level_pct']
current_temp = latest['temperature_c']
current_hum = latest['humidity_pct']

# Lasketaan muutos (verrattuna 24h taaksepäin, jos mahdollista)
try:
    yesterday_idx = df[df['timestamp'] < (latest['timestamp'] - timedelta(hours=24))].index[-1]
    fill_delta = current_fill - df.iloc[yesterday_idx]['fill_level_pct']
    temp_delta = current_temp - df.iloc[yesterday_idx]['temperature_c']
except IndexError:
    fill_delta = 0
    temp_delta = 0

# Mittarit ylös
m1, m2, m3, m4 = st.columns(4)
m1.metric("Current Fill Level", f"{current_fill:.1f} %", f"{fill_delta:+.1f}% (24h)")
m2.metric("Status", "CRITICAL" if current_fill > 80 else "Optimal", delta_color="inverse")
m3.metric("Temperature", f"{current_temp:.1f} °C", f"{temp_delta:+.1f} °C (24h)")
m4.metric("Humidity", f"{current_hum:.1f} %")

st.divider()

# --- TABS FOR DIFFERENT VIEWS ---
tab1, tab2, tab3 = st.tabs(["🚛 Logistics & Prediction", "🌡️ Environmental Conditions", "📄 Raw Data"])

# === TAB 1: LOGISTICS (Täyttöaste ja Ennuste) ===
with tab1:
    st.subheader("Fill Level Optimization")
    
    # Regression Logic
    emptied_indices = df[df['fill_level_pct'] < 5].index
    start_idx = emptied_indices[-1] if len(emptied_indices) > 0 else 0
    cycle_data = df.iloc[start_idx:].copy()
    
    if len(cycle_data) > 5:
        start_time = cycle_data['timestamp'].iloc[0]
        cycle_data['days_elapsed'] = (cycle_data['timestamp'] - start_time).dt.total_seconds() / (24 * 3600)
        
        X = cycle_data['days_elapsed'].values.reshape(-1, 1)
        y = cycle_data['fill_level_pct'].values.reshape(-1, 1)
        
        model = LinearRegression()
        model.fit(X, y)
        fill_rate = model.coef_[0][0]
        
        # Plotting
        col_chart, col_ai = st.columns([2, 1])
        
        with col_chart:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.scatter(cycle_data['timestamp'], cycle_data['fill_level_pct'], 
                       color='#1f77b4', s=15, label='Sensor Data', alpha=0.6)
            
            if fill_rate > 0.5:
                days_to_full = (100 - model.intercept_[0]) / fill_rate
                future_days = np.linspace(0, days_to_full + 1, 10)
                future_dates = [start_time + timedelta(days=d) for d in future_days]
                future_fill = model.predict(future_days.reshape(-1, 1))
                ax.plot(future_dates, future_fill, color='#2ca02c', linestyle='--', linewidth=2, label='AI Forecast')
                
                pickup_date = start_time + timedelta(days=days_to_full)
                st.info(f"📅 Predicted Pickup Date: **{pickup_date.strftime('%Y-%m-%d')}**")

            ax.axhline(y=100, color='#d62728', linestyle='-', label='Max Capacity')
            ax.set_ylabel("Fill Level (%)")
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
            
        with col_ai:
            st.markdown("#### 🤖 AI Analysis")
            if st.button("Generate Report", key="btn_logistics"):
                with st.spinner("Consulting AI..."):
                    context = {
                        "current_fill": f"{current_fill:.1f}%",
                        "trend": f"+{fill_rate:.1f}% / day",
                        "prediction_date": pickup_date.strftime('%Y-%m-%d') if fill_rate > 0.5 else "Stable",
                        "temperature": f"{current_temp} C"
                    }
                    report = generate_logistics_report(context)
                    st.session_state['report'] = report
            
            if 'report' in st.session_state:
                st.text_area("Draft:", value=st.session_state['report'], height=250)

# === TAB 2: ENVIRONMENTAL CONDITIONS (Lämpö ja Kosteus) ===
with tab2:
    st.subheader("Condition Monitoring History")
    
    # Valitaan kuinka paljon historiaa näytetään
    days_to_show = st.slider("Show history (days):", 7, 90, 30)
    
    # Suodatetaan data
    cutoff_date = df['timestamp'].max() - timedelta(days=days_to_show)
    hist_data = df[df['timestamp'] > cutoff_date]
    
    # Luodaan kaksi graafia allekkain
    fig2, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))
    
    # Temperature
    ax1.plot(hist_data['timestamp'], hist_data['temperature_c'], color='#ff7f0e', label='Temperature')
    ax1.set_ylabel("Temperature (°C)")
    ax1.axhline(y=25, color='red', linestyle=':', label='Risk Limit (25°C)')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Humidity
    ax2.plot(hist_data['timestamp'], hist_data['humidity_pct'], color='#17becf', label='Humidity')
    ax2.set_ylabel("Humidity (%)")
    ax2.axhline(y=60, color='orange', linestyle=':', label='Risk Limit (60%)')
    ax2.fill_between(hist_data['timestamp'], hist_data['humidity_pct'], alpha=0.1, color='#17becf')
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    plt.xticks(rotation=45)
    st.pyplot(fig2)
    
    # Analyysi
    avg_hum = hist_data['humidity_pct'].mean()
    if avg_hum > 50:
        st.warning(f"⚠️ High average humidity ({avg_hum:.1f}%) detected. Risk of mold growth in textiles.")
    else:
        st.success("✅ Environmental conditions are optimal for textile storage.")

# === TAB 3: RAW DATA ===
with tab3:
    st.subheader("Sensor Data Lake")
    st.dataframe(df.sort_values('timestamp', ascending=False))
    
    # Download button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name='bioeconomy_sensor_data.csv',
        mime='text/csv',
    )