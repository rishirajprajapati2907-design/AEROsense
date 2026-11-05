"""
AEROsense Editorial About Page — 60-30-10 Color Architecture
Color Distribution:
  - 60% Main: Deep Charcoal (#101820)
  - 30% Secondary: Soft Off-White (#E8EDEB)
  - 10% Accent: Electric Lime (#B7F34A)
Zero raw HTML/CSS leaks: uses st.html() and textwrap.dedent.
"""

import textwrap
import streamlit as st


def render_about_page(is_public: bool = False):
    """Render the editorial-style AEROsense platform documentation and background."""
    
    # ── Editorial Header ──
    st.html(textwrap.dedent("""
    <div style="padding: 10px 0 24px 0; border-bottom: 1px solid rgba(232,237,235,0.1); margin-bottom: 36px;">
        <div class="badge-tag">
            <span>PLATFORM BACKGROUND & ARCHITECTURE</span>
        </div>
        <h1 style="font-size:clamp(2.2rem, 3.8vw, 3.2rem);font-weight:900;color:#F1F5F9;margin:6px 0 12px 0;letter-spacing:-0.8px;line-height:1.15;">
            Intelligent Sensing for Enclosed Atmospheres
        </h1>
        <p class="body-editorial" style="max-width:760px;font-size:1.1rem;color:#E8EDEB;opacity:0.9;">
            AEROsense unites multi-gas telemetry, cloud synchronization, and statistical intelligence 
            to create actionable environmental clarity.
        </p>
    </div>
    """).strip())

    # ── Section 1: Project Introduction & Problem/Solution (Two-Column Editorial) ──
    col_intro_left, col_intro_right = st.columns([1.15, 1.0], gap="large")

    with col_intro_left:
        st.html(textwrap.dedent("""
        <div>
            <h2 style="font-size:1.6rem;font-weight:800;color:#F1F5F9;margin:0 0 12px 0;letter-spacing:-0.4px;">
                The Challenge of Enclosed Environments
            </h2>
            <p class="body-editorial" style="margin-bottom:16px;">
                Modern indoor spaces are engineered for energy efficiency and thermal insulation, frequently trapping 
                gaseous emissions and particulate matter that accumulate during daily activities. Unlike outdoor air 
                subject to continuous atmospheric mixing, indoor microclimates can experience dramatic shifts within minutes.
            </p>
            <p class="body-editorial">
                Because harmful air constituents such as carbon monoxide, volatile amine byproducts, and respirable particles 
                remain largely odorless and invisible, occupants lack immediate sensory warning. Passive ventilation alone cannot 
                diagnose or preempt deteriorating air quality.
            </p>
        </div>
        """).strip())

    with col_intro_right:
        st.html(textwrap.dedent("""
        <div style="background:#16222F;border:1px solid rgba(232,237,235,0.16);border-radius:16px;padding:24px;box-shadow:0 8px 30px rgba(0,0,0,0.35);">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                <span style="font-size:1.4rem;">💡</span>
                <span style="font-size:1.15rem;font-weight:800;color:#B7F34A;">The AEROsense Approach</span>
            </div>
            <p class="body-editorial" style="font-size:0.92rem;margin-bottom:14px;color:#E8EDEB;opacity:0.9;">
                AEROsense addresses this blind spot through continuous IoT-based data ingestion. Hardware-level sensors stream 
                telemetry into cloud storage, where statistical algorithms and time-series profiling evaluate conditions against 
                historical baselines.
            </p>
            <div style="display:flex;flex-direction:column;gap:8px;font-size:0.82rem;color:#E8EDEB;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="color:#B7F34A;font-weight:800;">✓</span> Multi-channel physical gas & particulate acquisition
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="color:#B7F34A;font-weight:800;">✓</span> Encrypted cloud data synchronization via REST protocols
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="color:#B7F34A;font-weight:800;">✓</span> Automated statistical outlier isolation and trend modeling
                </div>
            </div>
        </div>
        """).strip())

    st.html("<div style='height:54px;'></div>")

    # ── Section 2: System Workflow (Horizontal Diagram) ──
    st.html(textwrap.dedent("""
    <div style="margin-bottom:22px;">
        <h2 style="font-size:1.6rem;font-weight:800;color:#F1F5F9;margin:0 0 8px 0;letter-spacing:-0.4px;">
            System Workflow & Data Transmission
        </h2>
        <p class="body-editorial" style="max-width:700px;">
            Telemetry flows across six coordinated stages from physical transducers to user visual analytics.
        </p>
    </div>

    <div class="arch-flow-container">
        <div class="arch-step-node">
            <div class="arch-node-num">01</div>
            <div style="font-size:1.5rem;margin:4px 0;">🔬</div>
            <div style="font-weight:800;color:#F1F5F9;font-size:0.9rem;">Sensing Array</div>
            <div style="font-size:0.74rem;color:#B7F34A;margin-top:2px;">7 Sensor Channels</div>
        </div>
        <div class="arch-arrow">→</div>

        <div class="arch-step-node">
            <div class="arch-node-num">02</div>
            <div style="font-size:1.5rem;margin:4px 0;">⚡</div>
            <div style="font-weight:800;color:#F1F5F9;font-size:0.9rem;">ESP32 Node</div>
            <div style="font-size:0.74rem;color:#B7F34A;margin-top:2px;">ADC & I2C Sampling</div>
        </div>
        <div class="arch-arrow">→</div>

        <div class="arch-step-node">
            <div class="arch-node-num">03</div>
            <div style="font-size:1.5rem;margin:4px 0;">☁️</div>
            <div style="font-weight:800;color:#F1F5F9;font-size:0.9rem;">ThingSpeak</div>
            <div style="font-size:0.74rem;color:#E8EDEB;margin-top:2px;">Cloud Repository</div>
        </div>
        <div class="arch-arrow">→</div>

        <div class="arch-step-node">
            <div class="arch-node-num">04</div>
            <div style="font-size:1.5rem;margin:4px 0;">🐍</div>
            <div style="font-weight:800;color:#F1F5F9;font-size:0.9rem;">Python Core</div>
            <div style="font-size:0.74rem;color:#E8EDEB;margin-top:2px;">ETL & Normalization</div>
        </div>
        <div class="arch-arrow">→</div>

        <div class="arch-step-node">
            <div class="arch-node-num">05</div>
            <div style="font-size:1.5rem;margin:4px 0;">🧠</div>
            <div style="font-weight:800;color:#F1F5F9;font-size:0.9rem;">AI Intelligence</div>
            <div style="font-size:0.74rem;color:#B7F34A;margin-top:2px;">Statistical ML Models</div>
        </div>
        <div class="arch-arrow">→</div>

        <div class="arch-step-node" style="border-color:#B7F34A;">
            <div class="arch-node-num" style="background:#B7F34A;color:#101820;">06</div>
            <div style="font-size:1.5rem;margin:4px 0;">🍃</div>
            <div style="font-weight:800;color:#B7F34A;font-size:0.9rem;">AEROsense UI</div>
            <div style="font-size:0.74rem;color:#F1F5F9;margin-top:2px;">Interactive Portal</div>
        </div>
    </div>
    """).strip())

    st.html("<div style='height:54px;'></div>")

    # ── Section 3: Technology Stack (Compact Visual Showcase, NOT giant boxes) ──
    st.html(textwrap.dedent("""
    <div style="margin-bottom:20px;">
        <h2 style="font-size:1.6rem;font-weight:800;color:#F1F5F9;margin:0 0 8px 0;letter-spacing:-0.4px;">
            Technology Stack
        </h2>
        <p class="body-editorial" style="max-width:700px;">
            Built with modern software and hardware technologies powering data collection, analytics, and spatial rendering.
        </p>
    </div>

    <!-- Compact Technology Showcase (30% Secondary Soft Off-White) -->
    <div style="display:flex;flex-wrap:wrap;gap:12px;margin-bottom:28px;">
        <div class="tech-pill">
            <span>⚡</span>
            <span>ESP32 Microcontroller</span>
        </div>
        <div class="tech-pill">
            <span>🐍</span>
            <span>Python 3.11</span>
        </div>
        <div class="tech-pill">
            <span>🖥️</span>
            <span>Streamlit</span>
        </div>
        <div class="tech-pill">
            <span>☁️</span>
            <span>ThingSpeak Cloud</span>
        </div>
        <div class="tech-pill">
            <span>🧠</span>
            <span>Statistical Machine Learning</span>
        </div>
        <div class="tech-pill">
            <span>🏛️</span>
            <span>Three.js WebGL</span>
        </div>
        <div class="tech-pill">
            <span>📊</span>
            <span>Plotly Data Visualizations</span>
        </div>
    </div>
    """).strip())

    st.html("<div style='height:40px;'></div>")

    # ── Section 4: Project Objectives (Concise Numbered Layout with Lime Badges) ──
    st.html(textwrap.dedent("""
    <div style="margin-bottom:18px;">
        <h2 style="font-size:1.6rem;font-weight:800;color:#F1F5F9;margin:0 0 8px 0;letter-spacing:-0.4px;">
            Core Objectives
        </h2>
        <p class="body-editorial" style="max-width:700px;">
            Six focused functional goals guiding the architectural and algorithmic design of the platform.
        </p>
    </div>

    <div>
        <div class="editorial-num-row">
            <div class="editorial-num-badge">1</div>
            <div>
                <div style="font-weight:700;color:#F1F5F9;font-size:1.02rem;margin-bottom:2px;">
                    Continuous Indoor Telemetry Surveillance
                </div>
                <div class="body-editorial" style="font-size:0.9rem;">
                    Capture synchronized microclimate, combustion aerosols, and toxic gas fluctuations in real time.
                </div>
            </div>
        </div>

        <div class="editorial-num-row">
            <div class="editorial-num-badge">2</div>
            <div>
                <div style="font-weight:700;color:#F1F5F9;font-size:1.02rem;margin-bottom:2px;">
                    Cloud-Integrated Sensor Transmission
                </div>
                <div class="body-editorial" style="font-size:0.9rem;">
                    Maintain reliable, rate-compliant data synchronization between physical microcontrollers and cloud endpoints.
                </div>
            </div>
        </div>

        <div class="editorial-num-row">
            <div class="editorial-num-badge">3</div>
            <div>
                <div style="font-weight:700;color:#F1F5F9;font-size:1.02rem;margin-bottom:2px;">
                    Long-Term Time-Series Historical Profiling
                </div>
                <div class="body-editorial" style="font-size:0.9rem;">
                    Aggregate and analyze verified multi-week telemetry datasets to identify recurring environmental baselines.
                </div>
            </div>
        </div>

        <div class="editorial-num-row">
            <div class="editorial-num-badge">4</div>
            <div>
                <div style="font-weight:700;color:#F1F5F9;font-size:1.02rem;margin-bottom:2px;">
                    Statistical Anomaly and Fault Isolation
                </div>
                <div class="body-editorial" style="font-size:0.9rem;">
                    Detect unusual sensor readings, frozen analog signatures, and statistical Z-score spikes (>3σ) before hazardous accumulation.
                </div>
            </div>
        </div>

        <div class="editorial-num-row">
            <div class="editorial-num-badge">5</div>
            <div>
                <div style="font-weight:700;color:#F1F5F9;font-size:1.02rem;margin-bottom:2px;">
                    Predictive Diurnal Trend Exploration
                </div>
                <div class="body-editorial" style="font-size:0.9rem;">
                    Formulate predictive models extrapolating expected 1-hour particulate trends based on historical diurnal dynamics.
                </div>
            </div>
        </div>

        <div class="editorial-num-row">
            <div class="editorial-num-badge">6</div>
            <div>
                <div style="font-weight:700;color:#F1F5F9;font-size:1.02rem;margin-bottom:2px;">
                    Interactive Multi-Dimensional Visualization
                </div>
                <div class="body-editorial" style="font-size:0.9rem;">
                    Provide intuitive visual access via responsive charts, circular aggregate gauges, and 3D WebGL spatial twins.
                </div>
            </div>
        </div>
    </div>
    """).strip())

    st.html("<div style='height:54px;'></div>")

    # ── Section 5: Future Scope (Clean Editorial Section) ──
    st.html(textwrap.dedent("""
    <div style="padding-top:20px;border-top:1px solid rgba(232,237,235,0.1);margin-bottom:36px;">
        <h2 style="font-size:1.6rem;font-weight:800;color:#F1F5F9;margin:0 0 10px 0;letter-spacing:-0.4px;">
            Future Scope & Roadmap
        </h2>
        <p class="body-editorial" style="max-width:740px;margin-bottom:24px;">
            As AEROsense transitions beyond initial prototyping, development centers on multi-zone mesh scalability, 
            automated mechanical actuation, and advanced deep learning forecasting models.
        </p>

        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(260px, 1fr));gap:24px;">
            <div>
                <div style="font-weight:700;color:#B7F34A;font-size:0.95rem;margin-bottom:4px;">
                    Deep Learning Forecasting
                </div>
                <div class="body-editorial" style="font-size:0.88rem;">
                    Deploy multi-step recurrent neural networks (LSTM) trained on continuous temporal horizons to predict pollutant spikes hours ahead.
                </div>
            </div>

            <div>
                <div style="font-weight:700;color:#E8EDEB;font-size:0.95rem;margin-bottom:4px;">
                    Distributed Mesh Networks
                </div>
                <div class="body-editorial" style="font-size:0.88rem;">
                    Extend hardware nodes into multi-room mesh topologies (ESP-NOW/Zigbee) enabling spatial floorplan tracking across entire facilities.
                </div>
            </div>

            <div>
                <div style="font-weight:700;color:#E8EDEB;font-size:0.95rem;margin-bottom:4px;">
                    Automated HVAC Integration
                </div>
                <div class="body-editorial" style="font-size:0.88rem;">
                    Interface with smart ventilation relays to automatically trigger fresh air dampers whenever CO or particulate thresholds rise.
                </div>
            </div>

            <div>
                <div style="font-weight:700;color:#F59E0B;font-size:0.95rem;margin-bottom:4px;">
                    Real-Time Alerts & Notification Webhooks
                </div>
                <div class="body-editorial" style="font-size:0.88rem;">
                    Provide configurable webhook integrations and instant operator notifications for immediate awareness of air quality hazards.
                </div>
            </div>
        </div>
    </div>
    """).strip())

    # ── Call to Action (When accessed publicly) ──
    if is_public:
        st.html(textwrap.dedent("""
        <div style="text-align:center;padding:36px 20px;background:#16222F;border:1px solid rgba(232,237,235,0.18);border-radius:16px;margin:32px 0 16px 0;">
            <h3 style="font-size:1.45rem;font-weight:800;color:#F1F5F9;margin:0 0 8px 0;">
                Ready to Explore the Platform?
            </h3>
            <p class="body-editorial" style="font-size:0.95rem;max-width:540px;margin:0 auto 20px auto;">
                Experience the live sensor telemetry, statistical analytics, and 3D environment cockpit.
            </p>
        </div>
        """).strip())

        c1, c2, c3 = st.columns([1.2, 1.4, 1.2])
        with c2:
            if st.button("Explore Analytics ↗", type="primary", use_container_width=True, key="about_cta_btn"):
                st.session_state.public_nav = "login"
                st.rerun()

    # ── Editorial Footer ──
    st.html(textwrap.dedent("""
    <div style="border-top:1px solid rgba(232,237,235,0.1);padding-top:20px;margin-top:40px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
        <div style="font-size:0.8rem;color:#94A3B8;">
            <span style="color:#B7F34A;font-weight:700;">AERO</span><span style="color:#E8EDEB;">sense</span> Environmental Intelligence Platform
        </div>
        <div style="font-size:0.76rem;color:#94A3B8;">
            Channel 3540991 · IoT Cloud Synchronized
        </div>
    </div>
    """).strip())
