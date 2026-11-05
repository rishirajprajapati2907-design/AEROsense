"""
AEROsense Design System — Professional 60-30-10 Color Architecture
Theme: Deep Midnight & Environmental Intelligence
Color Distribution:
  - 60% MAIN: Deep Charcoal (#101820)
    Primary backgrounds, navigation shell, sidebar, and major interface canvas.
  - 30% SECONDARY: Soft Off-White (#E8EDEB)
    Content surfaces, readable editorial sections, panels, cards, and secondary contrast.
  - 10% ACCENT: Electric Lime (#B7F34A)
    Selectively applied to primary CTA buttons, active navigation, glowing status dots,
    and key interactive highlights.
"""

PALETTE_60_30_10 = {
    # 60% MAIN (Deep Charcoal)
    "main": "#101820",
    "main_darker": "#0C131A",
    "main_surface": "#16222F",
    "main_card": "#151F2A",
    
    # 30% SECONDARY (Soft Off-White)
    "secondary": "#E8EDEB",
    "secondary_surface": "#F4F7F6",
    "secondary_muted": "#CBD5E1",
    "secondary_border": "rgba(232, 237, 235, 0.16)",
    "text_dark": "#101820",
    
    # 10% ACCENT (Electric Lime)
    "accent": "#B7F34A",
    "accent_hover": "#C8F76B",
    "accent_glow": "rgba(183, 243, 74, 0.35)",
    "accent_subtle": "rgba(183, 243, 74, 0.12)",
    "accent_border": "rgba(183, 243, 74, 0.38)",
    
    # Standard Scientific Status Colors
    "text_main": "#F1F5F9",
    "text_secondary": "#94A3B8",
    "success": "#B7F34A",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "info": "#38BDF8",
}

# Backward compatibility aliases
STRATUM_PALETTE = PALETTE_60_30_10
MIDNIGHT_PALETTE = PALETTE_60_30_10

THEME_CSS = """
<style>
/* ── Typography & Global Reset ── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

/* 60% MAIN: Deep Charcoal Background */
.stApp {
    background-color: #101820 !important;
    color: #F1F5F9 !important;
}

.block-container {
    padding: 1.2rem 2.2rem 3rem !important;
    max-width: 1720px !important;
}

/* ── Typography & Gradient Headings ── */
.gradient-heading-lime {
    background: linear-gradient(135deg, #FFFFFF 0%, #E8EDEB 45%, #B7F34A 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline-block;
}

.gradient-heading-purple {
    background: linear-gradient(135deg, #FFFFFF 0%, #E8EDEB 50%, #B7F34A 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline-block;
}

.gradient-heading {
    background: linear-gradient(135deg, #B7F34A 0%, #E8EDEB 50%, #FFFFFF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline-block;
}

/* 10% ACCENT: Badges & Tags */
.badge-tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(183, 243, 74, 0.1);
    border: 1px solid rgba(183, 243, 74, 0.35);
    color: #B7F34A;
    font-size: 0.74rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 5px 14px;
    border-radius: 24px;
    margin-bottom: 14px;
}

.badge-tag-purple {
    background: rgba(232, 237, 235, 0.08);
    border: 1px solid rgba(232, 237, 235, 0.25);
    color: #E8EDEB;
}

/* ── SaaS Navigation Bar ── */
.saas-navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #16222F;
    border: 1px solid rgba(232, 237, 235, 0.16);
    border-radius: 16px;
    padding: 12px 24px;
    margin-bottom: 1.8rem;
    box-shadow: 0 8px 36px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(18px);
}

/* ── 30% SECONDARY: Soft Off-White Editorial Panels ── */
.surface-secondary {
    background: #E8EDEB !important;
    color: #101820 !important;
    border-radius: 18px !important;
    padding: 26px 28px !important;
    box-shadow: 0 10px 36px rgba(0, 0, 0, 0.35) !important;
    margin-bottom: 20px !important;
}

.surface-secondary h1,
.surface-secondary h2,
.surface-secondary h3,
.surface-secondary h4 {
    color: #101820 !important;
}

.surface-secondary p,
.surface-secondary span,
.surface-secondary div {
    color: #1E293B;
}

/* ── Modern Glassmorphism Cards ── */
.glass-panel {
    background: linear-gradient(135deg, rgba(22, 34, 47, 0.9) 0%, rgba(16, 24, 32, 0.98) 100%);
    border: 1px solid rgba(232, 237, 235, 0.15);
    border-radius: 16px;
    padding: 22px 26px;
    box-shadow: 0 6px 30px rgba(0, 0, 0, 0.45);
    backdrop-filter: blur(16px);
    transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
    margin-bottom: 16px;
}

.glass-panel:hover {
    border-color: rgba(183, 243, 74, 0.4);
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.55), 0 0 24px rgba(183, 243, 74, 0.1);
    transform: translateY(-2px);
}

/* ── Feature Cards (60-30-10 Grid) ── */
.feature-card {
    background: #16222F;
    border: 1px solid rgba(232, 237, 235, 0.14);
    border-radius: 16px;
    padding: 24px 22px;
    height: 100%;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
    overflow: hidden;
    box-sizing: border-box;
}

.feature-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #B7F34A 0%, #E8EDEB 100%);
    opacity: 0.7;
    transition: opacity 0.25s ease;
}

.feature-card:hover {
    transform: translateY(-4px);
    border-color: rgba(183, 243, 74, 0.45);
    box-shadow: 0 14px 40px rgba(0, 0, 0, 0.55), 0 0 28px rgba(183, 243, 74, 0.15);
}

.feature-card:hover::before {
    opacity: 1;
}

.feature-icon-wrapper {
    width: 46px;
    height: 46px;
    border-radius: 12px;
    background: rgba(183, 243, 74, 0.12);
    border: 1px solid rgba(183, 243, 74, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    margin-bottom: 16px;
}

.feature-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #F1F5F9;
    letter-spacing: -0.3px;
    margin-bottom: 8px;
}

.feature-desc {
    font-size: 0.88rem;
    color: #94A3B8;
    line-height: 1.6;
}

/* ── Interactive Sensor KPI Cards ── */
.sensor-card {
    background: #16222F;
    border: 1px solid rgba(232, 237, 235, 0.15);
    border-radius: 14px;
    padding: 16px 18px 12px 18px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
    transition: all 0.22s ease;
    position: relative;
    overflow: hidden;
    margin-bottom: 12px;
}

.sensor-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--sensor-accent, #B7F34A);
}

.sensor-card:hover {
    transform: translateY(-3px);
    border-color: rgba(183, 243, 74, 0.5);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5), 0 0 20px rgba(183, 243, 74, 0.12);
}

.sensor-card-value {
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.6px;
    line-height: 1.1;
    color: #F8FAFC;
}

.sensor-card-unit {
    font-size: 0.86rem;
    font-weight: 500;
    color: #94A3B8;
    margin-left: 4px;
}

/* ── Centered Admin Login Card ── */
.admin-card-container {
    max-width: 480px;
    margin: 0 auto;
    background: #16222F;
    border: 1px solid rgba(232, 237, 235, 0.18);
    border-radius: 18px;
    padding: 32px 30px;
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.65), 0 0 30px rgba(183, 243, 74, 0.1);
    backdrop-filter: blur(20px);
}

/* ── Left Sidebar Overrides (60% Main Deep Charcoal) ── */
[data-testid="stSidebar"] {
    background: #0C131A !important;
    border-right: 1px solid rgba(232, 237, 235, 0.1) !important;
}

[data-testid="stSidebar"] * {
    color: #CBD5E1 !important;
}

.sidebar-brand-box {
    padding: 8px 6px 16px 6px;
    border-bottom: 1px solid rgba(232, 237, 235, 0.1);
    margin-bottom: 14px;
}

.sidebar-title {
    font-size: 1.45rem;
    font-weight: 900;
    letter-spacing: -0.5px;
    color: #B7F34A !important;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.sidebar-subtitle {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #E8EDEB !important;
    margin-top: 3px;
}

/* ── Authenticated Top Bar ── */
.top-nav-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #16222F;
    border: 1px solid rgba(232, 237, 235, 0.15);
    border-radius: 14px;
    padding: 12px 22px;
    margin-bottom: 1.25rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(16px);
}

.user-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #101820;
    border: 1px solid rgba(183, 243, 74, 0.35);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    color: #E2E8F0;
}

.user-avatar {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: #B7F34A;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 0.65rem;
    color: #101820;
}

/* ── Badges ── */
.badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 9px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.badge-live {
    background: rgba(183, 243, 74, 0.15);
    color: #B7F34A;
    border: 1px solid rgba(183, 243, 74, 0.5);
}

.badge-offline {
    background: rgba(239, 68, 68, 0.15);
    color: #EF4444;
    border: 1px solid rgba(239, 68, 68, 0.5);
}

.badge-stale {
    background: rgba(245, 158, 11, 0.15);
    color: #F59E0B;
    border: 1px solid rgba(245, 158, 11, 0.5);
}

.badge-hist {
    background: rgba(232, 237, 235, 0.12);
    color: #E8EDEB;
    border: 1px solid rgba(232, 237, 235, 0.4);
}

/* ── Streamlit UI Elements: 10% Electric Lime Primary Action ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

div[data-testid="stButton"] > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background: #B7F34A !important;
    color: #101820 !important;
    font-weight: 800 !important;
    border: none !important;
    box-shadow: 0 4px 18px rgba(183, 243, 74, 0.35) !important;
}

div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #C8F76B !important;
    box-shadow: 0 6px 26px rgba(183, 243, 74, 0.55) !important;
    transform: translateY(-1px) !important;
    color: #101820 !important;
}

div[data-testid="stButton"] > button[kind="secondary"] {
    background: rgba(232, 237, 235, 0.05) !important;
    color: #E8EDEB !important;
    border: 1px solid rgba(232, 237, 235, 0.2) !important;
}

div[data-testid="stButton"] > button[kind="secondary"]:hover {
    border-color: #B7F34A !important;
    color: #FFFFFF !important;
    background: rgba(232, 237, 235, 0.12) !important;
    transform: translateY(-1px) !important;
}

div[data-testid="metric-container"] {
    background: #16222F !important;
    border: 1px solid rgba(232, 237, 235, 0.14) !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.3) !important;
}

div[data-testid="metric-container"]:hover {
    border-color: rgba(183, 243, 74, 0.45) !important;
}

/* ── Alert Boxes ── */
.alert-banner {
    padding: 12px 18px;
    border-radius: 10px;
    font-size: 0.85rem;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.alert-warning {
    background: rgba(245, 158, 11, 0.12);
    border: 1px solid #F59E0B;
    color: #FDE68A;
}

.alert-danger {
    background: rgba(239, 68, 68, 0.12);
    border: 1px solid #EF4444;
    color: #FECACA;
}

.alert-info {
    background: rgba(183, 243, 74, 0.1);
    border: 1px solid rgba(183, 243, 74, 0.35);
    color: #B7F34A;
}

/* ── Editorial Typography & Storytelling System ── */
.hero-title {
    font-size: clamp(2.4rem, 4.4vw, 3.8rem) !important;
    font-weight: 900 !important;
    line-height: 1.12 !important;
    letter-spacing: -1.2px !important;
    color: #F1F5F9 !important;
    margin: 0 0 16px 0 !important;
}

.section-title {
    font-size: clamp(1.85rem, 3vw, 2.5rem) !important;
    font-weight: 800 !important;
    line-height: 1.2 !important;
    letter-spacing: -0.6px !important;
    color: #F1F5F9 !important;
    margin: 8px 0 12px 0 !important;
}

.section-subtitle {
    font-size: 1.05rem !important;
    color: #E8EDEB !important;
    opacity: 0.85;
    line-height: 1.65 !important;
    max-width: 660px !important;
}

.body-editorial {
    font-size: 1.02rem !important;
    color: #CBD5E1 !important;
    line-height: 1.75 !important;
}

/* ── Parameter Showcase Pills (No heavy card boxes) ── */
.param-pill {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 18px;
    background: #16222F;
    border: 1px solid rgba(232, 237, 235, 0.16);
    border-radius: 14px;
    transition: all 0.22s ease;
}

.param-pill:hover {
    background: #1A2837;
    border-color: #B7F34A;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4), 0 0 16px rgba(183, 243, 74, 0.1);
}

.param-icon {
    font-size: 1.6rem;
    line-height: 1;
}

.param-name {
    font-weight: 700;
    font-size: 0.98rem;
    color: #F1F5F9;
    letter-spacing: -0.2px;
}

.param-desc {
    font-size: 0.76rem;
    color: #CBD5E1;
    margin-top: 2px;
}

/* ── Connected Architecture Pipeline ── */
.arch-flow-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
    padding: 24px 12px;
    margin: 18px 0;
    gap: 12px;
    flex-wrap: wrap;
}

.arch-step-node {
    flex: 1;
    min-width: 140px;
    background: #16222F;
    border: 1px solid rgba(232, 237, 235, 0.18);
    border-radius: 14px;
    padding: 16px 14px;
    text-align: center;
    transition: all 0.25s ease;
    position: relative;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
}

.arch-step-node:hover {
    border-color: #B7F34A;
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), 0 0 20px rgba(183, 243, 74, 0.18);
}

.arch-node-num {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 800;
    color: #B7F34A;
    background: rgba(183, 243, 74, 0.12);
    border: 1px solid rgba(183, 243, 74, 0.35);
    padding: 2px 7px;
    border-radius: 10px;
    margin-bottom: 6px;
    letter-spacing: 0.8px;
}

.arch-arrow {
    color: #B7F34A;
    font-size: 1.25rem;
    font-weight: 900;
    opacity: 0.8;
}

/* ── Asymmetric Platform Capabilities ── */
.capability-card {
    background: #16222F;
    border: 1px solid rgba(232, 237, 235, 0.15);
    border-radius: 16px;
    padding: 26px 24px;
    height: 100%;
    transition: all 0.25s ease;
    box-shadow: 0 6px 26px rgba(0, 0, 0, 0.38);
    position: relative;
}

.capability-card:hover {
    border-color: rgba(183, 243, 74, 0.45);
    transform: translateY(-3px);
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.5), 0 0 24px rgba(183, 243, 74, 0.12);
}

/* ── Mockup Window Frame (60-30-10) ── */
.mockup-frame {
    background: #101820;
    border: 1px solid rgba(232, 237, 235, 0.2);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.75), 0 0 40px rgba(183, 243, 74, 0.08);
}

.mockup-header {
    background: #16222F;
    padding: 12px 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid rgba(232, 237, 235, 0.08);
}

.mockup-dots {
    display: flex;
    gap: 7px;
}

.mockup-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
}

/* ── Compact Tech Logo Badge ── */
.tech-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    background: #16222F;
    border: 1px solid rgba(232, 237, 235, 0.16);
    border-radius: 20px;
    font-size: 0.86rem;
    font-weight: 600;
    color: #E8EDEB;
    transition: all 0.2s ease;
}

.tech-pill:hover {
    border-color: #B7F34A;
    background: rgba(183, 243, 74, 0.08);
    color: #FFFFFF;
    transform: translateY(-1px);
}

/* ── Numbered Editorial List ── */
.editorial-num-row {
    display: flex;
    gap: 18px;
    align-items: flex-start;
    padding: 14px 0;
    border-bottom: 1px solid rgba(232, 237, 235, 0.08);
}

.editorial-num-badge {
    font-size: 1.1rem;
    font-weight: 900;
    color: #B7F34A;
    min-width: 34px;
    height: 34px;
    border-radius: 8px;
    background: rgba(183, 243, 74, 0.12);
    border: 1px solid rgba(183, 243, 74, 0.35);
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>
"""
