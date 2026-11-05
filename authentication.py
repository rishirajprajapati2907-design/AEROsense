"""
AEROsense Authentication Service (Frontend Foundation)
Provides clean session-based authentication management, state transitions,
and input validation ready for secure backend API & database integration.
"""

from typing import Dict, Any, Optional
import streamlit as st


def init_auth_session():
    """Initialize authentication session state defaults."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "login"  # "login", "register", "forgot", "reset"
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "auth_error" not in st.session_state:
        st.session_state.auth_error = None
    if "auth_success" not in st.session_state:
        st.session_state.auth_success = None


def is_authenticated() -> bool:
    """Check if active user is authenticated."""
    return st.session_state.get("authenticated", False)


def get_current_user() -> Dict[str, Any]:
    """Get active user metadata."""
    default_user = {
        "name": "IoT Operator",
        "email": "operator@aerosense.local",
        "role": "Lead Systems Engineer",
        "initials": "IO",
        "is_guest": True,
    }
    return st.session_state.get("current_user") or default_user


def authenticate_user(email: str, password: str) -> bool:
    """
    Authenticate user credentials.
    In Phase 1 frontend foundation:
      Validates format and accepts operator demo access.
      Structured for future backend hashing & database verification.
    """
    email_clean = email.strip().lower()
    if not email_clean:
        st.session_state.auth_error = "Please enter your email address."
        return False
    if not password:
        st.session_state.auth_error = "Please enter your password."
        return False

    # Extract name from email for friendly display
    username = email_clean.split("@")[0].replace(".", " ").title()
    initials = "".join([part[0].upper() for part in username.split()[:2]]) or "OP"

    st.session_state.authenticated = True
    st.session_state.current_user = {
        "name": username or "IoT Operator",
        "email": email_clean,
        "role": "Environmental Intelligence Specialist",
        "initials": initials,
        "is_guest": False,
    }
    st.session_state.auth_error = None
    st.session_state.auth_success = f"Welcome back, {username}!"
    return True


def enter_demo_access():
    """Quick operator / evaluator demo access for immediate dashboard demonstration."""
    st.session_state.authenticated = True
    st.session_state.current_user = {
        "name": "Operator Demo",
        "email": "demo@aerosense.ai",
        "role": "Guest Evaluator",
        "initials": "OD",
        "is_guest": True,
    }
    st.session_state.auth_error = None


def logout_user():
    """Log out active user and reset authentication state."""
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.auth_view = "login"
    st.session_state.public_nav = "home"
    st.session_state.auth_error = None
    st.session_state.auth_success = "Logged out successfully."
