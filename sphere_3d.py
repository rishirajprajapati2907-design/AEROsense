"""
AEROsense 3D Atmospheric Visualization Component
Lightweight, hardware-accelerated WebGL Three.js interactive atmospheric sphere.
Includes orbiting particles, environmental color glow, and smooth mouse-drag rotation.
"""

import streamlit.components.v1 as components


def render_atmospheric_sphere_3d(status_color: str = "#B7F34A", status_text: str = "Optimal Air Flow", height: int = 340):
    """
    Renders an interactive, lightweight 3D atmospheric sphere with floating particles.
    Color dynamically reflects air quality status.
    """
    # Map status color to secondary glow
    glow_color = "#E8EDEB" if status_color in ["#B7F34A", "#00D2FF", "#10B981"] else status_color

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
            #canvas-container {{
                width: 100%;
                height: {height}px;
                position: relative;
                background: radial-gradient(circle at center, #16222F 0%, #101820 100%);
                border-radius: 14px;
                border: 1px solid rgba(232, 237, 235, 0.12);
                box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.5);
                cursor: grab;
            }}
            #canvas-container:active {{
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
                font-weight: 700;
                letter-spacing: 1.2px;
                text-transform: uppercase;
                color: #E8EDEB;
                opacity: 0.75;
                margin-bottom: 3px;
            }}
            .hud-status {{
                font-size: 13px;
                font-weight: 600;
                color: {status_color};
                display: flex;
                align-items: center;
                gap: 6px;
            }}
            .hud-tag {{
                position: absolute;
                bottom: 12px;
                right: 18px;
                font-size: 10px;
                color: rgba(232, 237, 235, 0.5);
                pointer-events: none;
                letter-spacing: 0.5px;
            }}
            .pulse-dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background-color: {status_color};
                box-shadow: 0 0 8px {status_color};
                display: inline-block;
            }}
        </style>
        <!-- Load Three.js safely from unpkg with fallback -->
        <script src="https://unpkg.com/three@0.128.0/build/three.min.js"></script>
    </head>
    <body>
        <div id="canvas-container">
            <div class="hud-overlay">
                <div class="hud-title">3D Atmospheric Particle Dynamics</div>
                <div class="hud-status">
                    <span class="pulse-dot"></span>
                    <span>{status_text}</span>
                </div>
            </div>
            <div class="hud-tag">Drag to rotate • Real-time WebGL</div>
        </div>

        <script>
            (function() {{
                const container = document.getElementById('canvas-container');
                const width = container.clientWidth || 400;
                const height = {height};

                // Check if Three.js loaded
                if (typeof THREE === 'undefined') {{
                    container.innerHTML = '<div style="color:#94a3b8;padding:20px;text-align:center;">Atmospheric 3D Engine Initializing...</div>';
                    return;
                }}

                // Scene, Camera, Renderer
                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
                camera.position.z = 180;

                const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
                renderer.setSize(width, height);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                container.appendChild(renderer.domElement);

                // Group for full rotation
                const atmosphereGroup = new THREE.Group();
                scene.add(atmosphereGroup);

                // 1. Inner Wireframe Sphere (Earth / Room boundary)
                const sphereGeo = new THREE.IcosahedronGeometry(42, 3);
                const sphereMat = new THREE.MeshBasicMaterial({{
                    color: "{status_color}",
                    wireframe: true,
                    transparent: true,
                    opacity: 0.28
                }});
                const sphere = new THREE.Mesh(sphereGeo, sphereMat);
                atmosphereGroup.add(sphere);

                // 2. Subtle Core Glow Sphere
                const coreGeo = new THREE.SphereGeometry(39, 24, 24);
                const coreMat = new THREE.MeshBasicMaterial({{
                    color: "{glow_color}",
                    transparent: true,
                    opacity: 0.08
                }});
                const coreSphere = new THREE.Mesh(coreGeo, coreMat);
                atmosphereGroup.add(coreSphere);

                // 3. Floating Aerosol / Air Particles (320 particles)
                const particleCount = 320;
                const particleGeo = new THREE.BufferGeometry();
                const positions = new Float32Array(particleCount * 3);
                const scales = new Float32Array(particleCount);

                for (let i = 0; i < particleCount; i++) {{
                    const u = Math.random();
                    const v = Math.random();
                    const theta = u * 2.0 * Math.PI;
                    const phi = Math.acos(2.0 * v - 1.0);
                    const r = 50 + Math.random() * 35; // Cloud envelope radius 50-85

                    positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
                    positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
                    positions[i * 3 + 2] = r * Math.cos(phi);
                    scales[i] = Math.random() * 2.5 + 1.0;
                }}

                particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));

                // Canvas particle texture
                const canvas = document.createElement('canvas');
                canvas.width = 16;
                canvas.height = 16;
                const ctx = canvas.getContext('2d');
                const grad = ctx.createRadialGradient(8, 8, 0, 8, 8, 8);
                grad.addColorStop(0, 'rgba(255,255,255,1)');
                grad.addColorStop(0.4, '{status_color}');
                grad.addColorStop(1, 'rgba(0,0,0,0)');
                ctx.fillStyle = grad;
                ctx.fillRect(0, 0, 16, 16);

                const pTexture = new THREE.CanvasTexture(canvas);
                const particleMat = new THREE.PointsMaterial({{
                    size: 3.2,
                    map: pTexture,
                    transparent: true,
                    blending: THREE.AdditiveBlending,
                    depthWrite: false,
                    opacity: 0.85
                }});

                const particleSystem = new THREE.Points(particleGeo, particleMat);
                atmosphereGroup.add(particleSystem);

                // 4. Subtle Orbital Ring
                const ringGeo = new THREE.RingGeometry(62, 63, 64);
                const ringMat = new THREE.MeshBasicMaterial({{
                    color: "{status_color}",
                    side: THREE.DoubleSide,
                    transparent: true,
                    opacity: 0.15
                }});
                const ring = new THREE.Mesh(ringGeo, ringMat);
                ring.rotation.x = Math.PI / 2.3;
                atmosphereGroup.add(ring);

                // Mouse Interaction (Click & Drag Rotation)
                let isDragging = false;
                let previousMousePosition = {{ x: 0, y: 0 }};

                container.addEventListener('mousedown', (e) => {{
                    isDragging = true;
                    previousMousePosition = {{ x: e.clientX, y: e.clientY }};
                }});

                window.addEventListener('mouseup', () => {{
                    isDragging = false;
                }});

                window.addEventListener('mousemove', (e) => {{
                    if (!isDragging) return;
                    const deltaX = e.clientX - previousMousePosition.x;
                    const deltaY = e.clientY - previousMousePosition.y;

                    atmosphereGroup.rotation.y += deltaX * 0.008;
                    atmosphereGroup.rotation.x += deltaY * 0.008;

                    previousMousePosition = {{ x: e.clientX, y: e.clientY }};
                }});

                // Window Resize
                window.addEventListener('resize', () => {{
                    const newW = container.clientWidth;
                    camera.aspect = newW / height;
                    camera.updateProjectionMatrix();
                    renderer.setSize(newW, height);
                }});

                // Animation Loop (Smooth & Lightweight)
                let clock = new THREE.Clock();
                function animate() {{
                    requestAnimationFrame(animate);
                    const elapsedTime = clock.getElapsedTime();

                    if (!isDragging) {{
                        atmosphereGroup.rotation.y += 0.004;
                        atmosphereGroup.rotation.x = Math.sin(elapsedTime * 0.25) * 0.12;
                    }}

                    // Gentle breathing oscillation on particle system
                    particleSystem.rotation.y -= 0.002;
                    const scaleFactor = 1.0 + Math.sin(elapsedTime * 1.5) * 0.02;
                    particleSystem.scale.set(scaleFactor, scaleFactor, scaleFactor);

                    renderer.render(scene, camera);
                }}

                animate();
            }})();
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=height, scrolling=False)
