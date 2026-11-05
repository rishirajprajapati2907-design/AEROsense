"""
AEROsense SaaS Home Page — 60-30-10 Color Architecture
Color Distribution:
  - 60% Main: Deep Charcoal (#101820)
  - 30% Secondary: Soft Off-White (#E8EDEB)
  - 10% Accent: Electric Lime (#B7F34A)
Zero raw HTML/CSS leaks: uses st.html() and textwrap.dedent.
"""

import textwrap
import streamlit as st
import streamlit.components.v1 as components


def _render_3d_network_sphere():
    """
    Render the 3D Environmental Intelligence Network Sphere with 60-30-10 color styling.
    Features:
    - Deep charcoal background (#101820 / #16222F)
    - Electric Lime (#B7F34A) & Soft Off-White (#E8EDEB) particles
    - Atmospheric circulation orbital rings in Lime and Off-White
    - Continuous rotation and mouse parallax responsiveness
    """
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
            background: radial-gradient(circle at center, #16222F 0%, #101820 95%);
            font-family: -apple-system, BlinkMacSystemFont, "Plus Jakarta Sans", Roboto, sans-serif;
        }
        #network-sphere-container {
            width: 100%;
            height: 100%;
            position: relative;
            box-sizing: border-box;
            border-radius: 18px;
            border: 1px solid rgba(232, 237, 235, 0.16);
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6), inset 0 0 35px rgba(183, 243, 74, 0.06);
            overflow: hidden;
            cursor: grab;
        }
        #network-sphere-container:active {
            cursor: grabbing;
        }
        .sphere-hud-badge {
            position: absolute;
            top: 14px;
            left: 16px;
            font-size: 10.5px;
            font-weight: 800;
            color: #B7F34A;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            background: rgba(16, 24, 32, 0.9);
            padding: 4px 10px;
            border-radius: 6px;
            border: 1px solid rgba(183, 243, 74, 0.35);
            pointer-events: none;
            z-index: 10;
        }
        .sphere-hud-status {
            position: absolute;
            bottom: 12px;
            right: 14px;
            font-size: 10px;
            color: #E8EDEB;
            background: rgba(16, 24, 32, 0.9);
            padding: 3px 8px;
            border-radius: 4px;
            border: 1px solid rgba(232, 237, 235, 0.2);
            pointer-events: none;
            z-index: 10;
        }
    </style>
</head>
<body>
    <div id="network-sphere-container">
        <div class="sphere-hud-badge">Atmospheric Network · WebGL 3D</div>
        <div class="sphere-hud-status">● Real-time Telemetry Dynamics</div>
    </div>
    <script src="https://unpkg.com/three@0.128.0/build/three.min.js"></script>
    <script>
        (function() {
            const container = document.getElementById('network-sphere-container');
            if (!container) return;

            function initNetworkSphere() {
                if (typeof THREE === 'undefined') {
                    setTimeout(initNetworkSphere, 60);
                    return;
                }
                const width = container.clientWidth || 520;
                const height = container.clientHeight || 420;

                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
                camera.position.z = 175;

                const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
                renderer.setSize(width, height);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                container.appendChild(renderer.domElement);

                const networkGroup = new THREE.Group();
                scene.add(networkGroup);

                // 1. Core Atmospheric Nodes (Electric Lime & Soft Off-White)
                const nodeCount = 340;
                const nodePositions = [];
                const nodeColors = [];
                const cLime = new THREE.Color(0xB7F34A);
                const cOffWhite = new THREE.Color(0xE8EDEB);
                const cMuted = new THREE.Color(0x94A3B8);

                const radius = 54;
                for (let i = 0; i < nodeCount; i++) {
                    const phi = Math.acos(-1 + (2 * i) / nodeCount);
                    const theta = Math.sqrt(nodeCount * Math.PI) * phi;
                    const r = radius + (Math.random() - 0.5) * 6;
                    const x = r * Math.cos(theta) * Math.sin(phi);
                    const y = r * Math.sin(theta) * Math.sin(phi);
                    const z = r * Math.cos(phi);
                    nodePositions.push(new THREE.Vector3(x, y, z));

                    const rand = Math.random();
                    let col;
                    if (rand < 0.45) {
                        col = cLime.clone().lerp(cOffWhite, rand / 0.45);
                    } else {
                        col = cOffWhite.clone().lerp(cMuted, (rand - 0.45) / 0.55);
                    }
                    nodeColors.push(col.r, col.g, col.b);
                }

                const nodeGeo = new THREE.BufferGeometry();
                const posArr = new Float32Array(nodeCount * 3);
                for (let i = 0; i < nodeCount; i++) {
                    posArr[i * 3] = nodePositions[i].x;
                    posArr[i * 3 + 1] = nodePositions[i].y;
                    posArr[i * 3 + 2] = nodePositions[i].z;
                }
                nodeGeo.setAttribute('position', new THREE.BufferAttribute(posArr, 3));
                nodeGeo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(nodeColors), 3));

                const nodeMat = new THREE.PointsMaterial({
                    size: 2.8,
                    vertexColors: true,
                    transparent: true,
                    opacity: 0.92,
                    blending: THREE.AdditiveBlending
                });
                const nodePoints = new THREE.Points(nodeGeo, nodeMat);
                networkGroup.add(nodePoints);

                // 2. Interconnecting Lattice Lines (Electric Lime)
                const linePositions = [];
                const maxDistance = 17.0;

                for (let i = 0; i < nodeCount; i++) {
                    for (let j = i + 1; j < nodeCount; j++) {
                        const dist = nodePositions[i].distanceTo(nodePositions[j]);
                        if (dist < maxDistance) {
                            linePositions.push(nodePositions[i].x, nodePositions[i].y, nodePositions[i].z);
                            linePositions.push(nodePositions[j].x, nodePositions[j].y, nodePositions[j].z);
                        }
                    }
                }

                const lineGeo = new THREE.BufferGeometry();
                lineGeo.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
                const lineMat = new THREE.LineBasicMaterial({
                    color: 0xB7F34A,
                    transparent: true,
                    opacity: 0.28,
                    blending: THREE.AdditiveBlending
                });
                const networkLines = new THREE.LineSegments(lineGeo, lineMat);
                networkGroup.add(networkLines);

                // 3. Orbital Circulation Rings (Lime & Off-White)
                function createOrbitalRing(ringRadius, ringColor, tiltX, tiltY) {
                    const ringPoints = [];
                    const segments = 100;
                    for (let i = 0; i <= segments; i++) {
                        const theta = (i / segments) * Math.PI * 2;
                        ringPoints.push(new THREE.Vector3(Math.cos(theta) * ringRadius, Math.sin(theta) * ringRadius, 0));
                    }
                    const rGeo = new THREE.BufferGeometry().setFromPoints(ringPoints);
                    const rMat = new THREE.LineBasicMaterial({
                        color: ringColor,
                        transparent: true,
                        opacity: 0.40,
                        blending: THREE.AdditiveBlending
                    });
                    const ring = new THREE.Line(rGeo, rMat);
                    ring.rotation.x = tiltX;
                    ring.rotation.y = tiltY;
                    return ring;
                }

                const ring1 = createOrbitalRing(68, 0xB7F34A, Math.PI / 3, Math.PI / 6);
                const ring2 = createOrbitalRing(76, 0xE8EDEB, -Math.PI / 4, Math.PI / 3);
                const ring3 = createOrbitalRing(84, 0xA3E635, Math.PI / 6, -Math.PI / 4);
                networkGroup.add(ring1);
                networkGroup.add(ring2);
                networkGroup.add(ring3);

                // Mouse Interactivity
                let mouseX = 0, mouseY = 0;
                let targetX = 0, targetY = 0;
                window.addEventListener('mousemove', function(e) {
                    const rect = container.getBoundingClientRect();
                    mouseX = ((e.clientX - rect.left) / width - 0.5) * 0.5;
                    mouseY = ((e.clientY - rect.top) / height - 0.5) * 0.5;
                });

                function animate() {
                    requestAnimationFrame(animate);
                    targetX += (mouseX - targetX) * 0.05;
                    targetY += (mouseY - targetY) * 0.05;

                    networkGroup.rotation.y += 0.0028 + targetX * 0.01;
                    networkGroup.rotation.x += 0.0014 + targetY * 0.01;

                    ring1.rotation.z += 0.0018;
                    ring2.rotation.z -= 0.0015;
                    ring3.rotation.z += 0.0020;

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

            initNetworkSphere();
        })();
    </script>
</body>
</html>"""
    components.html(three_html, height=430)


def render_home_page():
    """Render the spacious, editorial AEROsense commercial SaaS landing page."""
    
    # ══════════════════════════════════════════════════════════════════════════
    # HERO SECTION (Two-Column Spacious Composition)
    # ══════════════════════════════════════════════════════════════════════════
    col_hero_left, col_hero_right = st.columns([1.25, 1.0], gap="large")

    with col_hero_left:
        st.html(textwrap.dedent("""
        <div style="padding: 12px 0 16px 0;">
            <div class="badge-tag">
                <span style="font-size:0.75rem;">●</span>
                <span>ENVIRONMENTAL INTELLIGENCE PLATFORM</span>
            </div>

            <h1 class="hero-title">
                Understand Your Air.<br>
                <span class="gradient-heading-lime">
                    Predict a Healthier Tomorrow.
                </span>
            </h1>

            <p class="body-editorial" style="max-width:540px;margin-bottom:28px;">
                Monitor indoor environmental conditions, explore pollutant trends and gain meaningful 
                insights through intelligent IoT-based monitoring.
            </p>
        </div>
        """).strip())

        # Exactly ONE prominent button (10% Accent: Electric Lime)
        btn_col, _ = st.columns([1.4, 2.0])
        with btn_col:
            if st.button("Explore Analytics ↗", type="primary", use_container_width=True, key="hero_explore_btn"):
                st.session_state.public_nav = "login"
                st.rerun()

        # Telemetry Highlights (30% Secondary & 10% Accent)
        st.html(textwrap.dedent("""
        <div style="display:flex;gap:18px;margin-top:36px;padding-top:20px;border-top:1px solid rgba(232,237,235,0.1);flex-wrap:wrap;">
            <div>
                <div style="font-size:1.35rem;font-weight:900;color:#B7F34A;">7 Channels</div>
                <div style="font-size:0.78rem;color:#E8EDEB;opacity:0.85;">Monitored Parameters</div>
            </div>
            <div style="border-left:1px solid rgba(232,237,235,0.12);padding-left:18px;">
                <div style="font-size:1.35rem;font-weight:900;color:#E8EDEB;">Continuous</div>
                <div style="font-size:0.78rem;color:#E8EDEB;opacity:0.85;">IoT Telemetry Sync</div>
            </div>
            <div style="border-left:1px solid rgba(232,237,235,0.12);padding-left:18px;">
                <div style="font-size:1.35rem;font-weight:900;color:#E8EDEB;">AI-Driven</div>
                <div style="font-size:0.78rem;color:#E8EDEB;opacity:0.85;">Predictive Trajectories</div>
            </div>
        </div>
        """).strip())

    with col_hero_right:
        st.html("<div style='height:8px;'></div>")
        _render_3d_network_sphere()

    st.html("<div style='height:72px;'></div>")

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 1 — THE PROBLEM
    # Heading: "Indoor Air Quality Is More Important Than We Realize."
    # Editorial layout with an environmental illustration (not a generic text card)
    # ══════════════════════════════════════════════════════════════════════════
    col_prob_text, col_prob_vis = st.columns([1.1, 1.0], gap="large")

    with col_prob_text:
        st.html(textwrap.dedent("""
        <div style="padding-right:12px;">
            <div class="badge-tag">
                <span>THE INVISIBLE CHALLENGE</span>
            </div>
            <h2 class="section-title">
                Indoor Air Quality Is More Important Than We Realize.
            </h2>
            <p class="body-editorial" style="margin-bottom:18px;">
                Most individuals spend over 85% of their daily lives inside enclosed spaces — homes, educational institutions, 
                and modern workspaces. Yet indoor air can hold concentrations of invisible pollutants and volatile compounds 
                several times higher than outdoor ambient levels.
            </p>
            <p class="body-editorial" style="margin-bottom:22px;">
                Combustion byproducts, particulate accumulation, and subtle gas shifts are completely imperceptible to human senses. 
                Without persistent digital sensing and temporal analysis, hazardous environmental shifts go unnoticed until comfort, 
                productivity, or long-term respiratory health is impacted.
            </p>
            <div style="display:flex;gap:12px;flex-wrap:wrap;">
                <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.25);padding:8px 14px;border-radius:10px;font-size:0.82rem;color:#FCA5A5;font-weight:600;">
                    ⚠️ Imperceptible Micro-Pollutants
                </div>
                <div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.25);padding:8px 14px;border-radius:10px;font-size:0.82rem;color:#FDE68A;font-weight:600;">
                    📈 Diurnal Accumulation Cycles
                </div>
            </div>
        </div>
        """).strip())

    with col_prob_vis:
        st.html(textwrap.dedent("""
        <div style="background:#16222F;border:1px solid rgba(232,237,235,0.16);border-radius:18px;padding:26px;position:relative;overflow:hidden;box-shadow:0 12px 36px rgba(0,0,0,0.45);">
            <!-- Atmospheric Dispersion Visualizer -->
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;border-bottom:1px solid rgba(232,237,235,0.08);padding-bottom:12px;">
                <span style="font-size:0.84rem;font-weight:700;color:#F1F5F9;">Enclosed Environment Stratification</span>
                <span style="font-size:0.72rem;color:#B7F34A;font-weight:700;">Spatial Diffusion Model</span>
            </div>
            
            <div style="display:flex;flex-direction:column;gap:14px;">
                <!-- Layer 1: Ceiling stagnation -->
                <div style="background:rgba(239,68,68,0.08);border-left:3px solid #EF4444;border-radius:0 8px 8px 0;padding:10px 14px;">
                    <div style="display:flex;justify-content:space-between;font-size:0.82rem;">
                        <span style="font-weight:700;color:#FCA5A5;">Upper Stratum · Thermal Stagnation</span>
                        <span style="color:#CBD5E1;font-size:0.75rem;">Convective Accumulation</span>
                    </div>
                    <div style="font-size:0.75rem;color:#94A3B8;margin-top:2px;">Rising warm air trapped without cross-ventilation.</div>
                </div>

                <!-- Layer 2: Breathing Zone -->
                <div style="background:rgba(245,158,11,0.08);border-left:3px solid #F59E0B;border-radius:0 8px 8px 0;padding:10px 14px;">
                    <div style="display:flex;justify-content:space-between;font-size:0.82rem;">
                        <span style="font-weight:700;color:#FDE68A;">Breathing Zone (1.0m – 1.8m)</span>
                        <span style="color:#B7F34A;font-size:0.75rem;">Primary Human Exposure</span>
                    </div>
                    <div style="font-size:0.75rem;color:#94A3B8;margin-top:2px;">Highest concentration of respirable aerosols and gaseous compounds.</div>
                </div>

                <!-- Layer 3: Floor Level -->
                <div style="background:rgba(183,243,74,0.08);border-left:3px solid #B7F34A;border-radius:0 8px 8px 0;padding:10px 14px;">
                    <div style="display:flex;justify-content:space-between;font-size:0.82rem;">
                        <span style="font-weight:700;color:#B7F34A;">Floor Boundary · Baseline Zone</span>
                        <span style="color:#CBD5E1;font-size:0.75rem;">Resuspension Risks</span>
                    </div>
                    <div style="font-size:0.75rem;color:#94A3B8;margin-top:2px;">Particulates re-entrained by foot traffic and HVAC airflows.</div>
                </div>
            </div>

            <div style="margin-top:18px;display:flex;justify-content:space-between;font-size:0.74rem;color:#94A3B8;">
                <span>Continuous Multi-Channel Monitoring</span>
                <span style="color:#B7F34A;font-weight:700;">● Actionable Sensor Insights</span>
            </div>
        </div>
        """).strip())

    st.html("<div style='height:64px;'></div>")

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 2 — OUR APPROACH
    # Heading: "Seven Parameters. One Intelligent Platform."
    # Clean horizontal icon-based showcase
    # ══════════════════════════════════════════════════════════════════════════
    st.html(textwrap.dedent("""
    <div style="text-align:center;margin-bottom:32px;">
        <div class="badge-tag">
            <span>MULTIVARIATE TELEMETRY</span>
        </div>
        <h2 class="section-title">
            Seven Parameters. One Intelligent Platform.
        </h2>
        <p class="section-subtitle" style="margin:0 auto;">
            A unified sensing suite capturing the full spectrum of indoor air dynamics — from ambient thermal comfort 
            to chemical vapors and fine inhalable particulates.
        </p>
    </div>
    """).strip())

    # 7 Parameters Showcase (Clean horizontal icon pills)
    p_row1 = st.columns(4)
    p_row2 = st.columns(3)

    params_data = [
        ("🌡️", "Temperature", "Thermal comfort & HVAC dynamics", "#F59E0B"),
        ("💧", "Humidity", "Moisture balance & vapor saturation", "#06B6D4"),
        ("💨", "Smoke", "Combustion byproducts & aerosols", "#8B5CF6"),
        ("⚠️", "Carbon Monoxide", "Hazardous odorless toxic gas detection", "#EF4444"),
        ("🧪", "Ammonia", "Chemical vapors & ambient amine tracing", "#A855F7"),
        ("🏭", "Nitrogen Oxides", "Combustion emissions & airborne oxidants", "#EAB308"),
        ("🌫️", "PM2.5", "Fine respirable particulate fractions", "#B7F34A"),
    ]

    target_cols = [p_row1[0], p_row1[1], p_row1[2], p_row1[3], p_row2[0], p_row2[1], p_row2[2]]
    for idx, (icon, name, desc, color) in enumerate(params_data):
        with target_cols[idx]:
            st.html(textwrap.dedent(f"""
            <div class="param-pill" style="border-left:3px solid {color};margin-bottom:12px;">
                <div class="param-icon">{icon}</div>
                <div>
                    <div class="param-name">{name}</div>
                    <div class="param-desc">{desc}</div>
                </div>
            </div>
            """).strip())

    st.html("<div style='height:64px;'></div>")

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 3 — HOW IT WORKS
    # Heading: "From Environmental Sensing to Intelligent Insights."
    # System: Sensors → ESP32 → ThingSpeak → Python Processing → AI Analytics → AEROsense.
    # ══════════════════════════════════════════════════════════════════════════
    st.html(textwrap.dedent("""
    <div style="text-align:center;margin-bottom:28px;">
        <div class="badge-tag">
            <span>CONNECTED PIPELINE</span>
        </div>
        <h2 class="section-title">
            From Environmental Sensing to Intelligent Insights.
        </h2>
        <p class="section-subtitle" style="margin:0 auto;">
            An integrated end-to-end telemetry architecture connecting physical hardware to automated cloud analysis.
        </p>
    </div>

    <div class="arch-flow-container">
        <!-- 1. Sensors -->
        <div class="arch-step-node">
            <div class="arch-node-num">STAGE 01</div>
            <div style="font-size:1.8rem;margin:6px 0;">🔬</div>
            <div style="font-weight:800;color:#F1F5F9;font-size:0.95rem;">Sensors</div>
            <div style="font-size:0.75rem;color:#B7F34A;margin-top:2px;">7 Physical Channels</div>
            <div style="font-size:0.72rem;color:#94A3B8;margin-top:4px;">Continuous Acquisition</div>
        </div>

        <div class="arch-arrow">→</div>

        <!-- 2. ESP32 -->
        <div class="arch-step-node">
            <div class="arch-node-num">STAGE 02</div>
            <div style="font-size:1.8rem;margin:6px 0;">⚡</div>
            <div style="font-weight:800;color:#F1F5F9;font-size:0.95rem;">ESP32</div>
            <div style="font-size:0.75rem;color:#B7F34A;margin-top:2px;">Microcontroller Node</div>
            <div style="font-size:0.72rem;color:#94A3B8;margin-top:4px;">Sampling & Wi-Fi Feed</div>
        </div>

        <div class="arch-arrow">→</div>

        <!-- 3. ThingSpeak -->
        <div class="arch-step-node">
            <div class="arch-node-num">STAGE 03</div>
            <div style="font-size:1.8rem;margin:6px 0;">☁️</div>
            <div style="font-weight:800;color:#F1F5F9;font-size:0.95rem;">ThingSpeak</div>
            <div style="font-size:0.75rem;color:#E8EDEB;margin-top:2px;">IoT Cloud Telemetry</div>
            <div style="font-size:0.72rem;color:#94A3B8;margin-top:4px;">Secure REST Repository</div>
        </div>

        <div class="arch-arrow">→</div>

        <!-- 4. Python Processing -->
        <div class="arch-step-node">
            <div class="arch-node-num">STAGE 04</div>
            <div style="font-size:1.8rem;margin:6px 0;">🐍</div>
            <div style="font-weight:800;color:#F1F5F9;font-size:0.95rem;">Python Engine</div>
            <div style="font-size:0.75rem;color:#E8EDEB;margin-top:2px;">Data Processing</div>
            <div style="font-size:0.72rem;color:#94A3B8;margin-top:4px;">Cleaning & Normalization</div>
        </div>

        <div class="arch-arrow">→</div>

        <!-- 5. AI Analytics -->
        <div class="arch-step-node">
            <div class="arch-node-num">STAGE 05</div>
            <div style="font-size:1.8rem;margin:6px 0;">🧠</div>
            <div style="font-weight:800;color:#F1F5F9;font-size:0.95rem;">AI Analytics</div>
            <div style="font-size:0.75rem;color:#B7F34A;margin-top:2px;">Trend Intelligence</div>
            <div style="font-size:0.72rem;color:#94A3B8;margin-top:4px;">Outlier Detection</div>
        </div>

        <div class="arch-arrow">→</div>

        <!-- 6. AEROsense -->
        <div class="arch-step-node" style="border-color:#B7F34A;box-shadow:0 0 25px rgba(183,243,74,0.18);">
            <div class="arch-node-num" style="background:#B7F34A;color:#101820;">STAGE 06</div>
            <div style="font-size:1.8rem;margin:6px 0;">🍃</div>
            <div style="font-weight:800;color:#B7F34A;font-size:0.95rem;">AEROsense</div>
            <div style="font-size:0.75rem;color:#F1F5F9;margin-top:2px;">Interactive SaaS</div>
            <div style="font-size:0.72rem;color:#94A3B8;margin-top:4px;">Spatial Visualizations</div>
        </div>
    </div>
    """).strip())

    st.html("<div style='height:64px;'></div>")

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 4 — PLATFORM CAPABILITIES
    # 4 main capabilities with 60-30-10 styling
    # ══════════════════════════════════════════════════════════════════════════
    st.html(textwrap.dedent("""
    <div style="text-align:center;margin-bottom:32px;">
        <div class="badge-tag">
            <span>CORE CAPABILITIES</span>
        </div>
        <h2 class="section-title">
            Intelligent Tools for Environmental Clarity
        </h2>
        <p class="section-subtitle" style="margin:0 auto;">
            Engineered to transform complex raw sensor signals into actionable environmental insights.
        </p>
    </div>
    """).strip())

    cap_col1, cap_col2 = st.columns(2, gap="large")

    with cap_col1:
        # Capability 1: Environmental Monitoring
        st.html(textwrap.dedent("""
        <div class="capability-card" style="border-top:3px solid #B7F34A;margin-bottom:24px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                <span style="font-size:1.6rem;">📡</span>
                <span style="font-size:0.7rem;font-weight:700;color:#B7F34A;background:rgba(183,243,74,0.12);padding:3px 8px;border-radius:4px;">
                    LIVE TELEMETRY
                </span>
            </div>
            <h3 style="font-size:1.25rem;font-weight:800;color:#F1F5F9;margin:0 0 8px 0;">
                Environmental Monitoring
            </h3>
            <p class="body-editorial" style="font-size:0.92rem;margin-bottom:14px;">
                Continuously tracks multi-channel sensor feeds with instantaneous status evaluations. Observes ambient 
                temperature, humidity equilibrium, combustion indicators, and particulate concentrations in real time.
            </p>
            <div style="display:flex;gap:8px;font-size:0.76rem;color:#B7F34A;font-weight:600;">
                <span>● Real-time updates</span> · <span>● Multi-channel telemetry</span> · <span>● Spatial awareness</span>
            </div>
        </div>
        """).strip())

        # Capability 2: AI Intelligence
        st.html(textwrap.dedent("""
        <div class="capability-card" style="border-top:3px solid #E8EDEB;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                <span style="font-size:1.6rem;">🧠</span>
                <span style="font-size:0.7rem;font-weight:700;color:#E8EDEB;background:rgba(232,237,235,0.1);padding:3px 8px;border-radius:4px;">
                    PREDICTIVE MODELING
                </span>
            </div>
            <h3 style="font-size:1.25rem;font-weight:800;color:#F1F5F9;margin:0 0 8px 0;">
                AI Intelligence
            </h3>
            <p class="body-editorial" style="font-size:0.92rem;margin-bottom:14px;">
                Employs statistical machine learning and diurnal curve analysis to forecast future air quality trajectories. 
                Helps anticipate accumulation periods and recommends timely ventilation intervention.
            </p>
            <div style="display:flex;gap:8px;font-size:0.76rem;color:#E8EDEB;font-weight:600;">
                <span>● Trend projection</span> · <span>● Diurnal modeling</span> · <span>● Confidence intervals</span>
            </div>
        </div>
        """).strip())

    with cap_col2:
        # Capability 3: Historical Analytics
        st.html(textwrap.dedent("""
        <div class="capability-card" style="border-top:3px solid #E8EDEB;margin-bottom:24px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                <span style="font-size:1.6rem;">📈</span>
                <span style="font-size:0.7rem;font-weight:700;color:#E8EDEB;background:rgba(232,237,235,0.1);padding:3px 8px;border-radius:4px;">
                    TEMPORAL INSIGHTS
                </span>
            </div>
            <h3 style="font-size:1.25rem;font-weight:800;color:#F1F5F9;margin:0 0 8px 0;">
                Historical Analytics
            </h3>
            <p class="body-editorial" style="font-size:0.92rem;margin-bottom:14px;">
                Delves into multi-week temporal profiles, cross-parameter correlation heatmaps, and hourly distribution curves 
                to isolate systemic environmental patterns across operating shifts.
            </p>
            <div style="display:flex;gap:8px;font-size:0.76rem;color:#E8EDEB;font-weight:600;">
                <span>● Time-series profiling</span> · <span>● Correlation heatmaps</span> · <span>● Baseline trends</span>
            </div>
        </div>
        """).strip())

        # Capability 4: Anomaly Detection
        st.html(textwrap.dedent("""
        <div class="capability-card" style="border-top:3px solid #F59E0B;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                <span style="font-size:1.6rem;">🛡️</span>
                <span style="font-size:0.7rem;font-weight:700;color:#F59E0B;background:rgba(245,158,11,0.1);padding:3px 8px;border-radius:4px;">
                    STATISTICAL OUTLIERS
                </span>
            </div>
            <h3 style="font-size:1.25rem;font-weight:800;color:#F1F5F9;margin:0 0 8px 0;">
                Anomaly Detection
            </h3>
            <p class="body-editorial" style="font-size:0.92rem;margin-bottom:14px;">
                Identifies sudden sensor spikes, frozen ADC readings, and statistical outliers exceeding standard thresholds (>3σ), 
                allowing rapid isolation of equipment faults or sudden gas releases.
            </p>
            <div style="display:flex;gap:8px;font-size:0.76rem;color:#F59E0B;font-weight:600;">
                <span>● Z-score outlier filter</span> · <span>● Severity categorization</span> · <span>● Audit event log</span>
            </div>
        </div>
        """).strip())

    st.html("<div style='height:64px;'></div>")

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 5 — DASHBOARD PREVIEW (60-30-10 Design)
    # Mockup frame in #101820 with #E8EDEB panels and #B7F34A accents
    # ══════════════════════════════════════════════════════════════════════════
    st.html(textwrap.dedent("""
    <div style="text-align:center;margin-bottom:28px;">
        <div class="badge-tag">
            <span>DASHBOARD WORKSPACE PREVIEW</span>
        </div>
        <h2 class="section-title">
            Engineered for Precision and Clarity
        </h2>
        <p class="section-subtitle" style="margin:0 auto;">
            A unified monitoring cockpit providing environmental awareness, temporal analytics, and spatial digital twins.
        </p>
    </div>

    <!-- Polished SaaS Mockup Window Frame -->
    <div class="mockup-frame">
        <div class="mockup-header">
            <div class="mockup-dots">
                <div class="mockup-dot" style="background:#EF4444;"></div>
                <div class="mockup-dot" style="background:#F59E0B;"></div>
                <div class="mockup-dot" style="background:#B7F34A;"></div>
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.8rem;color:#E8EDEB;background:rgba(16,24,32,0.8);padding:4px 14px;border-radius:6px;border:1px solid rgba(232,237,235,0.1);">
                <span>🔒</span>
                <span>aerosense.workspace/overview · Operator Terminal</span>
            </div>
            <div style="font-size:0.72rem;color:#101820;background:#B7F34A;font-weight:800;padding:3px 10px;border-radius:4px;">
                DEMO PREVIEW · Illustrative Interface
            </div>
        </div>

        <div style="padding:22px;">
            <!-- Mini Metric Strip (30% Secondary Soft Off-White Contrast) -->
            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(130px, 1fr));gap:10px;margin-bottom:18px;">
                <div style="background:#16222F;border:1px solid rgba(232,237,235,0.16);border-radius:10px;padding:12px;text-align:center;">
                    <div style="font-size:0.72rem;color:#E8EDEB;font-weight:700;">TEMPERATURE</div>
                    <div style="font-size:1.25rem;font-weight:800;color:#F59E0B;margin:2px 0;">23.4 °C</div>
                    <div style="font-size:0.68rem;color:#B7F34A;">● Nominal Band</div>
                </div>
                <div style="background:#16222F;border:1px solid rgba(232,237,235,0.16);border-radius:10px;padding:12px;text-align:center;">
                    <div style="font-size:0.72rem;color:#E8EDEB;font-weight:700;">HUMIDITY</div>
                    <div style="font-size:1.25rem;font-weight:800;color:#E8EDEB;margin:2px 0;">46.2 %</div>
                    <div style="font-size:0.68rem;color:#B7F34A;">● Optimal Comfort</div>
                </div>
                <div style="background:#16222F;border:1px solid rgba(232,237,235,0.16);border-radius:10px;padding:12px;text-align:center;">
                    <div style="font-size:0.72rem;color:#E8EDEB;font-weight:700;">SMOKE / AEROSOL</div>
                    <div style="font-size:1.25rem;font-weight:800;color:#E8EDEB;margin:2px 0;">182 ADC</div>
                    <div style="font-size:0.68rem;color:#B7F34A;">● Ambient Baseline</div>
                </div>
                <div style="background:#16222F;border:1px solid rgba(232,237,235,0.16);border-radius:10px;padding:12px;text-align:center;">
                    <div style="font-size:0.72rem;color:#E8EDEB;font-weight:700;">CARBON MONOXIDE</div>
                    <div style="font-size:1.25rem;font-weight:800;color:#EF4444;margin:2px 0;">1.8 ppm</div>
                    <div style="font-size:0.68rem;color:#B7F34A;">● Safe Threshold</div>
                </div>
                <div style="background:#16222F;border:1px solid rgba(232,237,235,0.16);border-radius:10px;padding:12px;text-align:center;">
                    <div style="font-size:0.72rem;color:#E8EDEB;font-weight:700;">PM2.5 AEROSOL</div>
                    <div style="font-size:1.25rem;font-weight:800;color:#B7F34A;margin:2px 0;">8.4 µg/m³</div>
                    <div style="font-size:0.68rem;color:#B7F34A;">● Clean Atmosphere</div>
                </div>
            </div>

            <!-- Visual Charts Mockup Grid -->
            <div style="display:grid;grid-template-columns:1.4fr 1fr;gap:14px;">
                <!-- Left: Multi-gas trendline with lime & off-white bars -->
                <div style="background:#101820;border:1px solid rgba(232,237,235,0.14);border-radius:10px;padding:16px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
                        <span style="font-size:0.86rem;font-weight:700;color:#F1F5F9;">Multi-Pollutant Diurnal Profile</span>
                        <span style="font-size:0.72rem;color:#B7F34A;font-weight:700;">Sample Aggregation</span>
                    </div>
                    <div style="height:120px;display:flex;align-items:flex-end;gap:8px;padding:8px 0;border-bottom:1px solid rgba(232,237,235,0.1);">
                        <div style="flex:1;height:35%;background:#E8EDEB;border-radius:3px 3px 0 0;opacity:0.75;"></div>
                        <div style="flex:1;height:55%;background:#B7F34A;border-radius:3px 3px 0 0;opacity:0.9;"></div>
                        <div style="flex:1;height:45%;background:#E8EDEB;border-radius:3px 3px 0 0;opacity:0.75;"></div>
                        <div style="flex:1;height:75%;background:#B7F34A;border-radius:3px 3px 0 0;opacity:0.95;"></div>
                        <div style="flex:1;height:65%;background:#E8EDEB;border-radius:3px 3px 0 0;opacity:0.75;"></div>
                        <div style="flex:1;height:40%;background:#CBD5E1;border-radius:3px 3px 0 0;opacity:0.65;"></div>
                        <div style="flex:1;height:50%;background:#B7F34A;border-radius:3px 3px 0 0;opacity:0.9;"></div>
                        <div style="flex:1;height:60%;background:#E8EDEB;border-radius:3px 3px 0 0;opacity:0.75;"></div>
                    </div>
                    <div style="display:flex;justify-content:space-between;font-size:0.7rem;color:#94A3B8;margin-top:6px;">
                        <span>00:00</span><span>04:00</span><span>08:00</span><span>12:00</span><span>16:00</span><span>20:00</span><span>23:59</span>
                    </div>
                </div>

                <!-- Right: Air Quality Ring & Status -->
                <div style="background:#101820;border:1px solid rgba(232,237,235,0.14);border-radius:10px;padding:16px;">
                    <div style="font-size:0.86rem;font-weight:700;color:#F1F5F9;margin-bottom:12px;">Air Quality Status</div>
                    <div style="display:flex;align-items:center;gap:16px;">
                        <div style="width:64px;height:64px;border-radius:50%;background:conic-gradient(#B7F34A 0% 84%, rgba(232,237,235,0.1) 84% 100%);display:flex;align-items:center;justify-content:center;">
                            <div style="width:50px;height:50px;border-radius:50%;background:#16222F;display:flex;align-items:center;justify-content:center;font-weight:900;color:#B7F34A;font-size:0.88rem;">
                                84%
                            </div>
                        </div>
                        <div>
                            <div style="color:#B7F34A;font-weight:800;font-size:1.05rem;">Good / Nominal</div>
                            <div style="font-size:0.74rem;color:#E8EDEB;opacity:0.85;margin-top:2px;">All parameters within normal ambient bands.</div>
                        </div>
                    </div>
                    <div style="margin-top:14px;padding-top:10px;border-top:1px solid rgba(232,237,235,0.08);font-size:0.74rem;color:#94A3B8;">
                        Anomaly Engine: <span style="color:#B7F34A;font-weight:700;">0 Critical Outliers Detected</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """).strip())

    st.html("<div style='height:72px;'></div>")

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 6 — FINAL CALL TO ACTION
    # Heading: "Explore Environmental Intelligence."
    # Button: "Explore Analytics" (10% Electric Lime Accent)
    # ══════════════════════════════════════════════════════════════════════════
    st.html(textwrap.dedent("""
    <div style="text-align:center;padding:48px 24px;background:#16222F;border:1px solid rgba(232,237,235,0.18);border-radius:20px;box-shadow:0 12px 40px rgba(0,0,0,0.5);">
        <div class="badge-tag">
            <span>GET STARTED</span>
        </div>
        <h2 style="font-size:clamp(1.9rem, 3.2vw, 2.6rem);font-weight:900;color:#F1F5F9;margin:6px 0 12px 0;letter-spacing:-0.5px;">
            Explore Environmental Intelligence.
        </h2>
        <p class="body-editorial" style="max-width:580px;margin:0 auto 26px auto;">
            Access real-time telemetry streaming, interactive 3D WebGL spatial models, and statistical anomaly detection.
        </p>
    </div>
    """).strip())

    st.html("<div style='height:16px;'></div>")
    cta_c1, cta_c2, cta_c3 = st.columns([1.2, 1.4, 1.2])
    with cta_c2:
        if st.button("Explore Analytics ↗", type="primary", use_container_width=True, key="cta_explore_analytics_btn"):
            st.session_state.public_nav = "login"
            st.rerun()

    st.html("<div style='height:64px;'></div>")

    # ══════════════════════════════════════════════════════════════════════════
    # COMMERCIAL SAAS FOOTER
    # Clean, professional footer.
    # ══════════════════════════════════════════════════════════════════════════
    st.html(textwrap.dedent("""
    <div style="border-top:1px solid rgba(232,237,235,0.1);padding-top:24px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:1.3rem;">🍃</span>
            <span style="font-weight:800;color:#F1F5F9;font-size:0.95rem;">
                <span style="color:#B7F34A;">AERO</span><span style="color:#E8EDEB;">sense</span>
            </span>
            <span style="font-size:0.75rem;color:#94A3B8;">· © 2026 Environmental Intelligence Platform</span>
        </div>
        <div style="font-size:0.76rem;color:#94A3B8;">
            Cloud Ingestion Engine · ThingSpeak Telemetry Protocol
        </div>
    </div>
    """).strip())
