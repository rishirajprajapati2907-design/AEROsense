"""
Test verifying that Streamlit components execute using st.iframe and st.html
without deprecation warnings.
"""

import warnings
import pytest
from components.indoor_room_3d import render_indoor_room_3d, render_atmospheric_particle_sphere
from components.sphere_3d import render_atmospheric_sphere_3d
from components.authentication_ui import _render_ambient_auth_banner
from pages_app.home import _render_3d_network_sphere


def test_no_components_v1_deprecation_warnings():
    """Ensure calling 3D visualization components does not trigger components.v1 deprecation."""
    with warnings.catch_warnings(record=True) as recorded_warnings:
        warnings.simplefilter("always")

        # 1. Atmospheric sphere
        render_atmospheric_sphere_3d(status_color="#B7F34A", status_text="Nominal", height=300)

        # 2. Indoor room 3D
        dummy_data = {
            "field1": 24.5,
            "field2": 52.0,
            "field3": 412.0,
            "field4": 150.0,
            "field5": 85.0,
            "field6": 230.0,
            "field7": 45.0,
        }
        render_indoor_room_3d(sensor_data=dummy_data, status_color="#B7F34A", height=400)

        # 3. Atmospheric particle sphere
        render_atmospheric_particle_sphere(status_color="#B7F34A", status_text="Nominal", height=350)

        # 4. Ambient auth banner
        _render_ambient_auth_banner()

        # 5. Home 3D network sphere
        _render_3d_network_sphere()

        # Check that none of the recorded warnings mention st.components.v1.html or st.iframe
        deprecation_msgs = [
            str(w.message) for w in recorded_warnings
            if "components.v1.html" in str(w.message) or "st.components.v1" in str(w.message)
        ]
        assert len(deprecation_msgs) == 0, f"Found deprecation warnings: {deprecation_msgs}"
