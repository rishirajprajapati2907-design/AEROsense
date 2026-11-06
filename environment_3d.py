"""
AEROsense 3D Environment Page (Section 5 Requirements)
Dedicated interactive 3D digital twin room environment, probe markers,
conceptual airflow stream, and 3D atmospheric particle sphere.
"""

import streamlit as st
from components.indoor_room_3d import render_indoor_room_3d, render_atmospheric_particle_sphere
from data_loader import SENSORS


def render_environment_3d_page(latest_values: dict, overall_status: str, overall_color: str):
    """Render the dedicated 3D Interactive Environmental Visualizations."""
    st.markdown("""
    <div style="margin-bottom:14px;">
        <span style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#22D3EE;">
            Digital Twin & Spatial Intelligence
        </span>
        <h2 style="margin:2px 0 6px 0;font-size:1.6rem;color:#F1F5F9;font-weight:800;">
            Interactive 3D Indoor Monitoring Environment
        </h2>
        <div style="font-size:0.86rem;color:#94A3B8;">
            Hardware-accelerated Three.js WebGL simulation showing spatial IoT station placement, probe markers with live telemetry, and conceptual airflow stream dynamics.
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_room, tab_sphere = st.tabs(["🏛️ 3D Digital Twin Room & Probes", "🌐 3D Atmospheric Dispersion Sphere"])

    with tab_room:
        st.markdown("""
        <div class="alert-banner alert-info" style="margin-bottom:12px;">
            <span>💡</span>
            <div>
                <strong>3D Interactive Navigation:</strong> Click and drag to orbit the camera. 
                Click any <strong>Sensor Marker</strong> in the 3D scene to inspect real-time telemetry and channel diagnostics.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 3D Room Render
        render_indoor_room_3d(
            sensor_data=latest_values,
            status_color=overall_color,
            status_text=overall_status,
            height=500,
        )

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        # Probe placement legend
        st.markdown("#### 📍 Sensor Marker Placement Legend")
        lg_cols = st.columns(4)
        for idx, (fid, cfg) in enumerate(list(SENSORS.items())[:4]):
            val = latest_values.get(fid)
            val_str = f"{val:.{cfg['precision']}f} {cfg['unit']}" if val is not None else "--"
            with lg_cols[idx]:
                st.markdown(f"""
                <div class="glass-panel" style="padding:10px 14px;border-left:3px solid {cfg['color']};">
                    <div style="font-size:0.8rem;font-weight:700;color:#F1F5F9;">{cfg['icon']} {cfg['name']}</div>
                    <div style="font-size:1.1rem;font-weight:800;color:{cfg['color']};">{val_str}</div>
                    <div style="font-size:0.72rem;color:#64748B;">{cfg['description'][:45]}...</div>
                </div>
                """, unsafe_allow_html=True)

        lg_cols2 = st.columns(3)
        for idx, (fid, cfg) in enumerate(list(SENSORS.items())[4:]):
            val = latest_values.get(fid)
            val_str = f"{val:.{cfg['precision']}f} {cfg['unit']}" if val is not None else "--"
            with lg_cols2[idx]:
                st.markdown(f"""
                <div class="glass-panel" style="padding:10px 14px;border-left:3px solid {cfg['color']};">
                    <div style="font-size:0.8rem;font-weight:700;color:#F1F5F9;">{cfg['icon']} {cfg['name']}</div>
                    <div style="font-size:1.1rem;font-weight:800;color:{cfg['color']};">{val_str}</div>
                    <div style="font-size:0.72rem;color:#64748B;">{cfg['description'][:45]}...</div>
                </div>
                """, unsafe_allow_html=True)

    with tab_sphere:
        st.markdown("### 🌐 Atmospheric Dispersion Particle Sphere")
        st.caption("Rotating 480-particle WebGL shell reflecting multi-pollutant dispersion dynamics.")
        render_atmospheric_particle_sphere(
            status_color=overall_color,
            status_text=f"Aura State: {overall_status}",
            height=440,
        )
