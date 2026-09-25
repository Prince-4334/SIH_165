"""
SIF SENTINEL - High-Contrast Industrial EHS Styling System
Complies strictly with Section 3 Visual Identity rules:
- Steel navy (#0F172A), Slate teal / steel blue (#0369A1), Alert red (#DC2626), Warning amber (#D97706), Safety green (#16A34A), Neutral slate (#475569), Off-white (#F8FAFC)
- CRITICAL CSS RULE: Every selector setting background/background-color explicitly sets color in the SAME rule.
- Default (non-hovered) state has 100% readable, high-contrast text.
- Overrides Streamlit default chrome (hamburger menu, footer, padding).
- NO emoji glyphs in cards or buttons. The 🛡️ in sidebar header is the ONLY emoji glyph in the app.
"""

from config import COLORS

def get_industrial_css() -> str:
    """Returns accessible, high-contrast CSS for industrial EHS look and feel."""
    return f"""
    <style>
    /* -------------------------------------------------------------
       FONT IMPORT & ACCESSIBLE COLOR RESET
       ------------------------------------------------------------- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    html, body, .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        -webkit-font-smoothing: antialiased;
    }}

    .mono-val, .report-id, .metric-number, code, pre, .score-val {{
        font-family: 'JetBrains Mono', monospace !important;
    }}

    /* Remove default Streamlit chrome & adjust top padding */
    #MainMenu {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    header {{visibility: hidden !important;}}
    div[data-testid="stDecoration"] {{display: none !important;}}
    
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 98% !important;
    }}

    /* -------------------------------------------------------------
       TEXTAREA & INPUT BOXES: PROMINENT & HIGH-VISIBILITY
       ------------------------------------------------------------- */
    .stTextArea textarea {{
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 2px solid #0369A1 !important;
        border-radius: 6px !important;
        font-size: 0.95rem !important;
        font-family: 'Inter', sans-serif !important;
        line-height: 1.5 !important;
        padding: 12px 14px !important;
        box-shadow: 0 1px 3px rgba(3, 105, 161, 0.08) !important;
    }}

    .stTextArea textarea:focus {{
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-color: #0284C7 !important;
        box-shadow: 0 0 0 3px rgba(3, 105, 161, 0.2) !important;
        outline: none !important;
    }}

    .stTextArea textarea::placeholder {{
        color: #64748B !important;
        font-style: italic !important;
    }}

    .stTextInput input {{
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 6px !important;
        font-size: 0.9rem !important;
        padding: 8px 12px !important;
    }}

    .stTextInput input:focus {{
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-color: #0369A1 !important;
        box-shadow: 0 0 0 2px rgba(3, 105, 161, 0.15) !important;
    }}

    /* Selectbox dropdowns */
    div[data-baseweb="select"] > div {{
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 6px !important;
    }}

    div[data-baseweb="select"] * {{
        color: #0F172A !important;
    }}

    /* Form labels - High contrast bold */
    label[data-testid="stWidgetLabel"] p {{
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
    }}

    /* -------------------------------------------------------------
       BUTTONS - CLEAR HIERARCHY & 100% VISIBLE CONTRAST
       ------------------------------------------------------------- */
    .stButton button {{
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        padding: 8px 16px !important;
        transition: all 0.15s ease !important;
        cursor: pointer !important;
    }}

    button[kind="primary"], .stButton button[kind="primary"] {{
        background-color: #0369A1 !important;
        border: 1.5px solid #0284C7 !important;
        color: #FFFFFF !important;
        box-shadow: 0 1px 2px rgba(3, 105, 161, 0.2) !important;
    }}

    button[kind="primary"] p, button[kind="primary"] span, button[kind="primary"] div {{
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }}

    button[kind="primary"]:hover {{
        background-color: #075985 !important;
        border-color: #0369A1 !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 4px rgba(3, 105, 161, 0.3) !important;
    }}

    button[kind="secondary"], .stButton button[kind="secondary"] {{
        background-color: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        color: #1E293B !important;
    }}

    button[kind="secondary"] p, button[kind="secondary"] span {{
        color: #1E293B !important;
        font-weight: 600 !important;
    }}

    button[kind="secondary"]:hover {{
        background-color: #F1F5F9 !important;
        border-color: #94A3B8 !important;
        color: #0F172A !important;
    }}

    /* -------------------------------------------------------------
       SIDEBAR INDUSTRIAL STYLING
       ------------------------------------------------------------- */
    section[data-testid="stSidebar"] {{
        background-color: #1E293B !important;
        border-right: 1px solid #334155 !important;
        width: 280px !important;
    }}

    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] strong {{
        color: #F8FAFC !important;
    }}

    /* Restyle Streamlit radio buttons into enterprise navigation items */
    div[data-testid="stRadio"] > div {{
        gap: 6px !important;
    }}

    div[data-testid="stRadio"] label {{
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #F8FAFC !important;
        border-radius: 6px !important;
        padding: 10px 14px !important;
        margin: 2px 0 !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        display: flex !important;
        align-items: center !important;
    }}

    div[data-testid="stRadio"] label:hover {{
        background-color: rgba(255, 255, 255, 0.12) !important;
        color: #FFFFFF !important;
        border-color: #38BDF8 !important;
    }}

    div[data-testid="stRadio"] label[data-checked="true"],
    div[data-testid="stRadio"] input:checked + div {{
        background-color: #0369A1 !important;
        color: #FFFFFF !important;
        border-color: #38BDF8 !important;
        border-left: 4px solid #38BDF8 !important;
    }}

    div[data-testid="stRadio"] label p {{
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        color: #FFFFFF !important;
    }}

    div[data-testid="stRadio"] input {{
        display: none !important;
    }}

    /* -------------------------------------------------------------
       HEADER & NAVIGATION TOKENS
       ------------------------------------------------------------- */
    .app-header {{
        background-color: #0F172A;
        color: #FFFFFF;
        padding: 14px 20px;
        border-radius: 8px;
        border-bottom: 3px solid #0369A1;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 4px rgba(15, 23, 42, 0.08);
    }}

    .app-header h1 {{
        margin: 0;
        font-size: 1.25rem;
        font-weight: 700;
        letter-spacing: -0.01em;
        color: #FFFFFF !important;
        display: flex;
        align-items: center;
        gap: 10px;
    }}

    .app-header .tagline {{
        font-size: 0.82rem;
        color: #94A3B8 !important;
        font-weight: 400;
        margin-top: 2px;
    }}

    .app-header .env-badge {{
        background: #1E293B;
        border: 1px solid #334155;
        color: #38BDF8 !important;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace !important;
    }}

    /* -------------------------------------------------------------
       KPI CARD SYSTEM (High Contrast & Clear Typography)
       ------------------------------------------------------------- */
    .kpi-container {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        margin-bottom: 18px;
    }}

    .kpi-card {{
        background: #FFFFFF;
        color: #0F172A;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px 18px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
        position: relative;
    }}

    .kpi-card.kpi-total {{
        background: #FFFFFF;
        color: #0F172A;
        border-left: 4px solid #475569;
    }}

    .kpi-card.kpi-sif {{
        background: #FFFFFF;
        color: #0F172A;
        border-left: 4px solid #DC2626;
    }}

    .kpi-card.kpi-rate {{
        background: #FFFFFF;
        color: #0F172A;
        border-left: 4px solid #0369A1;
    }}

    .kpi-card.kpi-pending {{
        background: #FFFFFF;
        color: #0F172A;
        border-left: 4px solid #D97706;
    }}

    .kpi-card.kpi-confirmed {{
        background: #FFFFFF;
        color: #0F172A;
        border-left: 4px solid #16A34A;
    }}

    .kpi-title {{
        font-size: 0.78rem;
        font-weight: 700;
        color: #475569;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }}

    .kpi-value {{
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 2rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.1;
        margin-bottom: 4px;
    }}

    .kpi-subtext {{
        font-size: 0.74rem;
        color: #64748B;
    }}

    /* -------------------------------------------------------------
       HERO ANALYSIS RESULT CARD
       ------------------------------------------------------------- */
    .analysis-hero-card {{
        background: #FFFFFF;
        color: #0F172A;
        border: 1.5px solid #CBD5E1;
        border-radius: 8px;
        padding: 22px;
        margin-top: 16px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08);
    }}

    .analysis-hero-card.high-alert {{
        background: #FFFFFF;
        color: #0F172A;
        border-top: 5px solid #DC2626;
        border-left: 1.5px solid #FCA5A5;
    }}

    .analysis-hero-card.med-alert {{
        background: #FFFFFF;
        color: #0F172A;
        border-top: 5px solid #D97706;
        border-left: 1.5px solid #FCD34D;
    }}

    .analysis-hero-card.low-alert {{
        background: #FFFFFF;
        color: #0F172A;
        border-top: 5px solid #16A34A;
        border-left: 1.5px solid #86EFAC;
    }}

    .analysis-top-banner {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1.5px solid #E2E8F0;
        padding-bottom: 14px;
        margin-bottom: 16px;
    }}

    .sif-score-display {{
        text-align: right;
    }}

    .sif-score-num {{
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 2.2rem;
        font-weight: 700;
        line-height: 1;
    }}

    .meta-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 14px;
        margin-bottom: 18px;
    }}

    .meta-cell {{
        background: #F8FAFC;
        color: #0F172A;
        border: 1.5px solid #E2E8F0;
        border-radius: 6px;
        padding: 12px 14px;
    }}

    .meta-label {{
        font-size: 0.72rem;
        font-weight: 700;
        color: #475569;
        margin-bottom: 4px;
        letter-spacing: 0.02em;
    }}

    .meta-value {{
        font-size: 0.95rem;
        font-weight: 700;
        color: #0F172A;
    }}

    .explain-box {{
        background: #F0F9FF;
        color: #0F172A;
        border: 1.5px solid #BAE6FD;
        border-left: 4px solid #0369A1;
        border-radius: 6px;
        padding: 14px 16px;
        margin-bottom: 16px;
    }}

    .action-box {{
        background: #FFFBEB;
        color: #78350F;
        border: 1.5px solid #FDE68A;
        border-left: 4px solid #D97706;
        border-radius: 6px;
        padding: 14px 16px;
        margin-bottom: 16px;
    }}

    .evidence-pill {{
        background: #E2E8F0;
        color: #1E293B;
        border-radius: 4px;
        padding: 4px 10px;
        font-size: 0.78rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace !important;
        margin-right: 6px;
        display: inline-block;
        margin-top: 4px;
        border: 1px solid #CBD5E1;
    }}

    /* Status and Provenance Badges (NO EMOJIS) */
    .source-badge {{
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        display: inline-flex;
        align-items: center;
        letter-spacing: 0.02em;
    }}

    .source-live {{
        background: #DCFCE7;
        color: #15803D;
        border: 1px solid #86EFAC;
    }}

    .source-demo {{
        background: #FEF3C7;
        color: #B45309;
        border: 1px solid #FCD34D;
    }}

    .status-badge {{
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        display: inline-block;
    }}

    .badge-confirmed {{
        background: #DCFCE7;
        color: #15803D;
        border: 1px solid #86EFAC;
    }}

    .badge-pending {{
        background: #FEF3C7;
        color: #B45309;
        border: 1px solid #FCD34D;
    }}

    .badge-dismissed {{
        background: #F1F5F9;
        color: #475569;
        border: 1px solid #CBD5E1;
    }}

    .badge-escalated {{
        background: #E0F2FE;
        color: #0369A1;
        border: 1px solid #BAE6FD;
    }}

    /* Dataframe table cell styling */
    div[data-testid="stDataFrame"] {{
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }}

    /* -------------------------------------------------------------
       DISCLAIMER & FOOTER (Plain text, not a colored banner)
       ------------------------------------------------------------- */
    .app-footer {{
        margin-top: 36px;
        padding-top: 14px;
        border-top: 1px solid #E2E8F0;
        text-align: center;
        font-size: 0.8rem;
        color: #64748B;
        background: transparent;
    }}
    </style>
    """


def render_source_badge(data_source: str) -> str:
    """Returns visual badge distinguishing Demo Data vs Live Session Data without emojis."""
    if data_source == "LIVE":
        return '<span class="source-badge source-live">LIVE SESSION</span>'
    return '<span class="source-badge source-demo">DEMO BENCHMARK</span>'


def render_status_badge(status: str) -> str:
    """Returns official visual badge for HSE review status without emojis."""
    s_upper = status.upper()
    if "CONFIRMED" in s_upper or "REVIEWED" in s_upper:
        return f'<span class="status-badge badge-confirmed">REVIEWED</span>'
    elif "REJECTED" in s_upper or "DISMISSED" in s_upper:
        return f'<span class="status-badge badge-dismissed">DISMISSED</span>'
    elif "NEEDS" in s_upper or "ESCALATED" in s_upper:
        return f'<span class="status-badge badge-escalated">ESCALATED</span>'
    else:  # PENDING
        return f'<span class="status-badge badge-pending">PENDING REVIEW</span>'


def render_app_header() -> str:
    """Generate industrial top header HTML without emojis."""
    from config import APP_NAME, APP_SUBTITLE
    return f"""
    <div class="app-header">
        <div>
            <h1>{APP_NAME} <span style="font-weight:400; font-size: 0.95rem; color:#94A3B8;">| {APP_SUBTITLE}</span></h1>
            <div class="tagline">From Safety Reports to Actionable SIF Intelligence &bull; OIL Asset Decision Support</div>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
            <span class="env-badge">AIR-GAPPED ENGINE</span>
        </div>
    </div>
    """


def render_footer() -> str:
    """Standardized plain text footer disclaimer per Section 3."""
    from config import APP_DISCLAIMER
    return f"""
    <div class="app-footer">
        <p style="margin: 0; color: #64748B; font-weight: 500; font-size: 0.8rem;">{APP_DISCLAIMER}</p>
    </div>
    """
