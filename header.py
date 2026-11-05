"""
AEROsense Top Navigation & Header Component
Displays breadcrumb navigation, live date/time, telemetry status, notifications,
active operator profile, and logout action.
Zero raw HTML/CSS leaks: uses st.html() and textwrap.dedent.
"""

from datetime import datetime
import textwrap
import streamlit as st
from services.authentication import get_current_user, logout_user


def render_header(
    page_title: str = "Overview",
    is_live_mode: bool = False,
    connection_status: str = "HISTORICAL",
    data_source_label: str = "Historical Archive",
    notification_count: int = 0,
):
    """Render top application header with breadcrumbs and user controls."""
    now_str = datetime.now().strftime("%a, %b %d · %H:%M UTC")
    current_user = get_current_user()

    # Connection status badge
    if connection_status == "LIVE":
        status_html = "<span class='badge-pill badge-live'>● LIVE TELEMETRY</span>"
    elif connection_status == "STALE":
        status_html = "<span class='badge-pill badge-stale'>● STALE</span>"
    elif connection_status == "OFFLINE":
        status_html = "<span class='badge-pill badge-offline'>● OFFLINE</span>"
    else:
        status_html = "<span class='badge-pill badge-hist'>● HISTORICAL DATA</span>"

    c_left, c_right = st.columns([1.8, 2.2])

    with c_left:
        st.html(textwrap.dedent(f"""
        <div style="display:flex;align-items:center;gap:12px;padding:6px 0;">
            <span style="font-size:1.6rem;filter:drop-shadow(0 0 8px rgba(183,243,74,0.35));">🍃</span>
            <div>
                <div style="font-size:0.75rem;color:rgba(232,237,235,0.6);font-weight:600;letter-spacing:0.5px;text-transform:uppercase;">
                    AEROsense Platform / <span style="color:#B7F34A;">{page_title}</span>
                </div>
                <div style="font-size:1.4rem;font-weight:800;color:#E8EDEB;letter-spacing:-0.4px;">
                    {page_title}
                </div>
            </div>
        </div>
        """).strip())

    with c_right:
        h1, h2, h3, h4 = st.columns([1.1, 1.1, 1.2, 0.7])
        with h1:
            st.html(textwrap.dedent(f"""
            <div style="text-align:right;font-size:0.78rem;color:#E8EDEB;padding-top:10px;">
                <div>🕒 {now_str}</div>
                <div style="color:rgba(232,237,235,0.55);font-size:0.72rem;">{data_source_label}</div>
            </div>
            """).strip())
        with h2:
            st.html(textwrap.dedent(f"""
            <div style="text-align:right;padding-top:14px;">
                {status_html}
            </div>
            """).strip())
        with h3:
            st.html(textwrap.dedent(f"""
            <div class="user-badge" style="margin-top:10px;justify-content:center;">
                <span class="user-avatar">{current_user.get('initials', 'OP')}</span>
                <span style="font-weight:600;font-size:0.76rem;">{current_user.get('name', 'Operator')}</span>
            </div>
            """).strip())
        with h4:
            if st.button("🚪 Logout", key="btn_header_logout", help="Sign out of AEROsense"):
                logout_user()
                st.rerun()

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)


# Alias for backward compatibility
def render_top_navbar(*args, **kwargs):
    page_title = kwargs.get("page_title", "Overview")
    render_header(page_title=page_title, **{k: v for k, v in kwargs.items() if k != "page_title"})
