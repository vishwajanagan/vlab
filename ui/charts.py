"""
ChemLab - Scientific Data Visualizations
Plotly charts for elemental distribution, bond breakdowns,
descriptor comparisons, and VSEPR angular distributions styled for Midnight Laboratory.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

MIDNIGHT_CHART_THEME = {
    "plot_bgcolor": "#151F33",
    "paper_bgcolor": "#151F33",
    "font": {
        "family": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        "color": "#F1F5F9",
        "size": 12
    },
    "margin": {"l": 35, "r": 35, "t": 45, "b": 35}
}

MIDNIGHT_PALETTE = ["#2DD4BF", "#7DD3FC", "#34D399", "#FBBF24", "#A78BFA", "#FB7185", "#94A3B8"]

def create_element_composition_chart(element_counts: dict):
    """Create clean donut chart of elemental composition."""
    if not element_counts:
        return None

    df = pd.DataFrame(list(element_counts.items()), columns=["Element", "Count"])
    
    fig = px.pie(
        df,
        values="Count",
        names="Element",
        hole=0.6,
        color_discrete_sequence=MIDNIGHT_PALETTE,
        title="Elemental Composition (Atoms incl. H)"
    )
    fig.update_layout(
        **MIDNIGHT_CHART_THEME,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(color="#B6C2D2")
        ),
        title_font=dict(color="#F1F5F9", size=14)
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        marker=dict(line=dict(color="#0B1020", width=2))
    )
    return fig

def create_bond_distribution_chart(bond_counts: dict):
    """Create horizontal bar chart of bond types."""
    if not bond_counts:
        return None

    filtered = {k: v for k, v in bond_counts.items() if v > 0}
    df = pd.DataFrame(list(filtered.items()), columns=["Bond Type", "Count"])

    fig = px.bar(
        df,
        x="Count",
        y="Bond Type",
        orientation="h",
        color="Count",
        color_continuous_scale=[(0, "#344258"), (1, "#2DD4BF")],
        title="Bond Type & Framework Distribution"
    )
    fig.update_layout(
        **MIDNIGHT_CHART_THEME,
        coloraxis_showscale=False,
        xaxis=dict(
            title="Number of Bonds",
            gridcolor="#344258",
            zerolinecolor="#344258",
            color="#B6C2D2"
        ),
        yaxis=dict(title="", color="#F1F5F9"),
        title_font=dict(color="#F1F5F9", size=14)
    )
    fig.update_traces(
        marker=dict(line=dict(color="#2DD4BF", width=1))
    )
    return fig

def create_multi_property_radar(molecules_data: list):
    """
    Create radar chart comparing multiple molecules across normalized descriptors
    (MW, LogP, TPSA, HBD, HBA, Rotatable Bonds).
    """
    if not molecules_data:
        return None

    categories = ["MW (scaled)", "LogP (+3)", "TPSA (scaled)", "HBD", "HBA", "RotBonds"]

    fig = go.Figure()

    for idx, mol_item in enumerate(molecules_data):
        name = mol_item["name"]
        props = mol_item["props"]

        # Scale properties for comparable radar dimensions
        mw_scaled = min(props.get("Molecular Weight", 0) / 50.0, 10)
        logp_scaled = max(props.get("LogP", 0) + 3.0, 0)
        tpsa_scaled = min(props.get("TPSA", 0) / 20.0, 10)
        hbd = props.get("Hydrogen Bond Donors", 0)
        hba = props.get("Hydrogen Bond Acceptors", 0)
        rot = props.get("Rotatable Bonds", 0)

        values = [mw_scaled, logp_scaled, tpsa_scaled, hbd, hba, rot]
        values.append(values[0])

        color = MIDNIGHT_PALETTE[idx % len(MIDNIGHT_PALETTE)]

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill="toself",
            name=name,
            line=dict(color=color, width=2),
            opacity=0.6
        ))

    fig.update_layout(
        **MIDNIGHT_CHART_THEME,
        polar=dict(
            bgcolor="#151F33",
            radialaxis=dict(visible=True, range=[0, 10], color="#64748B", gridcolor="#344258"),
            angularaxis=dict(color="#B6C2D2", gridcolor="#344258")
        ),
        title="Comparative Molecular Descriptors Profile",
        title_font=dict(color="#F1F5F9", size=14),
        showlegend=True,
        legend=dict(font=dict(color="#B6C2D2"))
    )
    return fig

def create_vsepr_comparison_bar(series_data: list):
    """
    Bar chart comparing bond angles in tetrahedral series (CH4 vs NH3 vs H2O)
    illustrating the progressive compression from lone-pair repulsions.
    """
    df = pd.DataFrame(series_data)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Actual Bond Angle (°)",
        x=df["name"],
        y=df["actual_angle"],
        marker_color="#2DD4BF",
        text=df["actual_angle"].apply(lambda x: f"{x}°"),
        textposition="auto",
        textfont=dict(color="#0B1020", family="'Inter', sans-serif", weight="bold")
    ))

    fig.add_trace(go.Scatter(
        name="Ideal Tetrahedral (109.5°)",
        x=df["name"],
        y=[109.5] * len(df),
        mode="lines+markers",
        line=dict(color="#FB7185", width=2.5, dash="dash"),
        marker=dict(size=8, color="#FB7185")
    ))

    fig.update_layout(
        **MIDNIGHT_CHART_THEME,
        barmode="group",
        title="Tetrahedral Electron Domain: Lone-Pair Angular Compression",
        title_font=dict(color="#F1F5F9", size=14),
        xaxis=dict(color="#F1F5F9", gridcolor="#344258"),
        yaxis=dict(
            title="Bond Angle (°)",
            range=[95, 120],
            color="#B6C2D2",
            gridcolor="#344258",
            zerolinecolor="#344258"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(color="#B6C2D2")
        )
    )
    return fig
