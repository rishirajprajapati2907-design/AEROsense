"""
AEROsense 3D Indoor Environmental & Atmospheric Visualization Component
Hardware-accelerated Three.js WebGL interactive 3D visualization.
Features:
  1. 3D Modern Indoor Room with IoT station & 7 interactive sensor markers.
  2. 3D Atmospheric Particle Sphere with cyan/teal gradient & mouse interactivity.
  3. Conceptual smooth airflow particle dynamics.
  4. Interactive HUD displaying actual real-time/historical telemetry on marker click.
  5. Graceful fallback for non-WebGL environments.
"""

import json
import streamlit.components.v1 as components


def render_indoor_room_3d(
    sensor_data: dict,
    status_color: str = "#B7F34A",
    status_text: str = "Nominal Air Flow",
    height: int = 460,
):
    """
    Render the 3D Interactive Indoor Environmental Room with IoT Node,
    7 Sensor Probes with real data, and conceptual airflow stream.
    """
    # Safe JSON dump of sensor telemetry for the WebGL scene
    payload_json = json.dumps(sensor_data)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                padding: 0;
                overflow: hidden;
                background: #101820;
                font-family: -apple-system, BlinkMacSystemFont, "Plus Jakarta Sans", "Segoe UI", Roboto, sans-serif;
            }}
            #viewport {{
                width: 100%;
                height: {height}px;
                position: relative;
                background: radial-gradient(circle at 50% 40%, #16222F 0%, #101820 100%);
                border-radius: 14px;
                border: 1px solid rgba(183, 243, 74, 0.25);
                box-shadow: inset 0 0 35px rgba(0, 0, 0, 0.65);
                cursor: grab;
            }}
            #viewport:active {{
                cursor: grabbing;
            }}
            .hud-overlay {{
                position: absolute;
                top: 14px;
                left: 18px;
                pointer-events: none;
                z-index: 10;
            }}
            .hud-title {{
                font-size: 11px;
                font-weight: 800;
                letter-spacing: 1.2px;
                text-transform: uppercase;
                color: #E8EDEB;
                opacity: 0.75;
                margin-bottom: 4px;
            }}
            .hud-status {{
                font-size: 13px;
                font-weight: 700;
                color: {status_color};
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            .pulse-dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background-color: {status_color};
                box-shadow: 0 0 10px {status_color};
                display: inline-block;
            }}
            .disclaimer-badge {{
                position: absolute;
                bottom: 12px;
                left: 18px;
                font-size: 10px;
                color: rgba(232, 237, 235, 0.65);
                background: rgba(22, 34, 47, 0.9);
                padding: 3px 8px;
                border-radius: 4px;
                border: 1px solid rgba(232, 237, 235, 0.1);
                pointer-events: none;
            }}
            .control-hint {{
                position: absolute;
                bottom: 12px;
                right: 18px;
                font-size: 10px;
                color: #B7F34A;
                background: rgba(22, 34, 47, 0.9);
                padding: 3px 8px;
                border-radius: 4px;
                border: 1px solid rgba(183, 243, 74, 0.3);
                pointer-events: none;
            }}
            #sensor-popup {{
                position: absolute;
                bottom: 44px;
                left: 18px;
                background: rgba(22, 34, 47, 0.96);
                border: 1px solid #B7F34A;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 12px;
                color: #E8EDEB;
                display: none;
                z-index: 20;
                box-shadow: 0 4px 20px rgba(0,0,0,0.5);
                max-width: 260px;
            }}
        </style>
        <script src="https://unpkg.com/three@0.128.0/build/three.min.js"></script>
    </head>
    <body>
        <div id="viewport">
            <div class="hud-overlay">
                <div class="hud-title">3D Interactive Indoor Monitoring Environment</div>
                <div class="hud-status">
                    <span class="pulse-dot"></span>
                    <span>{status_text}</span>
                </div>
            </div>
            <div class="disclaimer-badge">ℹ Particle flow is conceptual & illustrative</div>
            <div class="control-hint">🖱️ Click & Drag to Rotate · Scroll to Zoom · Click Markers for Telemetry</div>
            <div id="sensor-popup"></div>
        </div>

        <script>
            (function() {{
                const container = document.getElementById('viewport');
                const popup = document.getElementById('sensor-popup');
                const width = container.clientWidth || 600;
                const height = {height};
                const sensorData = {payload_json};

                // WebGL Check
                if (typeof THREE === 'undefined') {{
                    container.innerHTML = '<div style="color:#94a3b8;padding:40px;text-align:center;">WebGL engine initializing... If not rendering, check hardware acceleration in browser.</div>';
                    return;
                }}

                // Scene, Camera, Renderer
                const scene = new THREE.Scene();
                scene.fog = new THREE.FogExp2(0x101820, 0.0035);

                const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
                camera.position.set(0, 55, 145);
                camera.lookAt(0, 10, 0);

                const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
                renderer.setSize(width, height);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                container.appendChild(renderer.domElement);

                // Lighting
                const ambientLight = new THREE.AmbientLight(0x16222F, 1.4);
                scene.add(ambientLight);

                const spotLight = new THREE.SpotLight(0xB7F34A, 2.2);
                spotLight.position.set(30, 90, 40);
                spotLight.angle = Math.PI / 4;
                spotLight.penumbra = 0.4;
                scene.add(spotLight);

                const pointLight = new THREE.PointLight(0xE8EDEB, 1.2, 120);
                pointLight.position.set(0, 15, 0);
                scene.add(pointLight);

                // Room Floor Grid
                const gridHelper = new THREE.GridHelper(120, 24, 0xB7F34A, 0x1E2B3A);
                gridHelper.position.y = -15;
                scene.add(gridHelper);

                // Room Boundary Lines (Architectural Outline)
                const roomGeo = new THREE.BoxGeometry(110, 55, 90);
                const roomEdges = new THREE.EdgesGeometry(roomGeo);
                const roomLine = new THREE.LineSegments(roomEdges, new THREE.LineBasicMaterial({{ color: 0x243242, transparent: true, opacity: 0.7 }}));
                roomLine.position.y = 12.5;
                scene.add(roomLine);

                // Central IoT Pedestal & Monitoring Station
                const pedGeo = new THREE.CylinderGeometry(10, 12, 10, 16);
                const pedMat = new THREE.MeshStandardMaterial({{ color: 0x16222F, roughness: 0.4, metalness: 0.6 }});
                const pedestal = new THREE.Mesh(pedGeo, pedMat);
                pedestal.position.set(0, -10, 0);
                scene.add(pedestal);

                // IoT Station Box (ESP32 Gateway Model)
                const iotGeo = new THREE.BoxGeometry(14, 5, 10);
                const iotMat = new THREE.MeshStandardMaterial({{ color: 0x1E2B3A, roughness: 0.3, metalness: 0.8 }});
                const iotNode = new THREE.Mesh(iotGeo, iotMat);
                iotNode.position.set(0, -3.5, 0);
                scene.add(iotNode);

                // Glowing Station Antenna / Status Beacon
                const beaconGeo = new THREE.SphereGeometry(1.6, 16, 16);
                const beaconMat = new THREE.MeshBasicMaterial({{ color: '{status_color}' }});
                const beacon = new THREE.Mesh(beaconGeo, beaconMat);
                beacon.position.set(0, 1.5, 0);
                scene.add(beacon);

                // 7 Sensor Probes in Room
                const sensorConfigs = [
                    {{ id: 'field1', name: 'Temperature', pos: [32, 18, -25], color: 0xF59E0B, label: 'DHT22 Temp' }},
                    {{ id: 'field2', name: 'Humidity', pos: [-32, 18, -25], color: 0x06B6D4, label: 'DHT22 RH' }},
                    {{ id: 'field3', name: 'Smoke', pos: [0, 36, -10], color: 0x94A3B8, label: 'MQ-2 Smoke' }},
                    {{ id: 'field4', name: 'Carbon Monoxide', pos: [28, -2, 20], color: 0xEF4444, label: 'MQ-7 CO' }},
                    {{ id: 'field5', name: 'Ammonia NH3', pos: [-28, -8, 20], color: 0xA855F7, label: 'MQ-137 NH3' }},
                    {{ id: 'field6', name: 'Nitrogen Oxides', pos: [-38, 5, -8], color: 0xEAB308, label: 'MICS-6814 NOx' }},
                    {{ id: 'field7', name: 'PM2.5', pos: [0, 6, 0], color: 0xEC4899, label: 'PMS5003 PM2.5' }},
                ];

                const probeMeshes = [];
                sensorConfigs.forEach(cfg => {{
                    // Probe Anchor Sphere
                    const probeGeo = new THREE.SphereGeometry(2.5, 16, 16);
                    const probeMat = new THREE.MeshStandardMaterial({{
                        color: cfg.color,
                        emissive: cfg.color,
                        emissiveIntensity: 0.6,
                        roughness: 0.2
                    }});
                    const mesh = new THREE.Mesh(probeGeo, probeMat);
                    mesh.position.set(cfg.pos[0], cfg.pos[1], cfg.pos[2]);
                    mesh.userData = {{
                        id: cfg.id,
                        name: cfg.name,
                        label: cfg.label,
                        val: (sensorData[cfg.id] !== undefined && sensorData[cfg.id] !== null) ? sensorData[cfg.id] : '--'
                    }};
                    scene.add(mesh);
                    probeMeshes.push(mesh);

                    // Connecting tether wire to floor or node
                    const lineGeo = new THREE.BufferGeometry().setFromPoints([
                        new THREE.Vector3(cfg.pos[0], cfg.pos[1], cfg.pos[2]),
                        new THREE.Vector3(cfg.pos[0], -15, cfg.pos[2])
                    ]);
                    const tether = new THREE.Line(lineGeo, new THREE.LineBasicMaterial({{ color: 0x243242, transparent: true, opacity: 0.4 }}));
                    scene.add(tether);
                }});

                // Airflow Particle Field (Conceptual 320 smooth drifting particles)
                const particleCount = 340;
                const particleGeo = new THREE.BufferGeometry();
                const posArr = new Float32Array(particleCount * 3);
                const velArr = new Float32Array(particleCount * 3);

                for (let i = 0; i < particleCount; i++) {{
                    posArr[i * 3] = (Math.random() - 0.5) * 100;
                    posArr[i * 3 + 1] = Math.random() * 45 - 12;
                    posArr[i * 3 + 2] = (Math.random() - 0.5) * 80;

                    velArr[i * 3] = (Math.random() - 0.5) * 0.12;
                    velArr[i * 3 + 1] = Math.sin(i) * 0.05;
                    velArr[i * 3 + 2] = (Math.random() * 0.15) + 0.04;
                }}
                particleGeo.setAttribute('position', new THREE.BufferAttribute(posArr, 3));

                const particleMat = new THREE.PointsMaterial({{
                    color: 0xB7F34A,
                    size: 1.6,
                    transparent: true,
                    opacity: 0.65,
                    blending: THREE.AdditiveBlending
                }});
                const airflowStream = new THREE.Points(particleGeo, particleMat);
                scene.add(airflowStream);

                // Mouse Drag Orbit Controls
                let isDragging = false;
                let prevMousePos = {{ x: 0, y: 0 }};
                let rotY = 0;
                let rotX = 0.25;

                container.addEventListener('mousedown', (e) => {{
                    isDragging = true;
                    prevMousePos = {{ x: e.clientX, y: e.clientY }};
                }});

                window.addEventListener('mouseup', () => {{
                    isDragging = false;
                }});

                window.addEventListener('mousemove', (e) => {{
                    if (isDragging) {{
                        const deltaX = e.clientX - prevMousePos.x;
                        const deltaY = e.clientY - prevMousePos.y;
                        rotY += deltaX * 0.008;
                        rotX = Math.max(-0.2, Math.min(1.1, rotX + deltaY * 0.008));
                        prevMousePos = {{ x: e.clientX, y: e.clientY }};
                    }}
                }});

                // Raycasting for Marker Clicks
                const raycaster = new THREE.Raycaster();
                const mouse = new THREE.Vector2();

                container.addEventListener('click', (e) => {{
                    const rect = container.getBoundingClientRect();
                    mouse.x = ((e.clientX - rect.left) / width) * 2 - 1;
                    mouse.y = -((e.clientY - rect.top) / height) * 2 + 1;

                    raycaster.setFromCamera(mouse, camera);
                    const intersects = raycaster.intersectObjects(probeMeshes);

                    if (intersects.length > 0) {{
                        const hit = intersects[0].object.userData;
                        popup.style.display = 'block';
                        popup.innerHTML = `
                            <div style="font-weight:700;color:#B7F34A;margin-bottom:2px;">📍 ${{hit.label}}</div>
                            <div style="font-size:11px;color:rgba(232,237,235,0.7);">Field ID: ${{hit.id}}</div>
                            <div style="font-size:14px;font-weight:800;color:#E8EDEB;margin:4px 0;">Reading: ${{hit.val}}</div>
                            <div style="font-size:10px;color:#B7F34A;">● Telemetry Active · Click background to dismiss</div>
                        `;
                    }} else {{
                        popup.style.display = 'none';
                    }}
                }});

                // Animation Loop
                let clock = 0;
                function animate() {{
                    requestAnimationFrame(animate);
                    clock += 0.02;

                    // Camera positioning based on orbit angles
                    camera.position.x = Math.sin(rotY) * 140;
                    camera.position.z = Math.cos(rotY) * 140;
                    camera.position.y = 35 + (rotX * 65);
                    camera.lookAt(0, 8, 0);

                    // Pulse central station beacon
                    beacon.scale.setScalar(1 + Math.sin(clock * 3) * 0.18);

                    // Animate airflow particles
                    const positions = airflowStream.geometry.attributes.position.array;
                    for (let i = 0; i < particleCount; i++) {{
                        positions[i * 3 + 2] += velArr[i * 3 + 2];
                        positions[i * 3] += velArr[i * 3];

                        // Recycle particle when leaving room bounding box
                        if (positions[i * 3 + 2] > 45) positions[i * 3 + 2] = -45;
                        if (positions[i * 3] > 52) positions[i * 3] = -52;
                        if (positions[i * 3] < -52) positions[i * 3] = 52;
                    }}
                    airflowStream.geometry.attributes.position.needsUpdate = true;

                    // Subtle floating bobbing for probe markers
                    probeMeshes.forEach((mesh, idx) => {{
                        mesh.position.y += Math.sin(clock + idx) * 0.04;
                    }});

                    renderer.render(scene, camera);
                }}
                animate();

                // Responsive Resize
                window.addEventListener('resize', () => {{
                    const newW = container.clientWidth;
                    if (newW > 0) {{
                        camera.aspect = newW / height;
                        camera.updateProjectionMatrix();
                        renderer.setSize(newW, height);
                    }}
                }});
            }})();
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=height + 10)


def render_atmospheric_particle_sphere(
    status_color: str = "#B7F34A",
    status_text: str = "Optimal Dispersion",
    height: int = 380,
):
    """
    Render the 3D Atmospheric Particle Sphere with smooth rotating particle shell,
    electric lime/off-white accents and interactive hover drag.
    """
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                padding: 0;
                overflow: hidden;
                background: transparent;
                font-family: -apple-system, BlinkMacSystemFont, "Plus Jakarta Sans", "Segoe UI", Roboto, sans-serif;
            }}
            #canvas-box {{
                width: 100%;
                height: {height}px;
                position: relative;
                background: radial-gradient(circle at center, #16222F 0%, #101820 95%);
                border-radius: 14px;
                border: 1px solid rgba(183, 243, 74, 0.22);
                cursor: grab;
            }}
            #canvas-box:active {{
                cursor: grabbing;
            }}
            .hud-overlay {{
                position: absolute;
                top: 14px;
                left: 18px;
                pointer-events: none;
                z-index: 10;
            }}
            .hud-title {{
                font-size: 11px;
                font-weight: 800;
                letter-spacing: 1.2px;
                text-transform: uppercase;
                color: #E8EDEB;
                opacity: 0.75;
                margin-bottom: 3px;
            }}
            .hud-status {{
                font-size: 13px;
                font-weight: 700;
                color: {status_color};
            }}
            .hint-tag {{
                position: absolute;
                bottom: 12px;
                right: 18px;
                font-size: 10px;
                color: rgba(232, 237, 235, 0.5);
                pointer-events: none;
            }}
        </style>
        <script src="https://unpkg.com/three@0.128.0/build/three.min.js"></script>
    </head>
    <body>
        <div id="canvas-box">
            <div class="hud-overlay">
                <div class="hud-title">3D Atmospheric Particle Sphere</div>
                <div class="hud-status">● {status_text}</div>
            </div>
            <div class="hint-tag">Drag to Rotate · Mouse Responsive</div>
        </div>

        <script>
            (function() {{
                const container = document.getElementById('canvas-box');
                const width = container.clientWidth || 450;
                const height = {height};

                if (typeof THREE === 'undefined') {{
                    container.innerHTML = '<div style="color:#94a3b8;padding:30px;text-align:center;">Atmospheric 3D Engine Initializing...</div>';
                    return;
                }}

                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
                camera.position.z = 175;

                const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
                renderer.setSize(width, height);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                container.appendChild(renderer.domElement);

                // Core Sphere Particles
                const particleCount = 480;
                const geometry = new THREE.BufferGeometry();
                const positions = new Float32Array(particleCount * 3);
                const colors = new Float32Array(particleCount * 3);

                const cPrimary = new THREE.Color('{status_color}');
                const cSecondary = new THREE.Color(0xE8EDEB);

                const radius = 55;
                for (let i = 0; i < particleCount; i++) {{
                    const phi = Math.acos(-1 + (2 * i) / particleCount);
                    const theta = Math.sqrt(particleCount * Math.PI) * phi;

                    const rJitter = radius + (Math.random() - 0.5) * 8;
                    const x = rJitter * Math.cos(theta) * Math.sin(phi);
                    const y = rJitter * Math.sin(theta) * Math.sin(phi);
                    const z = rJitter * Math.cos(phi);

                    positions[i * 3] = x;
                    positions[i * 3 + 1] = y;
                    positions[i * 3 + 2] = z;

                    const mix = Math.random();
                    const mixedC = cPrimary.clone().lerp(cSecondary, mix);
                    colors[i * 3] = mixedC.r;
                    colors[i * 3 + 1] = mixedC.g;
                    colors[i * 3 + 2] = mixedC.b;
                }}

                geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
                geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

                const material = new THREE.PointsMaterial({{
                    size: 2.4,
                    vertexColors: true,
                    transparent: true,
                    opacity: 0.85,
                    blending: THREE.AdditiveBlending
                }});

                const sphere = new THREE.Points(geometry, material);
                scene.add(sphere);

                // Inner Glow Wireframe
                const innerGeo = new THREE.IcosahedronGeometry(48, 2);
                const innerMat = new THREE.MeshBasicMaterial({{
                    color: cPrimary,
                    wireframe: true,
                    transparent: true,
                    opacity: 0.12
                }});
                const innerMesh = new THREE.Mesh(innerGeo, innerMat);
                scene.add(innerMesh);

                // Interactive Mouse Rotation
                let isDragging = false;
                let prevMousePos = {{ x: 0, y: 0 }};

                container.addEventListener('mousedown', (e) => {{
                    isDragging = true;
                    prevMousePos = {{ x: e.clientX, y: e.clientY }};
                }});

                window.addEventListener('mouseup', () => {{
                    isDragging = false;
                }});

                window.addEventListener('mousemove', (e) => {{
                    if (isDragging) {{
                        const deltaX = e.clientX - prevMousePos.x;
                        const deltaY = e.clientY - prevMousePos.y;
                        sphere.rotation.y += deltaX * 0.01;
                        sphere.rotation.x += deltaY * 0.01;
                        innerMesh.rotation.y += deltaX * 0.01;
                        innerMesh.rotation.x += deltaY * 0.01;
                        prevMousePos = {{ x: e.clientX, y: e.clientY }};
                    }}
                }});

                function animate() {{
                    requestAnimationFrame(animate);
                    if (!isDragging) {{
                        sphere.rotation.y += 0.0035;
                        sphere.rotation.x += 0.0018;
                        innerMesh.rotation.y -= 0.002;
                    }}
                    renderer.render(scene, camera);
                }}
                animate();

                window.addEventListener('resize', () => {{
                    const newW = container.clientWidth;
                    if (newW > 0) {{
                        camera.aspect = newW / height;
                        camera.updateProjectionMatrix();
                        renderer.setSize(newW, height);
                    }}
                }});
            }})();
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=height + 8)
