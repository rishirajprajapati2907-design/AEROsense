"""
Unit & Integration Tests for AEROsense Internal Navigation Manager & Back Navigation Button
Tests:
- Initialization and session-state structure
- Chronological page traversal (Overview -> Live -> Historical -> Sensor Explorer -> AI)
- Deduplication during widget reruns on the same page
- Sequential Back navigation (AI -> Sensor Explorer -> Historical -> Live -> Overview)
- Root history boundary condition and disabled state rendering
- Security: External URL rejection and page name sanitization
- Max history depth limiting
- End-to-end AppTest execution of app.py across all dashboard pages
"""

import os
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import streamlit as st
from streamlit.testing.v1 import AppTest

from services.navigation_manager import (
    initialize_navigation_history,
    update_navigation_history,
    can_go_back,
    get_previous_page,
    go_back,
    navigate_to_previous_page,
    navigate_to_page,
    get_navigation_history,
    clear_navigation_history,
    VALID_PAGES,
    MAX_HISTORY_DEPTH,
)
from components.back_button import render_back_button


class TestNavigationManager(unittest.TestCase):
    def setUp(self):
        # Reset streamlit session state dictionary for each unit test
        for key in list(st.session_state.keys()):
            del st.session_state[key]

    def test_01_initialization(self):
        """Verify initialize_navigation_history sets up session state cleanly."""
        initialize_navigation_history()
        self.assertEqual(st.session_state.nav_page, "Overview")
        self.assertEqual(st.session_state.nav_history, ["Overview"])
        self.assertFalse(st.session_state._nav_is_back)
        self.assertFalse(can_go_back())
        self.assertIsNone(get_previous_page())

    def test_02_forward_navigation_sequence(self):
        """
        Verify forward sequence:
        Overview -> Live Monitoring -> Historical Analytics -> Sensor Explorer -> AI Intelligence
        """
        initialize_navigation_history()

        sequence = [
            "Live Monitoring",
            "Historical Analytics",
            "Sensor Explorer",
            "AI Intelligence",
        ]

        for page in sequence:
            st.session_state.nav_page = page
            update_navigation_history(page)

        expected_history = [
            "Overview",
            "Live Monitoring",
            "Historical Analytics",
            "Sensor Explorer",
            "AI Intelligence",
        ]

        self.assertEqual(get_navigation_history(), expected_history)
        self.assertTrue(can_go_back())
        self.assertEqual(get_previous_page(), "Sensor Explorer")

    def test_03_deduplication_on_repeated_reruns(self):
        """
        Verify that multiple reruns on the same page (e.g. widget interactions, filters)
        do not append duplicate entries to the navigation history.
        """
        initialize_navigation_history()
        st.session_state.nav_page = "Sensor Explorer"
        update_navigation_history("Sensor Explorer")

        # Simulate 10 widget interactions on Sensor Explorer
        for _ in range(10):
            update_navigation_history("Sensor Explorer")

        self.assertEqual(
            get_navigation_history(),
            ["Overview", "Sensor Explorer"],
        )
        self.assertEqual(len(get_navigation_history()), 2)

    @patch("streamlit.rerun")
    def test_04_sequential_back_navigation(self, mock_rerun):
        """
        Verify reverse sequence when user clicks Back:
        AI Intelligence -> Sensor Explorer -> Historical Analytics -> Live Monitoring -> Overview
        """
        initialize_navigation_history()

        # Build history
        for page in ["Live Monitoring", "Historical Analytics", "Sensor Explorer", "AI Intelligence"]:
            st.session_state.nav_page = page
            update_navigation_history(page)

        # 1. Back from AI Intelligence -> Sensor Explorer
        prev1 = go_back()
        self.assertEqual(prev1, "Sensor Explorer")
        self.assertEqual(st.session_state.nav_page, "Sensor Explorer")
        self.assertTrue(st.session_state._nav_is_back)

        # Simulate script rerun on Sensor Explorer
        update_navigation_history("Sensor Explorer")
        self.assertFalse(st.session_state._nav_is_back)
        self.assertEqual(get_previous_page(), "Historical Analytics")

        # 2. Back from Sensor Explorer -> Historical Analytics
        prev2 = go_back()
        self.assertEqual(prev2, "Historical Analytics")
        self.assertEqual(st.session_state.nav_page, "Historical Analytics")
        update_navigation_history("Historical Analytics")
        self.assertEqual(get_previous_page(), "Live Monitoring")

        # 3. Back from Historical Analytics -> Live Monitoring
        prev3 = go_back()
        self.assertEqual(prev3, "Live Monitoring")
        update_navigation_history("Live Monitoring")
        self.assertEqual(get_previous_page(), "Overview")

        # 4. Back from Live Monitoring -> Overview
        prev4 = go_back()
        self.assertEqual(prev4, "Overview")
        update_navigation_history("Overview")

        # 5. At Overview (root): cannot go back further
        self.assertFalse(can_go_back())
        self.assertIsNone(get_previous_page())
        prev5 = go_back()
        self.assertIsNone(prev5)
        self.assertEqual(get_navigation_history(), ["Overview"])

    def test_05_safety_invalid_page_rejection(self):
        """
        Security requirement:
        Verify that external URLs or unauthorized page names are rejected and sanitized to Overview.
        """
        initialize_navigation_history()

        # Attempt to navigate to an external malicious URL
        update_navigation_history("https://external-phishing-site.com")
        self.assertEqual(st.session_state.nav_page, "Overview")
        self.assertEqual(get_navigation_history(), ["Overview"])

        # Attempt to navigate to an unknown internal page
        update_navigation_history("UnauthorizedAdminView")
        self.assertEqual(st.session_state.nav_page, "Overview")

    @patch("streamlit.rerun")
    def test_06_navigate_to_page_helper(self, mock_rerun):
        """Verify programmatic navigation using navigate_to_page."""
        initialize_navigation_history()
        navigate_to_page("Reports")

        self.assertEqual(st.session_state.nav_page, "Reports")
        self.assertEqual(get_navigation_history(), ["Overview", "Reports"])
        self.assertTrue(mock_rerun.called)

    def test_07_max_history_depth_truncation(self):
        """Verify navigation history does not grow unbounded."""
        initialize_navigation_history()

        pages = list(VALID_PAGES)
        for i in range(MAX_HISTORY_DEPTH + 30):
            target = pages[i % len(pages)]
            st.session_state.nav_page = target
            update_navigation_history(target)

        self.assertLessEqual(len(get_navigation_history()), MAX_HISTORY_DEPTH)

    def test_08_clear_history(self):
        """Verify clear_navigation_history resets state to single root page."""
        initialize_navigation_history()
        st.session_state.nav_page = "Settings"
        update_navigation_history("Settings")
        self.assertEqual(len(get_navigation_history()), 2)

        clear_navigation_history("Overview")
        self.assertEqual(get_navigation_history(), ["Overview"])
        self.assertEqual(st.session_state.nav_page, "Overview")
        self.assertFalse(can_go_back())

    @patch("streamlit.button")
    def test_09_back_button_rendering(self, mock_button):
        """Verify render_back_button renders disabled at root and active with history."""
        mock_button.return_value = False

        # When no history and hide_when_empty=False (default): renders disabled button
        initialize_navigation_history()
        rendered = render_back_button()
        self.assertFalse(rendered)
        mock_button.assert_called_once()
        args, kwargs = mock_button.call_args
        self.assertEqual(args[0], "← Back")
        self.assertTrue(kwargs.get("disabled"))
        self.assertIsNone(kwargs.get("on_click"))

        # When history exists: renders enabled active button with callback
        mock_button.reset_mock()
        st.session_state.nav_page = "Live Monitoring"
        update_navigation_history("Live Monitoring")

        render_back_button()
        mock_button.assert_called_once()
        args, kwargs = mock_button.call_args
        self.assertEqual(args[0], "← Back")
        self.assertEqual(kwargs.get("help"), "Return to Overview")
        self.assertFalse(kwargs.get("disabled"))
        self.assertIsNotNone(kwargs.get("on_click"))

    def test_10_end_to_end_apptest_navigation(self):
        """
        Acceptance test via real Streamlit AppTest execution on app.py:
        1. Renders disabled Back button on initial Overview page.
        2. Navigates Overview -> Live Monitoring -> Sensor Explorer.
        3. Verifies Back button renders directly above Sensor Explorer heading.
        4. Verifies widget rerun inside Sensor Explorer does not duplicate history.
        5. Verifies clicking Back steps backwards: Sensor Explorer -> Live Monitoring -> Overview.
        6. Verifies Back button renders on ALL 11 dashboard pages without exceptions.
        """
        app_path = str(Path(__file__).resolve().parent.parent / "app.py")
        at = AppTest.from_file(app_path, default_timeout=90)
        at.session_state["authenticated"] = True
        at.session_state["current_user"] = {
            "name": "Test Operator",
            "email": "test@aerosense.local",
            "role": "Lead Systems Engineer",
            "initials": "TO",
            "is_guest": False,
        }
        at.run(timeout=120)
        self.assertFalse(at.exception, msg=f"AppTest Overview error: {at.exception}")

        # 1. Overview (root): Back button must be rendered and disabled
        back_btn = at.button(key="btn_back_navigation")
        self.assertEqual(back_btn.label, "← Back")
        self.assertTrue(back_btn.disabled)

        # 2. Navigate Overview -> Live Monitoring
        at.button(key="nav_Live Monitoring").click().run(timeout=30)
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["nav_page"], "Live Monitoring")
        back_btn = at.button(key="btn_back_navigation")
        self.assertFalse(back_btn.disabled)

        # 3. Navigate Live Monitoring -> Sensor Explorer
        at.button(key="nav_Sensor Explorer").click().run(timeout=30)
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["nav_page"], "Sensor Explorer")
        back_btn = at.button(key="btn_back_navigation")
        self.assertFalse(back_btn.disabled)
        self.assertEqual(
            list(at.session_state["nav_history"]),
            ["Overview", "Live Monitoring", "Sensor Explorer"],
        )

        # Verify heading appears below Back button on Sensor Explorer
        md_texts = [m.value for m in at.markdown]
        self.assertTrue(any("Sensor Channel Surveillance & Explorer" in t for t in md_texts))

        # 4. Widget interaction on Sensor Explorer must preserve history without duplication
        at.selectbox[0].select("field2").run(timeout=30)
        self.assertFalse(at.exception)
        self.assertEqual(
            list(at.session_state["nav_history"]),
            ["Overview", "Live Monitoring", "Sensor Explorer"],
        )

        # 5. Click Back: Sensor Explorer -> Live Monitoring
        at.button(key="btn_back_navigation").click().run(timeout=30)
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["nav_page"], "Live Monitoring")
        self.assertEqual(
            list(at.session_state["nav_history"]),
            ["Overview", "Live Monitoring"],
        )

        # Click Back: Live Monitoring -> Overview
        at.button(key="btn_back_navigation").click().run(timeout=30)
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["nav_page"], "Overview")
        self.assertEqual(list(at.session_state["nav_history"]), ["Overview"])
        self.assertTrue(at.button(key="btn_back_navigation").disabled)

        # 6. Verify Back button is visibly rendered on remaining dashboard pages
        for page_name in [
            "Historical Analytics",
            "3D Environment",
            "AI Intelligence",
            "Anomaly Detection",
            "Reports",
            "Notifications",
            "About Project",
            "Settings",
        ]:
            at.button(key=f"nav_{page_name}").click().run(timeout=30)
            self.assertFalse(at.exception, msg=f"Error on {page_name}: {at.exception}")
            self.assertEqual(at.session_state["nav_page"], page_name)
            btn = at.button(key="btn_back_navigation")
            self.assertEqual(btn.label, "← Back")
            self.assertFalse(btn.disabled)


if __name__ == "__main__":
    unittest.main()
