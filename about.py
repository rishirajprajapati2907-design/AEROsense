"""
AEROsense About Project Page — Engineering Capstone Showcase
Structured Sections A through H:
A. Project Overview
B. Problem Statement
C. Proposed Solution
D. Monitoring Parameters (7 sensor cards)
E. Technology Stack (7 technology cards)
F. System Architecture (Engineering workflow pipeline)
G. Project Objectives (6 core objectives)
H. Future Scope (5 future scope areas)
Plus Scientific Validation & Professional Footer.
Zero raw HTML/CSS leaks: uses st.html() and textwrap.dedent.
"""

import textwrap
import streamlit as st
from services.authentication import enter_demo_access


def render_about_page(is_public: bool = False):
    """
    Render the comprehensive About AEROsense engineering project presentation.
    Supports both public-facing showcase and authenticated in-app reference.
    """
    # ── Top Public Return Bar ──
    if is_public:
        top_bar_c1, top_bar_c2 = st.columns([2.2, 1.2])
        with top_bar_c1:
            st.html(textwrap.dedent("""
            <div style="background:rgba(34,211,238,0.08);border:1px solid rgba(34,211,238,0.22);border-radius:10px;padding:12px 18px;margin-bottom:20px;">
                <span style="font-size:0.75rem;font-weight:700;color:#22D3EE;text-transform:uppercase;letter-spacing:1px;">
                    Department of Computer Science and Engineering · Capstone Showcase
                </span>
                <div style="font-size:0.92rem;color:#E2E8F0;margin-top:2px;">
                    AEROsense — AI-Powered Indoor Air Quality Monitoring and Prediction System
                </div>
            </div>
            """).strip())
        with top_bar_c2:
            st.html("<div style='height:4px;'></div>")
            c_back_home, c_go_login = st.columns(2)
            with c_back_home:
                if st.button("🏠 Home", use_container_width=True, key="about_top_home_btn"):
                    st.session_state.public_nav = "home"
                    st.rerun()
            with c_go_login:
                if st.button("🚀 Sign In", type="primary", use_container_width=True, key="about_top_signin_btn"):
                    st.session_state.public_nav = "login"
                    st.rerun()

    # ── A. PROJECT OVERVIEW ──
    st.html(textwrap.dedent("""
    <div class="glass-panel" style="border-left: 4px solid #22D3EE; margin-bottom: 24px; padding: 22px 24px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
            <span style="font-size:1.8rem;filter:drop-shadow(0 0 10px rgba(34,211,238,0.4));">🍃</span>
            <span style="font-size:0.78rem;font-weight:800;text-transform:uppercase;letter-spacing:1px;color:#22D3EE;background:rgba(34,211,238,0.12);padding:3px 10px;border-radius:6px;border:1px solid rgba(34,211,238,0.3);">
                Section A · Project Overview
            </span>
        </div>
        <h1 style="margin:4px 0 12px 0;font-size:2.25rem;color:#F1F5F9;font-weight:800;letter-spacing:-0.5px;line-height:1.22;">
            AEROsense — AI-Powered Indoor Air Quality Monitoring and Prediction System
        </h1>
        <p style="font-size:1.02rem;color:#CBD5E1;line-height:1.75;margin:0;max-width:1150px;">
            <strong>AEROsense</strong> is an IoT and AI-based indoor air-quality monitoring system that collects environmental 
            readings through connected sensors and presents them through an interactive monitoring platform. Designed as an 
            engineering project for B.Tech Computer Science and Engineering, AEROsense bridges physical hardware telemetry, 
            cloud synchronization, statistical machine learning models, and immersive 3D digital twin visualizations.
        </p>
    </div>
    """).strip())

    # ── B & C. PROBLEM STATEMENT & PROPOSED SOLUTION ──
    col_prob, col_sol = st.columns(2, gap="medium")
    with col_prob:
        st.html(textwrap.dedent("""
        <div class="glass-panel" style="border-top:3px solid #EF4444;height:100%;padding:22px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                <span style="font-size:1.5rem;">⚠️</span>
                <div>
                    <div style="font-size:0.75rem;font-weight:700;color:#F87171;text-transform:uppercase;letter-spacing:0.8px;">Section B</div>
                    <h3 style="margin:0;color:#F87171;font-size:1.25rem;font-weight:800;">Problem Statement</h3>
                </div>
            </div>
            <p style="color:#94A3B8;font-size:0.92rem;line-height:1.7;margin:0;">
                Indoor air pollutants and harmful gases are not always visible or detectable through human senses. 
                Without continuous monitoring and historical analysis, occupants and facility managers fail to recognize 
                gradual changes or hazardous spikes in indoor environmental conditions until negative health effects or safety risks emerge.
            </p>
        </div>
        """).strip())

    with col_sol:
        st.html(textwrap.dedent("""
        <div class="glass-panel" style="border-top:3px solid #10B981;height:100%;padding:22px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                <span style="font-size:1.5rem;">💡</span>
                <div>
                    <div style="font-size:0.75rem;font-weight:700;color:#34D399;text-transform:uppercase;letter-spacing:0.8px;">Section C</div>
                    <h3 style="margin:0;color:#34D399;font-size:1.25rem;font-weight:800;">Proposed Solution</h3>
                </div>
            </div>
            <p style="color:#94A3B8;font-size:0.92rem;line-height:1.7;margin:0;">
                AEROsense combines an ESP32 microcontroller, dedicated environmental sensors, ThingSpeak cloud ingestion, 
                Python data science processing, and AI-based analytics to monitor indoor environmental parameters, analyze 
                historical readings (over 5,024 verified records), isolate statistical anomalies, and explore predictive insights.
            </p>
        </div>
        """).strip())

    st.html("<div style='height:26px;'></div>")

    # ── D. MONITORING PARAMETERS (7 SENSOR CARDS) ──
    st.html(textwrap.dedent("""
    <div style="margin-bottom:14px;">
        <span style="font-size:0.75rem;font-weight:700;color:#22D3EE;text-transform:uppercase;letter-spacing:1px;">
            Section D · Environmental Parameters
        </span>
        <h2 style="font-size:1.75rem;font-weight:800;color:#F1F5F9;margin:4px 0 4px 0;letter-spacing:-0.4px;">
            Configured 7-Sensor Telemetry Suite
        </h2>
        <div style="font-size:0.88rem;color:#94A3B8;">
            Physical multi-sensor array continuously profiling microclimate, combustion gases, volatile chemicals, and respirable aerosols.
        </div>
    </div>
    """).strip())

    s_row1 = st.columns(4)
    s_row2 = st.columns(3)
    sensor_cards = [
        ("Temperature", "DHT22 / SHT31", "20.0 – 24.5 °C (Thermal Comfort)", "#F59E0B", "🌡️", "field1"),
        ("Humidity", "DHT22 / SHT31", "35 – 50 %RH (Healthy Moisture)", "#06B6D4", "💧", "field2"),
        ("Smoke / Aerosol", "MQ-2 Ionization", "Ambient Baseline (<300 ADC)", "#8B5CF6", "💨", "field3"),
        ("Carbon Monoxide (CO)", "MQ-7 Semiconductor", "< 9 ppm Safe Threshold (EPA / WHO)", "#EF4444", "⚠️", "field4"),
        ("Ammonia (NH3)", "MQ-137 Chemical", "< 5 ppm Safe Threshold (OSHA)", "#A855F7", "🧪", "field5"),
        ("Nitrogen Oxides (NOx)", "MICS-6814 Metal Oxide", "< 53 ppb Safe Ambient Standard", "#EAB308", "🏭", "field6"),
        ("PM2.5 Particulates", "PMS5003 / Optical", "< 15 µg/m³ 24h Average (WHO Guideline)", "#10B981", "🌫️", "field7"),
    ]

    target_cols = [s_row1[0], s_row1[1], s_row1[2], s_row1[3], s_row2[0], s_row2[1], s_row2[2]]
    for idx, (name, hw, detail, color, icon, field) in enumerate(sensor_cards):
        with target_cols[idx]:
            st.html(textwrap.dedent(f"""
            <div class="sensor-card" style="--sensor-accent:{color};padding:16px;height:100%;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                    <span style="font-size:1.35rem;">{icon}</span>
                    <span style="font-size:0.72rem;font-weight:700;color:{color};background:rgba(255,255,255,0.05);padding:2px 8px;border-radius:4px;">
                        {field}
                    </span>
                </div>
                <div style="font-size:0.95rem;font-weight:800;color:#F1F5F9;margin-bottom:2px;">{name}</div>
                <div style="font-size:0.78rem;font-weight:700;color:{color};margin-bottom:6px;">Sensor HW: {hw}</div>
                <div style="font-size:0.76rem;color:#94A3B8;line-height:1.45;">{detail}</div>
            </div>
            """).strip())

    st.html("<div style='height:28px;'></div>")

    # ── E. TECHNOLOGY STACK (7 TECHNOLOGY CARDS) ──
    st.html(textwrap.dedent("""
    <div style="margin-bottom:14px;">
        <span style="font-size:0.75rem;font-weight:700;color:#22D3EE;text-transform:uppercase;letter-spacing:1px;">
            Section E · Technology Stack
        </span>
        <h2 style="font-size:1.75rem;font-weight:800;color:#F1F5F9;margin:4px 0 4px 0;letter-spacing:-0.4px;">
            Modern Engineering & Software Architecture
        </h2>
        <div style="font-size:0.88rem;color:#94A3B8;">
            Seven integrated software and hardware technologies powering the AEROsense platform.
        </div>
    </div>
    """).strip())

    t_row1 = st.columns(4)
    t_row2 = st.columns(3)
    tech_cards = [
        ("ESP32", "Microcontroller & Sensor Connectivity", "Dual-core 240MHz hardware node performing analog ADC sampling, digital I2C bus acquisition, and encrypted Wi-Fi telemetry transmission.", "#F59E0B", "⚡"),
        ("Python", "Backend Processing & Analytics", "High-performance processing using Pandas, NumPy, and OpenPyXL for data cleaning, Z-score outlier isolation, and time-series aggregation.", "#22D3EE", "🐍"),
        ("Streamlit", "Web Application Framework", "Reactive Python dashboard framework delivering custom glassmorphism components, caching pipelines, and responsive SaaS interfaces.", "#FF4B4B", "🖥️"),
        ("ThingSpeak", "Cloud Sensor Data Collection", "Dedicated IoT time-series cloud repository (Channel 3540991) supporting secure REST API feeds with rate-limit compliance.", "#0284C7", "☁️"),
        ("Machine Learning", "Historical Analysis & Prediction", "Statistical modeling, linear regression, and Z-score outlier classification (>3σ) evaluating air quality trends and diurnal cycles.", "#10B981", "🧠"),
        ("Three.js", "3D Interactive Visualization", "Hardware-accelerated WebGL rendering isometric indoor digital twin rooms, interactive probe markers, and atmospheric particle spheres.", "#8B5CF6", "🏛️"),
        ("Plotly", "Interactive Scientific Charts", "Zoomable time-series charts, pollutant correlation heatmaps, hourly profiles, and multi-parameter distribution histograms.", "#14B8A6", "📊"),
    ]

    tech_targets = [t_row1[0], t_row1[1], t_row1[2], t_row1[3], t_row2[0], t_row2[1], t_row2[2]]
    for idx, (title, sub, desc, color, icon) in enumerate(tech_cards):
        with tech_targets[idx]:
            st.html(textwrap.dedent(f"""
            <div class="glass-panel" style="padding:16px;height:100%;border-top:3px solid {color};">
                <div style="font-size:1.4rem;margin-bottom:6px;">{icon}</div>
                <div style="font-weight:800;color:#F1F5F9;font-size:0.95rem;">{title}</div>
                <div style="font-size:0.75rem;color:{color};margin-bottom:8px;font-weight:700;">{sub}</div>
                <div style="font-size:0.78rem;color:#94A3B8;line-height:1.5;">{desc}</div>
            </div>
            """).strip())

    st.html("<div style='height:28px;'></div>")

    # ── F. SYSTEM ARCHITECTURE (WORKFLOW DIAGRAM) ──
    st.html(textwrap.dedent("""
    <div style="margin-bottom:14px;">
        <span style="font-size:0.75rem;font-weight:700;color:#22D3EE;text-transform:uppercase;letter-spacing:1px;">
            Section F · System Architecture
        </span>
        <h2 style="font-size:1.75rem;font-weight:800;color:#F1F5F9;margin:4px 0 4px 0;letter-spacing:-0.4px;">
            End-to-End Engineering Workflow Pipeline
        </h2>
        <div style="font-size:0.88rem;color:#94A3B8;">
            From physical environmental sensing to intelligent cloud visualization.
        </div>
    </div>
    <div class="glass-panel" style="padding:24px 20px;text-align:center;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
            <div style="background:rgba(13,23,40,0.9);border:1px solid #22D3EE;border-radius:10px;padding:14px 16px;flex:1;min-width:135px;">
                <div style="font-size:1.5rem;margin-bottom:4px;">🔬</div>
                <div style="font-weight:800;color:#F1F5F9;font-size:0.88rem;">Environmental Sensors</div>
                <div style="font-size:0.74rem;color:#94A3B8;">7 Physical Channels</div>
            </div>
            <span style="color:#22D3EE;font-size:1.4rem;font-weight:900;">↓</span>
            <div style="background:rgba(13,23,40,0.9);border:1px solid #22D3EE;border-radius:10px;padding:14px 16px;flex:1;min-width:135px;">
                <div style="font-size:1.5rem;margin-bottom:4px;">⚡</div>
                <div style="font-weight:800;color:#F1F5F9;font-size:0.88rem;">ESP32 Node</div>
                <div style="font-size:0.74rem;color:#94A3B8;">ADC Sampling & Wi-Fi</div>
            </div>
            <span style="color:#22D3EE;font-size:1.4rem;font-weight:900;">↓</span>
            <div style="background:rgba(13,23,40,0.9);border:1px solid #22D3EE;border-radius:10px;padding:14px 16px;flex:1;min-width:135px;">
                <div style="font-size:1.5rem;margin-bottom:4px;">☁️</div>
                <div style="font-weight:800;color:#F1F5F9;font-size:0.88rem;">ThingSpeak Cloud</div>
                <div style="font-size:0.74rem;color:#94A3B8;">REST API & Storage</div>
            </div>
            <span style="color:#22D3EE;font-size:1.4rem;font-weight:900;">↓</span>
            <div style="background:rgba(13,23,40,0.9);border:1px solid #22D3EE;border-radius:10px;padding:14px 16px;flex:1;min-width:135px;">
                <div style="font-size:1.5rem;margin-bottom:4px;">🐍</div>
                <div style="font-weight:800;color:#F1F5F9;font-size:0.88rem;">Python Data Processing</div>
                <div style="font-size:0.74rem;color:#94A3B8;">Cleaning & Validation</div>
            </div>
            <span style="color:#22D3EE;font-size:1.4rem;font-weight:900;">↓</span>
            <div style="background:rgba(13,23,40,0.9);border:1px solid #22D3EE;border-radius:10px;padding:14px 16px;flex:1;min-width:135px;">
                <div style="font-size:1.5rem;margin-bottom:4px;">🧠</div>
                <div style="font-weight:800;color:#F1F5F9;font-size:0.88rem;">AI & Data Analytics</div>
                <div style="font-size:0.74rem;color:#94A3B8;">Outliers & Forecasting</div>
            </div>
            <span style="color:#22D3EE;font-size:1.4rem;font-weight:900;">↓</span>
            <div style="background:rgba(13,23,40,0.9);border:1px solid #14B8A6;border-radius:10px;padding:14px 16px;flex:1;min-width:135px;">
                <div style="font-size:1.5rem;margin-bottom:4px;">🍃</div>
                <div style="font-weight:800;color:#22D3EE;font-size:0.88rem;">AEROsense Dashboard</div>
                <div style="font-size:0.74rem;color:#94A3B8;">3D WebGL Digital Twin</div>
            </div>
        </div>
    </div>
    """).strip())

    st.html("<div style='height:28px;'></div>")

    # ── G. PROJECT OBJECTIVES (6 CORE OBJECTIVES) ──
    st.html(textwrap.dedent("""
    <div style="margin-bottom:14px;">
        <span style="font-size:0.75rem;font-weight:700;color:#22D3EE;text-transform:uppercase;letter-spacing:1px;">
            Section G · Core Engineering Objectives
        </span>
        <h2 style="font-size:1.75rem;font-weight:800;color:#F1F5F9;margin:4px 0 4px 0;letter-spacing:-0.4px;">
            Project Objectives
        </h2>
    </div>
    """).strip())

    obj_c1, obj_c2, obj_c3 = st.columns(3)
    objectives = [
        ("Monitor indoor environmental parameters", "Continuously capture ambient microclimate, respirable aerosols, and combustible gases.", "📡"),
        ("Collect sensor readings", "Transmit encrypted telemetry from the ESP32 node to ThingSpeak cloud via REST API protocols.", "☁️"),
        ("Analyze historical data", "Store, parse, and profile long-term time-series datasets (5,024 verified records across 15.1 days).", "📊"),
        ("Identify unusual readings", "Detect statistical anomalies (>3σ) and hardware ADC faults before adverse exposure escalates.", "🛡️"),
        ("Explore predictive analytics", "Implement diurnal cycle modeling and predictive trend extrapolation to forecast particulate buildup.", "🔮"),
        ("Visualize environmental information", "Render interactive 3D WebGL spatial room twins, particle dynamics, and scientific charts.", "🏛️"),
    ]

    for idx, (title, desc, icon) in enumerate(objectives):
        col = [obj_c1, obj_c2, obj_c3][idx % 3]
        with col:
            st.html(textwrap.dedent(f"""
            <div class="glass-panel" style="padding:16px 18px;margin-bottom:12px;">
                <div style="font-size:1.3rem;margin-bottom:4px;">{icon}</div>
                <div style="font-weight:800;color:#F1F5F9;font-size:0.92rem;margin-bottom:4px;">{title}</div>
                <div style="font-size:0.82rem;color:#94A3B8;line-height:1.55;">{desc}</div>
            </div>
            """).strip())

    st.html("<div style='height:28px;'></div>")

    # ── H. FUTURE SCOPE (5 FUTURE SCOPE AREAS) ──
    st.html(textwrap.dedent("""
    <div style="margin-bottom:14px;">
        <span style="font-size:0.75rem;font-weight:700;color:#14B8A6;text-transform:uppercase;letter-spacing:1px;">
            Section H · Roadmap & Research
        </span>
        <h2 style="font-size:1.75rem;font-weight:800;color:#F1F5F9;margin:4px 0 4px 0;letter-spacing:-0.4px;">
            Future Engineering Scope
        </h2>
    </div>
    """).strip())

    f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
    future_items = [
        ("Improved prediction models", "Implement operational LSTM neural networks and Prophet time-series models for multi-step pollutant forecasting.", "🧠"),
        ("Multi-room monitoring", "Deploy distributed sensor nodes across multiple facility zones using ESP-NOW or Zigbee mesh topology.", "🏢"),
        ("Automated notifications", "Configure instant SMS, email, and Webhook alerts triggered whenever toxic gas or PM2.5 thresholds exceed safety limits.", "🔔"),
        ("Mobile application", "Develop a cross-platform Progressive Web App (PWA) with real-time push notifications and occupant health tips.", "📱"),
        ("Advanced analytics", "Integrate indoor air quality index (IAQI) standards and automated ventilation/HVAC relay actuation.", "📈"),
    ]

    future_targets = [f_col1, f_col2, f_col3, f_col4, f_col5]
    for idx, (title, desc, icon) in enumerate(future_items):
        with future_targets[idx]:
            st.html(textwrap.dedent(f"""
            <div class="glass-panel" style="padding:16px;height:100%;">
                <div style="font-size:1.4rem;margin-bottom:6px;">{icon}</div>
                <div style="font-weight:800;color:#F1F5F9;font-size:0.88rem;margin-bottom:6px;">{title}</div>
                <div style="font-size:0.78rem;color:#94A3B8;line-height:1.5;">{desc}</div>
            </div>
            """).strip())

    # ── CALL-TO-ACTION & PROFESSIONAL FOOTER ──
    if is_public:
        st.html("<div style='height:36px;'></div>")
        st.html(textwrap.dedent("""
        <div class="glass-panel" style="text-align:center;padding:26px 20px;border-color:rgba(34,211,238,0.35);">
            <h3 style="font-size:1.5rem;font-weight:800;color:#F1F5F9;margin:0 0 8px 0;letter-spacing:-0.4px;">
                Ready to Experience AEROsense Intelligence?
            </h3>
            <p style="font-size:0.9rem;color:#94A3B8;max-width:640px;margin:0 auto 18px auto;line-height:1.6;">
                Access live sensor monitoring, 3D WebGL isometric twins, and machine learning anomaly detection.
            </p>
        </div>
        """).strip())

        cta_col1, cta_col2 = st.columns([1, 1])
        with cta_col1:
            if st.button("🚀 Sign In to Dashboard", type="primary", use_container_width=True, key="cta_bottom_signin"):
                st.session_state.public_nav = "login"
                st.rerun()
        with cta_col2:
            if st.button("⚡ Instant Demo / Evaluator Access", use_container_width=True, key="cta_bottom_demo"):
                enter_demo_access()
                st.rerun()

    # Engineering Footer
    st.html(textwrap.dedent("""
    <div style="border-top:1px solid rgba(255,255,255,0.06);margin-top:36px;padding-top:18px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
        <div style="font-size:0.8rem;color:#64748B;">
            AEROsense Engineering Capstone Project · Department of Computer Science and Engineering
        </div>
        <div style="font-size:0.78rem;color:#64748B;">
            ThingSpeak Private Channel ID: 3540991
        </div>
    </div>
    """).strip())
