"""
AEROsense Home Page — Modern Environmental Intelligence Landing Page
Features:
- Professional Hero section with headline and mission description
- Interactive 3D Atmospheric Particle Sphere (Three.js WebGL)
- 4 Core Environmental Intelligence Pillars
- 7 Telemetry Channels Interactive Overview
- System Architecture Preview Pipeline
- Verified Dataset & Hardware Metrics Banner
- Professional Engineering Footer
Zero raw HTML/CSS leaks: uses st.html() and textwrap.dedent.
"""

import textwrap
import streamlit as st
import streamlit.components.v1 as components
from services.authentication import enter_demo_access


def _render_hero_3d_atmospheric_sphere():
    """Render the interactive Three.js 3D atmospheric particle sphere."""
    three_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: radial-gradient(circle at center, #0D1728 0%, #080F1E 95%);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        #hero-sphere-viewport {
            width: 100%;
            height: 100%;
            position: relative;
            box-sizing: border-box;
            border-radius: 14px;
            border: 1px solid rgba(34, 211, 238, 0.2);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 0 25px rgba(34, 211, 238, 0.05);
            overflow: hidden;
            cursor: grab;
        }
        #hero-sphere-viewport:active {
            cursor: grabbing;
        }
        .hud-label {
            position: absolute;
            top: 14px;
            left: 16px;
            font-size: 11px;
            font-weight: 700;
            color: #22D3EE;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            background: rgba(8, 15, 30, 0.8);
            padding: 4px 10px;
            border-radius: 5px;
            border: 1px solid rgba(34, 211, 238, 0.25);
            pointer-events: none;
            z-index: 10;
        }
        .hud-status {
            position: absolute;
            bottom: 12px;
            right: 14px;
            font-size: 10px;
            color: #94A3B8;
            background: rgba(8, 15, 30, 0.75);
            padding: 3px 8px;
            border-radius: 4px;
            pointer-events: none;
            z-index: 10;
        }
    </style>
</head>
<body>
    <div id="hero-sphere-viewport">
        <div class="hud-label">Atmospheric Dynamics · WebGL 3D</div>
        <div class="hud-status">Interactive Simulation · 450 Particles</div>
    </div>
    <script src="https://unpkg.com/three@0.128.0/build/three.min.js"></script>
    <script>
        (function() {
            const container = document.getElementById('hero-sphere-viewport');
            if (!container) return;

            function initScene() {
                if (typeof THREE === 'undefined') {
                    setTimeout(initScene, 60);
                    return;
                }
                const width = container.clientWidth || 500;
                const height = container.clientHeight || 340;

                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
                camera.position.z = 155;

                const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
                renderer.setSize(width, height);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                container.appendChild(renderer.domElement);

                // Create Particle Sphere
                const count = 480;
                const geometry = new THREE.BufferGeometry();
                const positions = new Float32Array(count * 3);
                const colors = new Float32Array(count * 3);

                const c1 = new THREE.Color(0x22D3EE); // Vibrant Cyan
                const c2 = new THREE.Color(0x14B8A6); // Emerald Teal
                const c3 = new THREE.Color(0x38BDF8); // Ambient Sky Blue

                for (let i = 0; i < count; i++) {
                    const phi = Math.acos(-1 + (2 * i) / count);
                    const theta = Math.sqrt(count * Math.PI) * phi;
                    const r = 48 + (Math.random() - 0.5) * 8;
                    positions[i * 3] = r * Math.cos(theta) * Math.sin(phi);
                    positions[i * 3 + 1] = r * Math.sin(theta) * Math.sin(phi);
                    positions[i * 3 + 2] = r * Math.cos(phi);

                    const mix = Math.random();
                    const col = mix < 0.5 ? c1.clone().lerp(c2, mix * 2) : c2.clone().lerp(c3, (mix - 0.5) * 2);
                    colors[i * 3] = col.r;
                    colors[i * 3 + 1] = col.g;
                    colors[i * 3 + 2] = col.b;
                }

                geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
                geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

                const material = new THREE.PointsMaterial({
                    size: 2.5,
                    vertexColors: true,
                    transparent: true,
                    opacity: 0.9,
                    blending: THREE.AdditiveBlending
                });

                const sphere = new THREE.Points(geometry, material);
                scene.add(sphere);

                // Add subtle inner core glow
                const coreGeo = new THREE.SphereGeometry(18, 16, 16);
                const coreMat = new THREE.MeshBasicMaterial({
                    color: 0x0D2847,
                    wireframe: true,
                    transparent: true,
                    opacity: 0.25
                });
                const core = new THREE.Mesh(coreGeo, coreMat);
                scene.add(core);

                // Mouse interactivity
                let mouseX = 0, mouseY = 0;
                window.addEventListener('mousemove', function(e) {
                    const rect = container.getBoundingClientRect();
                    mouseX = ((e.clientX - rect.left) / width - 0.5) * 0.4;
                    mouseY = ((e.clientY - rect.top) / height - 0.5) * 0.4;
                });

                function animate() {
                    requestAnimationFrame(animate);
                    sphere.rotation.y += 0.0035 + mouseX * 0.01;
                    sphere.rotation.x += 0.0018 + mouseY * 0.01;
                    core.rotation.y -= 0.002;
                    renderer.render(scene, camera);
                }
                animate();

                window.addEventListener('resize', function() {
                    const w = container.clientWidth || width;
                    const h = container.clientHeight || height;
                    camera.aspect = w / h;
                    camera.updateProjectionMatrix();
                    renderer.setSize(w, h);
                });
            }

            initScene();
        })();
    </script>
</body>
</html>"""
    components.html(three_html, height=350)


def render_home_page():
    """Render the dedicated AEROsense Home / Landing Page."""
    # ── 1. HERO SECTION ──
    col_hero_text, col_hero_3d = st.columns([1.25, 1.0], gap="large")

    with col_hero_text:
        st.html(textwrap.dedent("""
        <div style="padding: 10px 4px 14px 4px;">
            <div style="display:inline-flex;align-items:center;gap:8px;background:rgba(34,211,238,0.1);border:1px solid rgba(34,211,238,0.3);padding:4px 12px;border-radius:20px;margin-bottom:16px;">
                <span style="font-size:0.9rem;">🍃</span>
                <span style="font-size:0.75rem;font-weight:700;color:#22D3EE;text-transform:uppercase;letter-spacing:1px;">
                    Environmental Intelligence Platform · B.Tech Capstone
                </span>
            </div>

            <h1 style="font-size:2.85rem;font-weight:900;color:#F1F5F9;line-height:1.18;margin:0 0 16px 0;letter-spacing:-0.8px;">
                Understand Your Air.<br>
                <span style="background:linear-gradient(90deg,#22D3EE 0%,#14B8A6 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                    Predict a Healthier Tomorrow.
                </span>
            </h1>

            <p style="font-size:1.05rem;color:#94A3B8;line-height:1.75;max-width:580px;margin:0 0 24px 0;">
                An IoT-powered indoor environmental monitoring platform designed to collect, analyze and visualize 
                air-quality parameters through intelligent sensing and data analytics.
            </p>
        </div>
        """).strip())

        # Action Buttons
        btn_c1, btn_c2, btn_c3 = st.columns([1.1, 1.1, 1.1])
        with btn_c1:
            if st.button("🚀 Explore Project", type="primary", use_container_width=True, key="home_hero_explore_btn"):
                st.session_state.public_nav = "about"
                st.rerun()
        with btn_c2:
            if st.button("🔑 Access Platform", type="secondary", use_container_width=True, key="home_hero_login_btn"):
                st.session_state.public_nav = "login"
                st.rerun()
        with btn_c3:
            if st.button("⚡ Instant Demo", use_container_width=True, key="home_hero_demo_btn", help="One-click access with guest evaluator profile"):
                enter_demo_access()
                st.rerun()

        # Telemetry Badges Strip
        st.html(textwrap.dedent("""
        <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:24px;">
            <span style="background:rgba(17,28,46,0.85);border:1px solid rgba(34,211,238,0.2);color:#CBD5E1;font-size:0.78rem;font-weight:600;padding:6px 12px;border-radius:20px;">
                📡 7 Telemetry Channels
            </span>
            <span style="background:rgba(17,28,46,0.85);border:1px solid rgba(34,211,238,0.2);color:#CBD5E1;font-size:0.78rem;font-weight:600;padding:6px 12px;border-radius:20px;">
                ☁️ ThingSpeak Cloud Feed
            </span>
            <span style="background:rgba(17,28,46,0.85);border:1px solid rgba(34,211,238,0.2);color:#CBD5E1;font-size:0.78rem;font-weight:600;padding:6px 12px;border-radius:20px;">
                🧠 Statistical Outlier AI (>3σ)
            </span>
            <span style="background:rgba(17,28,46,0.85);border:1px solid rgba(34,211,238,0.2);color:#CBD5E1;font-size:0.78rem;font-weight:600;padding:6px 12px;border-radius:20px;">
                🏛️ 3D Digital Room Twin
            </span>
        </div>
        """).strip())

    with col_hero_3d:
        st.html("<div style='height:4px;'></div>")
        _render_hero_3d_atmospheric_sphere()

    st.html("<div style='height:32px;'></div>")

    # ── 2. FOUR CORE INTELLIGENCE PILLARS ──
    st.html(textwrap.dedent("""
    <div style="text-align:center;margin-bottom:20px;">
        <span style="font-size:0.75rem;font-weight:700;color:#22D3EE;text-transform:uppercase;letter-spacing:1.2px;">
            Integrated System Capabilities
        </span>
        <h2 style="font-size:1.85rem;font-weight:800;color:#F1F5F9;margin:6px 0 0 0;letter-spacing:-0.5px;">
            Scientific Architecture & Intelligent Monitoring
        </h2>
    </div>
    """).strip())

    p1, p2, p3, p4 = st.columns(4)
    pillars = [
        ("🔬 Multi-Gas Telemetry", "Simultaneous acquisition of microclimate (Temp/Hum), particulate fraction (PM2.5), and hazardous gases (CO, NH3, NOx, Smoke).", "#F59E0B", "📡"),
        ("⚡ ESP32 Edge Ingestion", "Dual-core 240MHz hardware node performing multi-channel ADC sampling and encrypted Wi-Fi transmissions.", "#06B6D4", "⚡"),
        ("☁️ ThingSpeak Cloud", "Real-time cloud database managing telemetry feeds (Channel 3540991) with rate-limit compliance.", "#8B5CF6", "☁️"),
        ("🧠 AI Diagnostics", "Continuous statistical anomaly detection isolating physical sensor outliers (>3σ) and diurnal forecasting.", "#10B981", "🧠"),
    ]

    for idx, (title, desc, color, icon) in enumerate(pillars):
        col = [p1, p2, p3, p4][idx]
        with col:
            st.html(textwrap.dedent(f"""
            <div class="glass-panel" style="padding:18px 20px;height:100%;border-top:3px solid {color};">
                <div style="font-size:1.5rem;margin-bottom:8px;">{icon}</div>
                <div style="font-size:0.96rem;font-weight:800;color:#F1F5F9;margin-bottom:6px;">{title}</div>
                <div style="font-size:0.8rem;color:#94A3B8;line-height:1.55;">{desc}</div>
            </div>
            """).strip())

    st.html("<div style='height:36px;'></div>")

    # ── 3. SEVEN MONITORED PARAMETERS OVERVIEW ──
    st.html(textwrap.dedent("""
    <div style="text-align:center;margin-bottom:20px;">
        <span style="font-size:0.75rem;font-weight:700;color:#22D3EE;text-transform:uppercase;letter-spacing:1.2px;">
            Continuous Environmental Sensing
        </span>
        <h2 style="font-size:1.85rem;font-weight:800;color:#F1F5F9;margin:6px 0 6px 0;letter-spacing:-0.5px;">
            Seven Indoor Air Quality Telemetry Channels
        </h2>
        <div style="font-size:0.88rem;color:#94A3B8;max-width:700px;margin:0 auto;">
            Configured to monitor critical thermal comfort, combustible risk, and respirable toxic thresholds.
        </div>
    </div>
    """).strip())

    s_row1 = st.columns(4)
    s_row2 = st.columns(3)
    sensors = [
        ("Temperature", "20.0 – 24.5 °C", "DHT22 / SHT31", "Thermal comfort and HVAC load index", "#F59E0B", "🌡️"),
        ("Humidity", "35 – 50 %RH", "DHT22 / SHT31", "Relative moisture & mold deterrence", "#06B6D4", "💧"),
        ("Smoke / Aerosol", "Clean Ambient", "MQ-2 Ionization", "Combustion particles & aerosol presence", "#8B5CF6", "💨"),
        ("Carbon Monoxide (CO)", "< 9 ppm Safe", "MQ-7 Semiconductor", "Surveillance of toxic incomplete combustion", "#EF4444", "⚠️"),
        ("Ammonia (NH3)", "< 5 ppm Safe", "MQ-137 Amine", "Surveillance of volatile amine off-gassing", "#A855F7", "🧪"),
        ("Nitrogen Oxides (NOx)", "< 53 ppb Safe", "MICS-6814 Metal Oxide", "Combustion and vehicle exhaust filtration", "#EAB308", "🏭"),
        ("PM2.5 Particulates", "< 15 µg/m³ WHO", "PMS5003 / Optical", "Respirable dust <= 2.5 µm fraction", "#10B981", "🌫️"),
    ]

    target_cols = [s_row1[0], s_row1[1], s_row1[2], s_row1[3], s_row2[0], s_row2[1], s_row2[2]]
    for idx, (name, bench, hw, desc, color, icon) in enumerate(sensors):
        with target_cols[idx]:
            st.html(textwrap.dedent(f"""
            <div class="sensor-card" style="--sensor-accent:{color};padding:16px;height:100%;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                    <span style="font-size:1.35rem;">{icon}</span>
                    <span style="font-size:0.72rem;font-weight:700;color:{color};background:rgba(255,255,255,0.05);padding:2px 8px;border-radius:4px;">
                        field{idx+1}
                    </span>
                </div>
                <div style="font-size:0.95rem;font-weight:800;color:#F1F5F9;margin-bottom:2px;">{name}</div>
                <div style="font-size:0.8rem;font-weight:700;color:{color};margin-bottom:6px;">Benchmark: {bench}</div>
                <div style="font-size:0.76rem;color:#94A3B8;line-height:1.45;">{desc}</div>
            </div>
            """).strip())

    st.html("<div style='height:36px;'></div>")

    # ── 4. END-TO-END WORKFLOW ARCHITECTURE TEASER ──
    st.html(textwrap.dedent("""
    <div style="text-align:center;margin-bottom:20px;">
        <span style="font-size:0.75rem;font-weight:700;color:#22D3EE;text-transform:uppercase;letter-spacing:1.2px;">
            Data Ingestion Pipeline
        </span>
        <h2 style="font-size:1.85rem;font-weight:800;color:#F1F5F9;margin:6px 0 0 0;letter-spacing:-0.5px;">
            Hardware to Cloud to Intelligence Workflow
        </h2>
    </div>
    <div class="glass-panel" style="padding:22px;text-align:center;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
            <div style="background:rgba(13,23,40,0.9);border:1px solid #22D3EE;border-radius:10px;padding:12px 14px;flex:1;min-width:130px;">
                <div style="font-size:1.4rem;">🔬</div>
                <div style="font-weight:700;color:#F1F5F9;font-size:0.86rem;">7 Sensors</div>
                <div style="font-size:0.72rem;color:#94A3B8;">Physical Analog/Digital</div>
            </div>
            <span style="color:#22D3EE;font-size:1.2rem;font-weight:800;">→</span>
            <div style="background:rgba(13,23,40,0.9);border:1px solid #22D3EE;border-radius:10px;padding:12px 14px;flex:1;min-width:130px;">
                <div style="font-size:1.4rem;">⚡</div>
                <div style="font-weight:700;color:#F1F5F9;font-size:0.86rem;">ESP32 MCU</div>
                <div style="font-size:0.72rem;color:#94A3B8;">ADC Sampling & Wi-Fi</div>
            </div>
            <span style="color:#22D3EE;font-size:1.2rem;font-weight:800;">→</span>
            <div style="background:rgba(13,23,40,0.9);border:1px solid #22D3EE;border-radius:10px;padding:12px 14px;flex:1;min-width:130px;">
                <div style="font-size:1.4rem;">☁️</div>
                <div style="font-weight:700;color:#F1F5F9;font-size:0.86rem;">ThingSpeak</div>
                <div style="font-size:0.72rem;color:#94A3B8;">Channel 3540991</div>
            </div>
            <span style="color:#22D3EE;font-size:1.2rem;font-weight:800;">→</span>
            <div style="background:rgba(13,23,40,0.9);border:1px solid #22D3EE;border-radius:10px;padding:12px 14px;flex:1;min-width:130px;">
                <div style="font-size:1.4rem;">🐍</div>
                <div style="font-weight:700;color:#F1F5F9;font-size:0.86rem;">Python Engine</div>
                <div style="font-size:0.72rem;color:#94A3B8;">Pandas & Outlier Clean</div>
            </div>
            <span style="color:#22D3EE;font-size:1.2rem;font-weight:800;">→</span>
            <div style="background:rgba(13,23,40,0.9);border:1px solid #22D3EE;border-radius:10px;padding:12px 14px;flex:1;min-width:130px;">
                <div style="font-size:1.4rem;">🧠</div>
                <div style="font-weight:700;color:#F1F5F9;font-size:0.86rem;">AI Analytics</div>
                <div style="font-size:0.72rem;color:#94A3B8;">Diurnal & Outlier Models</div>
            </div>
            <span style="color:#22D3EE;font-size:1.2rem;font-weight:800;">→</span>
            <div style="background:rgba(13,23,40,0.9);border:1px solid #14B8A6;border-radius:10px;padding:12px 14px;flex:1;min-width:130px;">
                <div style="font-size:1.4rem;">🍃</div>
                <div style="font-weight:700;color:#22D3EE;font-size:0.86rem;">AEROsense UI</div>
                <div style="font-size:0.72rem;color:#94A3B8;">3D WebGL Digital Twin</div>
            </div>
        </div>
    </div>
    """).strip())

    st.html("<div style='height:36px;'></div>")

    # ── 5. VERIFIED DATASET METRICS BANNER ──
    st.html(textwrap.dedent("""
    <div class="glass-panel" style="padding:24px 30px;background:linear-gradient(135deg,rgba(17,28,46,0.95) 0%,rgba(13,23,40,0.98) 100%);border-color:rgba(34,211,238,0.25);">
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:20px;text-align:center;">
            <div>
                <div style="font-size:2.2rem;font-weight:900;color:#22D3EE;letter-spacing:-0.5px;">5,024</div>
                <div style="font-size:0.78rem;font-weight:700;color:#CBD5E1;text-transform:uppercase;margin-top:2px;">Historical Readings</div>
                <div style="font-size:0.72rem;color:#64748B;">Validated Excel Archive</div>
            </div>
            <div>
                <div style="font-size:2.2rem;font-weight:900;color:#14B8A6;letter-spacing:-0.5px;">15.1</div>
                <div style="font-size:0.78rem;font-weight:700;color:#CBD5E1;text-transform:uppercase;margin-top:2px;">Days Continuous Sampling</div>
                <div style="font-size:0.72rem;color:#64748B;">Multi-Week Indoor Profiling</div>
            </div>
            <div>
                <div style="font-size:2.2rem;font-weight:900;color:#F59E0B;letter-spacing:-0.5px;">7</div>
                <div style="font-size:0.78rem;font-weight:700;color:#CBD5E1;text-transform:uppercase;margin-top:2px;">Active Telemetry Probes</div>
                <div style="font-size:0.72rem;color:#64748B;">Microclimate, Gas & Aerosols</div>
            </div>
            <div>
                <div style="font-size:2.2rem;font-weight:900;color:#10B981;letter-spacing:-0.5px;">100%</div>
                <div style="font-size:0.78rem;font-weight:700;color:#CBD5E1;text-transform:uppercase;margin-top:2px;">Physical Ingestion</div>
                <div style="font-size:0.72rem;color:#64748B;">Zero Synthetic Data</div>
            </div>
        </div>
    </div>
    """).strip())

    st.html("<div style='height:32px;'></div>")

    # ── 6. CALL-TO-ACTION & PROFESSIONAL FOOTER ──
    st.html(textwrap.dedent("""
    <div class="glass-panel" style="text-align:center;padding:28px 24px;border-color:rgba(34,211,238,0.35);">
        <h3 style="font-size:1.6rem;font-weight:800;color:#F1F5F9;margin:0 0 8px 0;letter-spacing:-0.4px;">
            Ready to Evaluate the AEROsense Platform?
        </h3>
        <p style="font-size:0.92rem;color:#94A3B8;max-width:620px;margin:0 auto 20px auto;line-height:1.6;">
            Access real-time sensor streams, interactive 3D WebGL isometric room models, 
            and statistical anomaly detection analytics.
        </p>
    </div>
    """).strip())

    cta_c1, cta_c2 = st.columns([1, 1])
    with cta_c1:
        if st.button("🚀 Sign In to Dashboard", type="primary", use_container_width=True, key="home_bottom_signin_btn"):
            st.session_state.public_nav = "login"
            st.rerun()
    with cta_c2:
        if st.button("📖 Read Engineering Documentation", type="secondary", use_container_width=True, key="home_bottom_about_btn"):
            st.session_state.public_nav = "about"
            st.rerun()

    # Footer
    st.html(textwrap.dedent("""
    <div style="border-top:1px solid rgba(255,255,255,0.06);margin-top:40px;padding-top:20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
        <div style="font-size:0.8rem;color:#64748B;">
            AEROsense v3.2 · B.Tech Computer Science and Engineering Capstone Project · ThingSpeak Channel ID: 3540991
        </div>
        <div style="font-size:0.78rem;color:#64748B;">
            Environmental Intelligence & IoT AI Platform
        </div>
    </div>
    """).strip())
