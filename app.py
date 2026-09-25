"""
SIF SENTINEL
AI-Powered SIF Precursor Intelligence Platform
From Safety Reports to Actionable SIF Intelligence
"""

import streamlit as st
from config import APP_NAME, APP_SUBTITLE, APP_TAGLINE, COLORS
from db import init_db, get_kpis
from styles import get_industrial_css, render_app_header, render_footer

# Import views
from views.overview import render_overview
from views.analyze import render_analyze
from views.history import render_history
from views.patterns import render_patterns
from views.rules import render_rules
from views.about import render_about

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title=f"{APP_NAME} — SIF Precursor Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database schema and synthetic dataset on cold start
init_db()

# Inject high-contrast industrial styling
st.markdown(get_industrial_css(), unsafe_allow_html=True)

# Navigation options
NAV_OPTIONS = [
    "Overview",
    "Analyze Report",
    "SIF Reports",
    "Precursor Patterns",
    "Life-Saving Rules",
    "About"
]

if "current_nav" not in st.session_state:
    st.session_state["current_nav"] = "Overview"

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"""
    <div style="padding: 10px 4px 16px 4px; border-bottom: 1px solid #334155; margin-bottom: 14px;">
        <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size: 1.45rem;">🛡️</span>
            <div>
                <div style="font-weight: 700; font-size: 1.15rem; color: #FFFFFF; letter-spacing: -0.02em;">
                    {APP_NAME}
                </div>
                <div style="font-size: 0.72rem; color: #94A3B8; font-weight: 500;">
                    SIF Precursor Intelligence
                </div>
            </div>
        </div>
        <div style="margin-top: 10px; display:flex; justify-content:space-between; align-items:center;">
            <span style="background: #0F172A; border: 1px solid #334155; color: #38BDF8; font-size: 0.68rem; padding: 3px 8px; border-radius: 4px; font-family:'JetBrains Mono', monospace; font-weight:600;">
                OIL HSE v2.4
            </span>
            <span style="color: #64748B; font-size: 0.7rem; font-family:'JetBrains Mono', monospace; font-weight:600;">
                AIR-GAPPED
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    sidebar_choice = st.radio(
        "Navigation",
        options=NAV_OPTIONS,
        index=NAV_OPTIONS.index(st.session_state["current_nav"]) if st.session_state["current_nav"] in NAV_OPTIONS else 0,
        key="sidebar_nav_radio",
        label_visibility="collapsed"
    )
    if sidebar_choice != st.session_state["current_nav"]:
        st.session_state["current_nav"] = sidebar_choice
        st.rerun()

    # Sidebar dynamic quick metrics
    kpis = get_kpis()
    st.markdown(f"""
    <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #334155;">
        <div style="font-size: 0.72rem; font-weight: 700; color: #94A3B8; margin-bottom: 10px; text-transform: uppercase;">
            Live Precursor Registry
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.82rem;">
            <span style="color: #CBD5E1;">Total Reports:</span>
            <strong style="color: #FFFFFF; font-family:'JetBrains Mono'; font-weight:700;">{kpis['total_reports']:,}</strong>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.82rem;">
            <span style="color: #CBD5E1;">High SIF:</span>
            <strong style="color: #F87171; font-family:'JetBrains Mono'; font-weight:700;">{kpis['sif_potential']:,}</strong>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.82rem;">
            <span style="color: #CBD5E1;">Review Pending:</span>
            <strong style="color: #FBBF24; font-family:'JetBrains Mono'; font-weight:700;">{kpis['pending_review']}</strong>
        </div>
    </div>
    
    <div style="margin-top: 24px; padding: 12px; background: #0F172A; border: 1px solid #334155; border-radius: 6px; font-size: 0.74rem; color: #94A3B8; line-height: 1.45;">
        <strong style="color: #38BDF8;">IOGP Framework Grounding:</strong><br>
        Screening calibrated against IOGP Life-Saving Rules and barrier failure taxonomy.
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MAIN APP CANVAS
# -----------------------------------------------------------------------------
# Top application industrial banner
st.markdown(render_app_header(), unsafe_allow_html=True)

# Top Fast Navigation Bar (Visible on screen at all times)
top_cols = st.columns(len(NAV_OPTIONS))

for idx, opt in enumerate(NAV_OPTIONS):
    is_active = (st.session_state["current_nav"] == opt)
    btn_type = "primary" if is_active else "secondary"
    if top_cols[idx].button(opt, key=f"top_nav_{idx}", type=btn_type, use_container_width=True):
        st.session_state["current_nav"] = opt
        st.rerun()

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# Dispatch to view
current_view = st.session_state["current_nav"]
if current_view == "Overview":
    render_overview()
elif current_view == "Analyze Report":
    render_analyze()
elif current_view == "SIF Reports":
    render_history()
elif current_view == "Precursor Patterns":
    render_patterns()
elif current_view == "Life-Saving Rules":
    render_rules()
elif current_view == "About":
    render_about()

# Standardized footer disclaimer
st.markdown(render_footer(), unsafe_allow_html=True)
