"""
AEROsense Top Navigation Component
Renders the enterprise header with branding, real-time status, timestamp, and profile indicator.
"""

from datetime import datetime
import streamlit as st


def render_top_navbar(
    is_live_mode: bool = False,
    connection_status: str = "HISTORICAL",
    data_source_label: str = "Historical Archive (5,024 Records)",
    last_updated_str: str = "",
    notification_count: int = 0,
):
    """Render top navigation bar."""
    now_str = datetime.now().strftime("%a, %b %d %Y · %H:%M:%S")
    
    # Status badge styling
    if connection_status == "LIVE":
        status_html = "<span class='badge-pill badge-live'>● LIVE STREAM</span>"
    elif connection_status == "STALE":
        status_html = "<span class='badge-pill badge-stale'>● STALE TELEMETRY</span>"
    elif connection_status == "OFFLINE":
        status_html = "<span class='badge-pill badge-offline'>● OFFLINE</span>"
    else:
        status_html = "<span class='badge-pill badge-hist'>● HISTORICAL DATA</span>"

    notif_badge = f"<span style='background:#EF4444;color:#fff;font-size:0.65rem;padding:1px 5px;border-radius:10px;margin-left:4px;'>{notification_count}</span>" if notification_count > 0 else ""

    html = f"""
    <div class="top-nav-bar">
        <div class="top-nav-brand">
            <span style="font-size:1.5rem;">🍃</span>
            <div>
                <span class="top-nav-title">AEROsense</span>
                <span class="top-nav-tag" style="margin-left:8px;">Enterprise Platform</span>
            </div>
        </div>
        <div class="top-nav-meta">
            <div class="top-nav-item">
                <span>🕒</span>
                <span>{now_str}</span>
            </div>
            <div class="top-nav-item">
                <span>📂</span>
                <span style="color:#22D3EE;">{data_source_label}</span>
            </div>
            <div class="top-nav-item">
                {status_html}
            </div>
            <div class="top-nav-item" style="cursor:pointer;" title="Alerts & System Notifications">
                <span>🔔</span>
                {notif_badge}
            </div>
            <div class="user-badge">
                <span class="user-avatar">AG</span>
                <span>IoT Operator</span>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
