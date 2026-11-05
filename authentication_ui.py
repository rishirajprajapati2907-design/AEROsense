"""
AEROsense Centered Authentication Component
Renders a centered, focused login experience with subtle 3D atmospheric dynamics,
clean empty inputs, password visibility toggle, registration, password recovery,
and Return Home navigation.
Zero raw HTML/CSS leaks: uses st.html() and textwrap.dedent.
"""

import textwrap
import streamlit as st
import streamlit.components.v1 as components
from services.authentication import (
    authenticate_user,
    enter_demo_access,
    init_auth_session,
)


def _render_ambient_auth_banner():
    """Render a lightweight, ambient 3D WebGL particle header banner."""
    banner_html = """<!DOCTYPE html>
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
        }
        #banner-canvas {
            width: 100%;
            height: 100%;
            position: relative;
            border-radius: 12px 12px 0 0;
            box-sizing: border-box;
        }
    </style>
</head>
<body>
    <div id="banner-canvas"></div>
    <script src="https://unpkg.com/three@0.128.0/build/three.min.js"></script>
    <script>
        (function() {
            const container = document.getElementById('banner-canvas');
            if (!container) return;

            function initBanner() {
                if (typeof THREE === 'undefined') {
                    setTimeout(initBanner, 50);
                    return;
                }
                const width = container.clientWidth || 460;
                const height = container.clientHeight || 120;

                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 1000);
                camera.position.z = 110;

                const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
                renderer.setSize(width, height);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                container.appendChild(renderer.domElement);

                // Wave Particle Field
                const count = 260;
                const geometry = new THREE.BufferGeometry();
                const positions = new Float32Array(count * 3);
                const colors = new Float32Array(count * 3);

                const c1 = new THREE.Color(0xB7F34A);
                const c2 = new THREE.Color(0xE8EDEB);

                for (let i = 0; i < count; i++) {
                    const u = (i / count) * Math.PI * 2;
                    const r = 32 + (Math.random() - 0.5) * 6;
                    positions[i * 3] = Math.cos(u) * r * 1.5;
                    positions[i * 3 + 1] = Math.sin(u) * r * 0.5 + (Math.random() - 0.5) * 6;
                    positions[i * 3 + 2] = (Math.random() - 0.5) * 20;

                    const mix = Math.random();
                    const col = c1.clone().lerp(c2, mix);
                    colors[i * 3] = col.r;
                    colors[i * 3 + 1] = col.g;
                    colors[i * 3 + 2] = col.b;
                }

                geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
                geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

                const material = new THREE.PointsMaterial({
                    size: 2.2,
                    vertexColors: true,
                    transparent: true,
                    opacity: 0.85,
                    blending: THREE.AdditiveBlending
                });

                const particles = new THREE.Points(geometry, material);
                scene.add(particles);

                function animate() {
                    requestAnimationFrame(animate);
                    particles.rotation.y += 0.003;
                    particles.rotation.z += 0.001;
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

            initBanner();
        })();
    </script>
</body>
</html>"""
    components.html(banner_html, height=125)


def render_auth_page():
    """Render the centered, focused authentication experience."""
    init_auth_session()
    view = st.session_state.get("auth_view", "login")

    # Center horizontally using balanced 3-column layout
    col_left, col_center, col_right = st.columns([1.0, 1.45, 1.0])

    with col_center:
        # Top Return Home link
        top_c1, top_c2 = st.columns([1, 1])
        with top_c1:
            if st.button("← Back to Home", key="btn_auth_return_home", help="Back to AEROsense Home"):
                st.session_state.public_nav = "home"
                st.session_state.auth_error = None
                st.rerun()
        with top_c2:
            st.html(textwrap.dedent("""
            <div style="text-align:right;font-size:0.75rem;color:#64748B;padding-top:8px;">
                Admin Portal
            </div>
            """).strip())

        st.html("<div style='height:8px;'></div>")

        # Glassmorphism Centered Card Container
        with st.container(border=True):
            # Ambient 3D WebGL Particle Header Banner
            _render_ambient_auth_banner()

            # Error Alert Banner
            if st.session_state.get("auth_error"):
                st.html(textwrap.dedent(f"""
                <div class="alert-banner alert-danger" style="margin: 14px 0;">
                    <span>⚠️</span>
                    <span>{st.session_state.auth_error}</span>
                </div>
                """).strip())

            # Success Alert Banner
            if st.session_state.get("auth_success"):
                st.html(textwrap.dedent(f"""
                <div class="alert-banner alert-info" style="margin: 14px 0;">
                    <span>✓</span>
                    <span>{st.session_state.auth_success}</span>
                </div>
                """).strip())

            # ─── 1. CENTERED LOGIN VIEW ───
            if view == "login":
                st.html(textwrap.dedent("""
                <div style="text-align:center;padding:12px 0 16px 0;">
                    <div style="display:inline-flex;align-items:center;gap:10px;margin-bottom:8px;">
                        <span style="font-size:1.8rem;filter:drop-shadow(0 0 10px rgba(183,243,74,0.4));">🍃</span>
                        <span style="font-size:1.75rem;font-weight:900;letter-spacing:-0.5px;">
                            <span style="color:#B7F34A;">AERO</span><span style="color:#E8EDEB;">sense</span>
                        </span>
                    </div>
                    <h2 style="font-size:1.45rem;font-weight:800;color:#F1F5F9;margin:0 0 6px 0;letter-spacing:-0.4px;">
                        Admin Authentication
                    </h2>
                    <div style="font-size:0.86rem;color:#94A3B8;line-height:1.5;max-width:380px;margin:0 auto;">
                        Enter your credentials to access the environmental intelligence workspace.
                    </div>
                </div>
                """).strip())

                # Clean, empty inputs without prefilled credentials
                login_email = st.text_input(
                    "Username or Email:",
                    placeholder="name@example.com",
                    value="",
                    key="auth_email",
                )

                # Password input with show/hide toggle
                c_pwd_head, c_pwd_toggle = st.columns([1.3, 1.0])
                with c_pwd_toggle:
                    show_pwd = st.checkbox("Show password", value=False, key="toggle_show_pwd")

                login_pwd = st.text_input(
                    "Password:",
                    type="default" if show_pwd else "password",
                    placeholder="••••••••••••",
                    value="",
                    key="auth_pwd",
                )

                # Remember Me & Forgot Password
                c_rem, c_forgot = st.columns([1, 1])
                with c_rem:
                    st.checkbox("Remember Me", value=True, key="rem_me")
                with c_forgot:
                    if st.button("Forgot Password?", key="link_forgot", help="Reset your account password"):
                        st.session_state.auth_view = "forgot"
                        st.session_state.auth_error = None
                        st.rerun()

                st.html("<div style='height:8px;'></div>")

                # Primary Action Button
                if st.button("Sign In to Admin Workspace", type="primary", use_container_width=True, key="btn_signin"):
                    success = authenticate_user(login_email, login_pwd)
                    if success:
                        st.rerun()

                st.html(textwrap.dedent("""
                <div style="text-align:center;font-size:0.75rem;color:#64748B;margin:16px 0 12px 0;letter-spacing:0.8px;font-weight:600;">
                    — FRONTEND DEMO AUTHENTICATION —
                </div>
                """).strip())

                # Clearly labelled frontend demo authentication flow
                if st.button(
                    "⚡ Instant Demo Sign In",
                    use_container_width=True,
                    key="btn_demo_access",
                    help="Direct access for evaluation and demonstration",
                ):
                    enter_demo_access()
                    st.rerun()

                st.html(textwrap.dedent("""
                <div style="text-align:center;margin-top:20px;margin-bottom:6px;font-size:0.84rem;color:#94A3B8;">
                    Need a new admin account?
                </div>
                """).strip())

                if st.button("Create Account →", use_container_width=True, key="link_to_register"):
                    st.session_state.auth_view = "register"
                    st.session_state.auth_error = None
                    st.rerun()

            # ─── 2. CENTERED REGISTRATION VIEW ───
            elif view == "register":
                st.html(textwrap.dedent("""
                <div style="text-align:center;padding:10px 0 16px 0;">
                    <div style="display:inline-flex;align-items:center;gap:10px;margin-bottom:8px;">
                        <span style="font-size:1.8rem;filter:drop-shadow(0 0 10px rgba(183,243,74,0.4));">🍃</span>
                        <span style="font-size:1.75rem;font-weight:900;letter-spacing:-0.5px;">
                            <span style="color:#B7F34A;">AERO</span><span style="color:#E8EDEB;">sense</span>
                        </span>
                    </div>
                    <h2 style="font-size:1.5rem;font-weight:800;color:#E8EDEB;margin:0 0 4px 0;letter-spacing:-0.4px;">
                        Create Account
                    </h2>
                    <div style="font-size:0.86rem;color:rgba(232,237,235,0.7);line-height:1.5;max-width:380px;margin:0 auto;">
                        Register for operator credentials on the AEROsense platform.
                    </div>
                </div>
                """).strip())

                reg_name = st.text_input("Full Name:", placeholder="Alex Mercer", value="", key="reg_name")
                reg_email = st.text_input("Work Email Address:", placeholder="alex@organization.org", value="", key="reg_email")
                reg_pwd = st.text_input("Password (min 6 chars):", type="password", placeholder="••••••••••••", value="", key="reg_pwd")
                reg_pwd2 = st.text_input("Confirm Password:", type="password", placeholder="••••••••••••", value="", key="reg_pwd2")

                terms_ok = st.checkbox(
                    "I agree to the Environmental Monitoring Terms & Data Privacy Policy.",
                    value=True,
                    key="reg_terms",
                )

                st.html("<div style='height:8px;'></div>")

                if st.button("Create Account", type="primary", use_container_width=True, key="btn_do_register"):
                    if not reg_name.strip():
                        st.session_state.auth_error = "Please enter your full name."
                        st.rerun()
                    elif not reg_email.strip() or "@" not in reg_email:
                        st.session_state.auth_error = "Please enter a valid email address."
                        st.rerun()
                    elif len(reg_pwd) < 6:
                        st.session_state.auth_error = "Password must be at least 6 characters long."
                        st.rerun()
                    elif reg_pwd != reg_pwd2:
                        st.session_state.auth_error = "Passwords do not match."
                        st.rerun()
                    elif not terms_ok:
                        st.session_state.auth_error = "You must accept the terms & data policy."
                        st.rerun()
                    else:
                        authenticate_user(reg_email, reg_pwd)
                        st.session_state.current_user["name"] = reg_name
                        st.rerun()

                st.html("<div style='height:6px;'></div>")
                if st.button("← Return to Sign In", use_container_width=True, key="reg_back_btn"):
                    st.session_state.auth_view = "login"
                    st.session_state.auth_error = None
                    st.rerun()

            # ─── 3. CENTERED FORGOT PASSWORD VIEW ───
            elif view == "forgot":
                st.html(textwrap.dedent("""
                <div style="text-align:center;padding:10px 0 16px 0;">
                    <div style="display:inline-flex;align-items:center;gap:10px;margin-bottom:8px;">
                        <span style="font-size:1.8rem;filter:drop-shadow(0 0 10px rgba(183,243,74,0.4));">🍃</span>
                        <span style="font-size:1.75rem;font-weight:900;letter-spacing:-0.5px;">
                            <span style="color:#B7F34A;">AERO</span><span style="color:#E8EDEB;">sense</span>
                        </span>
                    </div>
                    <h2 style="font-size:1.5rem;font-weight:800;color:#E8EDEB;margin:0 0 4px 0;letter-spacing:-0.4px;">
                        Reset Password
                    </h2>
                    <div style="font-size:0.86rem;color:rgba(232,237,235,0.7);line-height:1.5;max-width:380px;margin:0 auto;">
                        Enter your verified operator email to receive recovery instructions.
                    </div>
                </div>
                """).strip())

                forgot_email = st.text_input(
                    "Registered Email Address:",
                    placeholder="name@example.com",
                    value="",
                    key="forgot_email",
                )

                st.html("<div style='height:8px;'></div>")

                if st.button("Send Reset Instructions", type="primary", use_container_width=True, key="btn_send_reset"):
                    if not forgot_email or "@" not in forgot_email:
                        st.session_state.auth_error = "Please enter a valid email address."
                        st.rerun()
                    else:
                        st.session_state.auth_view = "reset"
                        st.session_state.auth_error = None
                        st.session_state.auth_success = f"Verification instructions sent to {forgot_email}."
                        st.rerun()

                st.html("<div style='height:6px;'></div>")
                if st.button("← Return to Sign In", use_container_width=True, key="forgot_back_btn"):
                    st.session_state.auth_view = "login"
                    st.session_state.auth_error = None
                    st.rerun()

            # ─── 4. CENTERED SET NEW PASSWORD VIEW ───
            elif view == "reset":
                st.html(textwrap.dedent("""
                <div style="text-align:center;padding:10px 0 16px 0;">
                    <div style="display:inline-flex;align-items:center;gap:10px;margin-bottom:8px;">
                        <span style="font-size:1.8rem;filter:drop-shadow(0 0 10px rgba(183,243,74,0.4));">🍃</span>
                        <span style="font-size:1.75rem;font-weight:900;letter-spacing:-0.5px;">
                            <span style="color:#B7F34A;">AERO</span><span style="color:#E8EDEB;">sense</span>
                        </span>
                    </div>
                    <h2 style="font-size:1.5rem;font-weight:800;color:#E8EDEB;margin:0 0 4px 0;letter-spacing:-0.4px;">
                        Set New Password
                    </h2>
                    <div style="font-size:0.86rem;color:rgba(232,237,235,0.7);line-height:1.5;max-width:380px;margin:0 auto;">
                        Choose a strong new password for your operator account.
                    </div>
                </div>
                """).strip())

                new_pwd = st.text_input("New Password:", type="password", placeholder="••••••••••••", value="", key="reset_new_pwd")
                new_pwd2 = st.text_input("Confirm New Password:", type="password", placeholder="••••••••••••", value="", key="reset_new_pwd2")

                st.html("<div style='height:8px;'></div>")

                if st.button("Update Password & Sign In", type="primary", use_container_width=True, key="btn_confirm_reset"):
                    if len(new_pwd) < 6:
                        st.session_state.auth_error = "Password must be at least 6 characters."
                        st.rerun()
                    elif new_pwd != new_pwd2:
                        st.session_state.auth_error = "Passwords do not match."
                        st.rerun()
                    else:
                        st.session_state.authenticated = True
                        st.session_state.auth_error = None
                        st.session_state.auth_success = "Password updated successfully!"
                        st.rerun()

                st.html("<div style='height:6px;'></div>")
                if st.button("← Return to Sign In", use_container_width=True, key="reset_back_btn"):
                    st.session_state.auth_view = "login"
                    st.session_state.auth_error = None
                    st.rerun()

        # Scientific Security Notice
        st.html(textwrap.dedent("""
        <div style="text-align:center;margin-top:16px;font-size:0.75rem;color:rgba(232,237,235,0.45);line-height:1.5;">
            🔒 Phase 1 Frontend Prototype: Session-based operator state.<br>
            Configured for OAuth2 / JWT backend token authentication in production.
        </div>
        """).strip())
