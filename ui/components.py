"""
ChemLab - Reusable UI Components
Provides headers, footers with exact author credits, metric cards, and layout wrappers
styled for the Midnight Laboratory design system.
"""

import streamlit as st

def render_header():
    """Render the compact, professional scientific workstation header."""
    st.markdown("""
    <div class="chemlab-header">
        <div class="chemlab-title-group">
            <h1>⚗️ ChemLab <span style="font-size: 13px; font-weight: 500; color: #7DD3FC; margin-left: 6px;">| Scientific Cheminformatics Workstation</span></h1>
            <div class="chemlab-tagline">Explore molecules. Understand bonding. Visualise chemistry.</div>
        </div>
        <div class="chemlab-author-badge">
            Designed by R Vishwa Janagan
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    """
    Render consistent minimal footer across every application section.
    Displays exactly: '© R Vishwa Janagan'
    """
    st.markdown("""
    <div class="chemlab-footer">
        <span class="copyright">© R Vishwa Janagan</span> &nbsp;•&nbsp; 
        <span>ChemLab — Interactive Virtual Chemistry Laboratory</span> &nbsp;•&nbsp;
        <span>Scientific Computing & Cheminformatics</span>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(label: str, value: str, unit: str = ""):
    """Render a clean scientific metric box with high-contrast text."""
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">{label}</div>
        <div class="metric-val">{value}<span class="metric-unit">{unit}</span></div>
    </div>
    """, unsafe_allow_html=True)
