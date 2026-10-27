"""
ChemLab - Midnight Laboratory Design System
Implements an authentic scientific-computing workstation aesthetic:
Deep Midnight (#0B1020), Sidebar (#10182A), Panels (#151F33), Elevated Cards (#1C2940),
Primary Accent (#2DD4BF Teal), Secondary Accent (#7DD3FC Cyan), and High-Contrast Typography.
"""

MIDNIGHT_LAB_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* -------------------------------------------------------------
   Design Tokens - Midnight Laboratory
   ------------------------------------------------------------- */
:root {
    --bg-main: #0B1020;
    --bg-sidebar: #10182A;
    --bg-panel: #151F33;
    --bg-card: #1C2940;
    
    --accent-primary: #2DD4BF;
    --accent-hover: #14B8A6;
    --accent-secondary: #7DD3FC;
    
    --text-primary: #F1F5F9;
    --text-secondary: #B6C2D2;
    --text-muted: #64748B;
    
    --border-color: #344258;
    --border-focus: #2DD4BF;
    
    --status-success: #34D399;
    --status-warning: #FBBF24;
    --status-error: #FB7185;

    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

/* -------------------------------------------------------------
   Global Application Surface & Typography
   ------------------------------------------------------------- */
html, body, [class*="st-emotion"] {
    font-family: var(--font-sans) !important;
    color: var(--text-primary) !important;
}

.stApp,
[data-testid="stAppViewContainer"] {
    background-color: var(--bg-main) !important;
    color: var(--text-primary) !important;
}

[data-testid="stHeader"] {
    background-color: rgba(11, 16, 32, 0.85) !important;
    backdrop-filter: blur(8px) !important;
    border-bottom: 1px solid var(--border-color) !important;
}

[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-color) !important;
}

/* Base Headings & Text */
h1, [data-testid="stMarkdownContainer"] h1 {
    font-size: 30px !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.025em !important;
    margin-top: 0 !important;
    margin-bottom: 12px !important;
}

h2, [data-testid="stMarkdownContainer"] h2 {
    font-size: 22px !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.015em !important;
    margin-top: 20px !important;
    margin-bottom: 10px !important;
}

h3, [data-testid="stMarkdownContainer"] h3 {
    font-size: 18px !important;
    font-weight: 600 !important;
    color: var(--accent-secondary) !important;
    letter-spacing: -0.01em !important;
    margin-top: 16px !important;
    margin-bottom: 8px !important;
}

h4, [data-testid="stMarkdownContainer"] h4 {
    font-size: 15px !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
}

p, [data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    font-size: 15px !important;
    line-height: 1.6 !important;
    color: var(--text-secondary) !important;
}

/* -------------------------------------------------------------
   Application Header Bar
   ------------------------------------------------------------- */
.chemlab-header {
    background: var(--bg-panel);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 16px 22px;
    margin-bottom: 22px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
}

.chemlab-title-group h1 {
    font-size: 22px !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    margin: 0 !important;
    padding: 0 !important;
    display: flex;
    align-items: center;
    gap: 10px;
}

.chemlab-tagline {
    font-size: 13px;
    color: var(--accent-secondary);
    margin-top: 2px;
    font-weight: 500;
}

.chemlab-author-badge {
    background: rgba(45, 212, 191, 0.12);
    color: var(--accent-primary);
    font-size: 12px;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: 9999px;
    border: 1px solid rgba(45, 212, 191, 0.3);
    white-space: nowrap;
}

/* -------------------------------------------------------------
   Scientific Panels & Elevated Surface Cards
   ------------------------------------------------------------- */
.lab-panel {
    background: var(--bg-panel);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 18px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15);
}

.lab-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 18px;
    margin-bottom: 16px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12);
}

.lab-card-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Metric Display Blocks */
.metric-box {
    background: var(--bg-panel);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 12px 14px;
    margin-bottom: 10px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
}

.metric-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-secondary);
    margin-bottom: 4px;
}

.metric-val {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-primary);
    display: flex;
    align-items: baseline;
}

.metric-unit {
    font-size: 12px;
    font-weight: 500;
    color: var(--accent-secondary);
    margin-left: 4px;
}

/* -------------------------------------------------------------
   Hero Card on Introduction Page
   ------------------------------------------------------------- */
.intro-hero {
    background: linear-gradient(135deg, #10182A 0%, #151F33 100%);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 30px 28px;
    margin-bottom: 22px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
}

.intro-badge {
    display: inline-block;
    background: rgba(45, 212, 191, 0.15);
    color: var(--accent-primary);
    font-size: 12px;
    font-weight: 600;
    padding: 3px 12px;
    border-radius: 9999px;
    border: 1px solid rgba(45, 212, 191, 0.35);
    margin-bottom: 10px;
}

.intro-title {
    font-size: 28px;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.02em;
    margin-bottom: 6px;
}

.intro-desc {
    font-size: 15px;
    color: var(--text-secondary);
    line-height: 1.6;
    max-width: 720px;
    margin-bottom: 18px;
}

.feature-pill {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 12px;
    color: var(--text-primary);
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-right: 6px;
    margin-bottom: 6px;
}

/* -------------------------------------------------------------
   Educational Callouts
   ------------------------------------------------------------- */
.callout-teal {
    background: rgba(45, 212, 191, 0.08);
    border-left: 4px solid var(--accent-primary);
    border-radius: 0 6px 6px 0;
    padding: 12px 16px;
    margin: 12px 0;
    font-size: 14px;
    line-height: 1.6;
    color: var(--text-primary);
    border-top: 1px solid rgba(45, 212, 191, 0.2);
    border-right: 1px solid rgba(45, 212, 191, 0.2);
    border-bottom: 1px solid rgba(45, 212, 191, 0.2);
}

.callout-blue {
    background: rgba(125, 211, 252, 0.08);
    border-left: 4px solid var(--accent-secondary);
    border-radius: 0 6px 6px 0;
    padding: 12px 16px;
    margin: 12px 0;
    font-size: 14px;
    line-height: 1.6;
    color: var(--text-primary);
    border-top: 1px solid rgba(125, 211, 252, 0.2);
    border-right: 1px solid rgba(125, 211, 252, 0.2);
    border-bottom: 1px solid rgba(125, 211, 252, 0.2);
}

/* -------------------------------------------------------------
   Streamlit Native Inputs, Selectboxes, Tabs & Buttons
   ------------------------------------------------------------- */
/* Text inputs & text areas */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: var(--bg-panel) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 6px !important;
    font-size: 14px !important;
    padding: 8px 12px !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--border-focus) !important;
    box-shadow: 0 0 0 2px rgba(45, 212, 191, 0.2) !important;
}

/* Dropdown select boxes */
[data-baseweb="select"] {
    background-color: var(--bg-panel) !important;
    border-radius: 6px !important;
    border: 1px solid var(--border-color) !important;
}

[data-baseweb="select"] * {
    color: var(--text-primary) !important;
    background-color: var(--bg-panel) !important;
}

/* Standard Buttons */
.stButton > button {
    background-color: var(--bg-panel) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 8px 16px !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
    transition: all 0.15s ease-in-out !important;
}

.stButton > button:hover {
    border-color: var(--accent-primary) !important;
    color: var(--accent-primary) !important;
    background-color: var(--bg-card) !important;
}

/* Primary Action Buttons */
.stButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"] {
    background-color: var(--accent-primary) !important;
    border-color: var(--accent-primary) !important;
    color: #0B1020 !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 6px rgba(45, 212, 191, 0.3) !important;
}

.stButton > button[kind="primary"]:hover,
.stDownloadButton > button[kind="primary"]:hover {
    background-color: var(--accent-hover) !important;
    border-color: var(--accent-hover) !important;
    color: #0B1020 !important;
}

/* Sidebar Nav Buttons */
.nav-group-header {
    font-size: 11px;
    font-weight: 700;
    color: var(--accent-secondary);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 12px 6px 6px 6px;
    margin-top: 6px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    border-bottom: 1px solid var(--border-color);
    gap: 8px;
    background-color: transparent;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 6px 6px 0 0;
    font-weight: 600;
    font-size: 14px;
    color: var(--text-secondary) !important;
    padding: 8px 16px;
}

.stTabs [aria-selected="true"] {
    color: var(--accent-primary) !important;
    border-bottom: 2px solid var(--accent-primary) !important;
}

/* Dataframe containers */
[data-testid="stDataFrame"] {
    background-color: var(--bg-panel) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 6px !important;
}

/* Radio button typography */
.stRadio label,
.stRadio [data-testid="stMarkdownContainer"] p {
    color: var(--text-primary) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}

/* Expander styling */
[data-testid="stExpander"] {
    background-color: var(--bg-panel) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 6px !important;
}

/* Consistent Footer */
.chemlab-footer {
    border-top: 1px solid var(--border-color);
    margin-top: 48px;
    padding-top: 20px;
    padding-bottom: 28px;
    text-align: center;
    font-size: 13px;
    color: var(--text-secondary);
}

.chemlab-footer .copyright {
    font-weight: 700;
    color: var(--text-primary);
}
</style>
"""

# Backwards compatibility alias
NEUTRAL_THEME_CSS = MIDNIGHT_LAB_CSS
