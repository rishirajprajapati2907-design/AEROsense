"""
AEROsense Settings & System Preferences Page
Profile preferences, theme settings, ThingSpeak REST configuration,
dataset management, and hardware calibration offsets.
"""

import os
import streamlit as st
from config import DEFAULT_CHANNEL_ID, DEFAULT_CHANNEL_NAME, DEFAULT_READ_API_KEY
from services.authentication import get_current_user


def render_settings_page(hist_meta: dict):
    """Render the application settings and preferences page."""
    current_user = get_current_user()

    st.markdown("## ⚙️ System Settings & Platform Preferences")
    st.caption("Manage authentication profiles, cloud IoT integrations, data archives, and sensor calibration offsets.")

    tab_profile, tab_iot, tab_data, tab_calib = st.tabs([
        "👤 Operator Profile",
        "☁️ ThingSpeak REST API",
        "📂 Dataset Management",
        "🔧 Hardware Calibration",
    ])

    with tab_profile:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("#### Operator Profile Details")
        st.write(f"**Name:** {current_user.get('name')}")
        st.write(f"**Email:** {current_user.get('email')}")
        st.write(f"**Role:** {current_user.get('role')}")
        st.write(f"**Account Type:** {'Demonstration / Guest' if current_user.get('is_guest') else 'Verified Operator'}")
        
        st.markdown("---")
        st.markdown("#### Theme Preferences")
        st.selectbox("UI Theme:", ["60-30-10 MODERN SAAS (Active)", "DEEP CHARCOAL & LIME", "HIGH-CONTRAST DARK"], index=0)
        st.caption("Color tokens: #101820 (60% Main Charcoal), #E8EDEB (30% Secondary Off-White), #B7F34A (10% Electric Lime Accent).")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_iot:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("#### ThingSpeak Cloud Telemetry Configuration")
        st.write(f"**Channel Name:** `{DEFAULT_CHANNEL_NAME}`")
        st.write(f"**Target Channel ID:** `{DEFAULT_CHANNEL_ID}`")
        st.write(f"**Access Privilege:** `PRIVATE`")
        
        env_key = os.environ.get("THINGSPEAK_READ_API_KEY", "") or DEFAULT_READ_API_KEY
        masked_key = ("*" * 12 + env_key[-4:]) if len(env_key) >= 4 else "Not Set (Using .env)"
        st.write(f"**Read API Key:** `{masked_key}`")
        st.caption("Credentials loaded securely via environment variables (.env) or Streamlit Secrets. Never exposed in frontend code.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_data:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("#### Historical Spreadsheet Management")
        st.write(f"**Target File Path:** `{hist_meta.get('file_path', 'data/aerosense_historical_data.xlsx')}`")
        st.write(f"**Verified Records Loaded:** `{hist_meta.get('total_records', 5024):,}`")
        st.write(f"**Time Horizon:** `{hist_meta.get('span_days', 15)} Days`")
        
        # File uploader to swap or update historical dataset
        uploaded_file = st.file_uploader("Upload Updated Historical Sensor Spreadsheet (.xlsx or .csv):", type=["xlsx", "csv"])
        if uploaded_file is not None:
            save_path = os.path.join("data", "aerosense_historical_data.xlsx" if uploaded_file.name.endswith(".xlsx") else "aerosense_historical_data.csv")
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ Saved new dataset to `{save_path}`. Reloading application...")
            st.cache_data.clear()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_calib:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("#### Sensor Hardware Calibration & Zero-Point Offsets")
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("Temperature Calibration Offset (°C):", value=0.0, step=0.1, key="temp_offset")
            st.number_input("Carbon Monoxide (CO) Baseline Offset:", value=0.0, step=1.0, key="co_offset")
        with c2:
            st.number_input("Relative Humidity Offset (%):", value=0.0, step=0.5, key="hum_offset")
            st.number_input("PM2.5 Scaling Multiplier:", value=1.0, step=0.05, key="pm25_scale")
        st.caption("Calibration offsets are applied to telemetry feeds before threshold evaluation.")
        st.markdown("</div>", unsafe_allow_html=True)
