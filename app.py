"""
CHEMLAB — Interactive Virtual Chemistry Laboratory
Visual System: Midnight Laboratory
Tagline: "Explore molecules. Understand bonding. Visualise chemistry."

Designed by R Vishwa Janagan
"""

import os
import streamlit as st
import pandas as pd
from rdkit import Chem

# Import modular ChemLab packages
from chemistry import (
    EXAMPLE_MOLECULES,
    parse_smiles,
    get_canonical_smiles,
    calculate_properties,
    generate_2d_image,
    generate_3d_molecule,
    get_element_composition,
    get_bond_type_distribution,
    VSEPR_DATABASE,
    TETRAHEDRAL_SERIES,
    calculate_conformer_angles,
    GEOMETRY_QUIZ,
    LEWIS_DATABASE,
    HYBRIDIZATION_INFO,
    POLARITY_EXAMPLES,
    inspect_molecule_structure,
    BONDING_QUIZ,
    generate_molecule_pdf,
    generate_multi_molecule_pdf
)

from ui import (
    MIDNIGHT_LAB_CSS,
    render_3dmol,
    create_element_composition_chart,
    create_bond_distribution_chart,
    create_multi_property_radar,
    create_vsepr_comparison_bar,
    render_header,
    render_footer,
    render_metric_card
)

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="ChemLab — Virtual Chemistry Laboratory",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Midnight Laboratory Design System CSS
st.markdown(MIDNIGHT_LAB_CSS, unsafe_allow_html=True)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
if "current_page" not in st.session_state:
    st.session_state.current_page = "Introduction"

if "active_smiles" not in st.session_state:
    st.session_state.active_smiles = "CCO"

if "viz_style" not in st.session_state:
    st.session_state.viz_style = "Ball and Stick"

if "show_surface" not in st.session_state:
    st.session_state.show_surface = False

if "canvas_bg" not in st.session_state:
    st.session_state.canvas_bg = "#F8FAFC"

if "student_name" not in st.session_state:
    st.session_state.student_name = ""

if "registration_number" not in st.session_state:
    st.session_state.registration_number = ""

if "geom_quiz_submitted" not in st.session_state:
    st.session_state.geom_quiz_submitted = False

if "bonding_quiz_submitted" not in st.session_state:
    st.session_state.bonding_quiz_submitted = False

# ============================================================
# SIDEBAR NAVIGATION (GROUPED BY WORKSPACE / OUTPUTS / INFO)
# ============================================================
NAV_GROUPS = [
    ("WORKSPACE", [
        ("Introduction", "intro"),
        ("Laboratory", "lab"),
        ("Molecular Geometry", "geom"),
        ("Chemical Bonding", "bonding"),
        ("Comparative Analysis", "compare"),
    ]),
    ("OUTPUTS", [
        ("Reports", "reports"),
    ]),
    ("INFORMATION", [
        ("About", "about"),
    ])
]

with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 16px 0; border-bottom: 1px solid #344258; margin-bottom: 14px;">
        <div style="font-size: 22px; font-weight: 800; color: #FFFFFF; display: flex; align-items: center; gap: 8px;">
            ⚗️ ChemLab
        </div>
        <div style="font-size: 12px; color: #7DD3FC; font-weight: 600; margin-top: 2px;">
            Scientific Cheminformatics
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Render Grouped Navigation
    for group_name, items in NAV_GROUPS:
        st.markdown(f"<div class='nav-group-header'>{group_name}</div>", unsafe_allow_html=True)
        for label, key_id in items:
            is_active = (st.session_state.current_page == label)
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_btn_{key_id}", use_container_width=True, type=btn_type):
                if st.session_state.current_page != label:
                    st.session_state.current_page = label
                    st.rerun()

    st.markdown("<hr style='border: none; border-top: 1px solid #344258; margin: 20px 0 16px 0;'>", unsafe_allow_html=True)
    
    # Student Metadata Profile
    st.markdown("<div style='font-size: 11px; font-weight: 700; color: #7DD3FC; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;'>Student Analyst</div>", unsafe_allow_html=True)
    st.session_state.student_name = st.text_input(
        "Student Name",
        value=st.session_state.student_name,
        placeholder="e.g. Alex Smith",
        key="sidebar_name_input",
        label_visibility="collapsed"
    )
    st.session_state.registration_number = st.text_input(
        "Registration No.",
        value=st.session_state.registration_number,
        placeholder="e.g. RA2311003010",
        key="sidebar_reg_input",
        label_visibility="collapsed"
    )

    # Clean Preferences / Settings Panel
    with st.expander("⚙️ Viewport Settings", expanded=False):
        st.session_state.canvas_bg = st.selectbox(
            "3D Canvas Canvas",
            ["Light Neutral (#F8FAFC)", "Dark Slate (#151F33)", "Pure White (#FFFFFF)"],
            index=["Light Neutral (#F8FAFC)", "Dark Slate (#151F33)", "Pure White (#FFFFFF)"].index(
                "Light Neutral (#F8FAFC)" if st.session_state.canvas_bg == "#F8FAFC" else
                ("Dark Slate (#151F33)" if st.session_state.canvas_bg == "#151F33" else "Pure White (#FFFFFF)")
            ),
            key="canvas_bg_select"
        )
        if "Light Neutral" in st.session_state.canvas_bg:
            st.session_state.canvas_bg = "#F8FAFC"
        elif "Dark Slate" in st.session_state.canvas_bg:
            st.session_state.canvas_bg = "#151F33"
        else:
            st.session_state.canvas_bg = "#FFFFFF"

    st.markdown("""
    <div style="font-size: 11px; color: #B6C2D2; line-height: 1.5; background: #151F33; padding: 10px 12px; border-radius: 6px; border: 1px solid #344258; margin-top: 14px;">
        <span style="color: #2DD4BF; font-weight: 700;">Designed by R Vishwa Janagan</span><br>
        <span style="font-size: 10px; color: #64748B;">Python • Streamlit • RDKit</span>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PAGE 1: INTRODUCTION
# ============================================================
if st.session_state.current_page == "Introduction":
    render_header()

    st.markdown("""
    <div class="intro-hero">
        <div class="intro-badge">Scientific Molecular Modeling Platform</div>
        <div class="intro-title">ChemLab — Interactive Virtual Chemistry Laboratory</div>
        <div class="intro-desc">
            Explore molecules. Understand bonding. Visualise chemistry.<br>
            A high-performance computing environment for molecular structure exploration,
            VSEPR geometry predictions, and chemical bonding analyses.
        </div>
        <div>
            <span class="feature-pill">🔬 RDKit Cheminformatics</span>
            <span class="feature-pill">🌐 Interactive 3D WebGL</span>
            <span class="feature-pill">📐 VSEPR Geometry Lab</span>
            <span class="feature-pill">🔗 Chemical Bonding Explorer</span>
            <span class="feature-pill">📑 Automated PDF Reports</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_action1, col_action2 = st.columns([1.5, 3])
    with col_action1:
        if st.button("🚀 Open Laboratory Workspace", type="primary", use_container_width=True, key="hero_open_lab"):
            st.session_state.current_page = "Laboratory"
            st.rerun()

    st.markdown("<hr style='border: none; border-top: 1px solid #344258; margin: 24px 0 20px 0;'>", unsafe_allow_html=True)

    # Quick Launch Molecules
    st.markdown("### ⚡ Quick-Launch Representative Molecules")
    st.markdown("Select any molecule to immediately load its 2D connectivity, 3D conformer, and calculated descriptors in the laboratory:")
    
    quick_cols = st.columns(len(EXAMPLE_MOLECULES))
    for idx, (m_name, m_smi) in enumerate(EXAMPLE_MOLECULES.items()):
        with quick_cols[idx]:
            if st.button(m_name, key=f"intro_mol_{m_name}", use_container_width=True):
                st.session_state.active_smiles = m_smi
                st.session_state.current_page = "Laboratory"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Three Pillar Features
    st.markdown("### 🔬 Laboratory Capabilities")
    f1, f2, f3 = st.columns(3)

    with f1:
        st.markdown("""
        <div class="lab-card">
            <div class="lab-card-title"><span style="color: #2DD4BF;">🧪</span> Molecular Analysis Lab</div>
            <p style="font-size: 14px; color: #B6C2D2; line-height: 1.6;">
                Parse any valid SMILES notation. View 2D constitutional graphs and full 3D interactive
                force-field minimized conformations with customizable representation models and van der Waals surfaces.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with f2:
        st.markdown("""
        <div class="lab-card">
            <div class="lab-card-title"><span style="color: #7DD3FC;">📐</span> Molecular Geometry Lab</div>
            <p style="font-size: 14px; color: #B6C2D2; line-height: 1.6;">
                Analyze VSEPR theory across steric numbers 2 to 6. Differentiate electron-domain vs
                molecular geometries, inspect Cartesian conformer bond angles, and explore lone-pair repulsion.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with f3:
        st.markdown("""
        <div class="lab-card">
            <div class="lab-card-title"><span style="color: #34D399;">🔗</span> Chemical Bonding Explorer</div>
            <p style="font-size: 14px; color: #B6C2D2; line-height: 1.6;">
                Investigate chemistry-aware Lewis structures, formal charges, octet rule exceptions (BF₃, SF₆),
                covalent bond orders, σ vs π framework decomposition, and dipole vector cancellations.
            </p>
        </div>
        """, unsafe_allow_html=True)

    render_footer()


# ============================================================
# PAGE 2: LABORATORY WORKSPACE
# ============================================================
elif st.session_state.current_page == "Laboratory":
    render_header()

    st.markdown("### 🧪 Molecular Analysis Laboratory")
    st.markdown("Input any valid chemical SMILES string, select a curated example, or choose from the quick-chips to generate 2D/3D structures and compute molecular descriptors.")

    # Molecular Input Bar
    in_col1, in_col2, in_col3, in_col4 = st.columns([3.5, 2.5, 1.2, 1])

    with in_col1:
        user_smiles_input = st.text_input(
            "Molecular SMILES Input",
            value=st.session_state.active_smiles,
            key="lab_smiles_input_box",
            placeholder="e.g. CCO, c1ccccc1, CC(=O)Oc1ccccc1C(=O)O, C, N, O",
            help="Type SMILES string and click Generate or press Enter."
        )

    with in_col2:
        curated_choice = st.selectbox(
            "Curated Molecular Library",
            ["-- Choose Curated Molecule --"] + list(EXAMPLE_MOLECULES.keys()),
            key="lab_curated_dropdown"
        )
        if curated_choice != "-- Choose Curated Molecule --":
            chosen_smi = EXAMPLE_MOLECULES[curated_choice]
            if chosen_smi != st.session_state.active_smiles:
                st.session_state.active_smiles = chosen_smi
                st.rerun()

    with in_col3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("⚡ Generate", type="primary", use_container_width=True, key="lab_btn_gen"):
            if user_smiles_input.strip() and user_smiles_input.strip() != st.session_state.active_smiles:
                st.session_state.active_smiles = user_smiles_input.strip()
                st.rerun()

    with in_col4:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Clear", use_container_width=True, key="lab_btn_clear"):
            st.session_state.active_smiles = ""
            st.rerun()

    # Quick Select Chips
    st.markdown("<div style='font-size: 11px; font-weight: 700; color: #7DD3FC; margin-top: -6px; margin-bottom: 6px; text-transform: uppercase;'>Quick-Select Molecule:</div>", unsafe_allow_html=True)
    chip_cols = st.columns(len(EXAMPLE_MOLECULES))
    for idx, (mol_name, mol_smi) in enumerate(EXAMPLE_MOLECULES.items()):
        with chip_cols[idx]:
            if st.button(mol_name, key=f"lab_chip_{mol_name}", use_container_width=True):
                if st.session_state.active_smiles != mol_smi:
                    st.session_state.active_smiles = mol_smi
                    st.rerun()

    st.markdown("<hr style='border: none; border-top: 1px solid #344258; margin: 18px 0;'>", unsafe_allow_html=True)

    # Process and Validate Active SMILES
    current_smi = st.session_state.active_smiles.strip()
    mol, parse_err = parse_smiles(current_smi)

    if not current_smi:
        st.info("💡 Enter a SMILES notation above or select a curated molecule to begin molecular visualization.")
    elif parse_err or mol is None:
        st.error(f"❌ {parse_err}")
    else:
        canonical = get_canonical_smiles(mol)
        props = calculate_properties(mol)

        st.markdown(f"""
        <div style="background: rgba(45, 212, 191, 0.1); border: 1px solid #2DD4BF; border-radius: 6px; padding: 10px 16px; margin-bottom: 18px; display: flex; justify-content: space-between; align-items: center;">
            <div style="font-weight: 700; color: #F1F5F9; font-size: 15px;">
                ✅ Active Molecular Target: <span style="color: #2DD4BF;">{props.get('Molecular Formula', '')}</span>
            </div>
            <div style="font-family: monospace; font-size: 13px; color: #7DD3FC; background: #151F33; padding: 4px 10px; border-radius: 4px; border: 1px solid #344258;">
                Canonical: {canonical}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Workspace Layout Controls
        st.markdown("#### 🌐 Molecular Viewport & Rendering Controls")

        v_col1, v_col2, v_col3 = st.columns([2.5, 2, 2])
        with v_col1:
            layout_mode = st.radio(
                "Viewport Layout",
                ["Split View (2D & 3D)", "3D Focus", "2D Graph Focus"],
                horizontal=True,
                key="lab_layout_radio"
            )
        with v_col2:
            st.session_state.viz_style = st.selectbox(
                "3D Model Style",
                ["Ball and Stick", "Stick", "Space Filling", "Wireframe", "Cartoon"],
                index=["Ball and Stick", "Stick", "Space Filling", "Wireframe", "Cartoon"].index(st.session_state.viz_style),
                key="lab_viz_style_select"
            )
        with v_col3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            st.session_state.show_surface = st.checkbox(
                "Show van der Waals Surface",
                value=st.session_state.show_surface,
                key="lab_surface_toggle"
            )

        # Conformer Generation
        with st.spinner("Generating 3D coordinates and minimizing force-field energy..."):
            mol3d = generate_3d_molecule(mol)

        # Viewport Rendering
        if layout_mode == "Split View (2D & 3D)":
            col_2d, col_3d = st.columns([1, 1.4])
            with col_2d:
                st.markdown("<div style='font-size: 13px; font-weight: 600; color: #7DD3FC; margin-bottom: 6px;'>2D Constitutional Graph</div>", unsafe_allow_html=True)
                img2d = generate_2d_image(mol, size=(600, 480))
                if img2d:
                    st.image(img2d, use_container_width=True)
            with col_3d:
                st.markdown("<div style='font-size: 13px; font-weight: 600; color: #7DD3FC; margin-bottom: 6px;'>3D Molecular Viewport</div>", unsafe_allow_html=True)
                if mol3d:
                    render_3dmol(
                        mol3d,
                        style=st.session_state.viz_style,
                        show_surface=st.session_state.show_surface,
                        height=480,
                        bg_color=st.session_state.canvas_bg,
                        viewer_id="lab_split_v"
                    )
                else:
                    st.warning("Could not generate 3D coordinates for this molecule. Displaying 2D graph.")
        elif layout_mode == "3D Focus":
            st.markdown("<div style='font-size: 13px; font-weight: 600; color: #7DD3FC; margin-bottom: 6px;'>3D Molecular Viewport Focus</div>", unsafe_allow_html=True)
            if mol3d:
                render_3dmol(
                    mol3d,
                    style=st.session_state.viz_style,
                    show_surface=st.session_state.show_surface,
                    height=540,
                    bg_color=st.session_state.canvas_bg,
                    viewer_id="lab_focus_v"
                )
            else:
                st.warning("Could not generate 3D coordinates.")
        else:
            st.markdown("<div style='font-size: 13px; font-weight: 600; color: #7DD3FC; margin-bottom: 6px;'>2D Chemical Graph</div>", unsafe_allow_html=True)
            img2d = generate_2d_image(mol, size=(750, 500))
            if img2d:
                st.image(img2d, use_container_width=False)

        st.markdown("<hr style='border: none; border-top: 1px solid #344258; margin: 24px 0;'>", unsafe_allow_html=True)

        # Molecular Descriptors Grid
        st.markdown("#### 📊 Physicochemical Descriptors & Covalent Framework")

        m1, m2, m3, m4, m5, m6 = st.columns(6)
        with m1:
            render_metric_card("Molecular Weight", str(props.get("Molecular Weight", "N/A")), " g/mol")
        with m2:
            render_metric_card("LogP", str(props.get("LogP", "N/A")))
        with m3:
            render_metric_card("TPSA", str(props.get("TPSA", "N/A")), " Å²")
        with m4:
            render_metric_card("H-Bond Donors", str(props.get("Hydrogen Bond Donors", "0")))
        with m5:
            render_metric_card("H-Bond Acceptors", str(props.get("Hydrogen Bond Acceptors", "0")))
        with m6:
            render_metric_card("Rotatable Bonds", str(props.get("Rotatable Bonds", "0")))

        m7, m8, m9, m10, m11, m12 = st.columns(6)
        with m7:
            render_metric_card("Sigma (σ) Bonds", str(props.get("Sigma (σ) Bonds", "0")))
        with m8:
            render_metric_card("Pi (π) Bonds", str(props.get("Pi (π) Bonds", "0")))
        with m9:
            render_metric_card("Total Rings", str(props.get("Ring Count", "0")))
        with m10:
            render_metric_card("Aromatic Rings", str(props.get("Aromatic Rings", "0")))
        with m11:
            render_metric_card("Fraction Csp³", str(props.get("Fraction Csp3", "0.0")))
        with m12:
            render_metric_card("Total Atoms (w/ H)", str(props.get("Total Atoms (including H)", "0")))

        # Scientific Charts
        st.markdown("#### 📈 Scientific Visualisations")
        c_chart1, c_chart2 = st.columns(2)

        with c_chart1:
            elem_counts = get_element_composition(mol)
            fig_elem = create_element_composition_chart(elem_counts)
            if fig_elem:
                st.plotly_chart(fig_elem, use_container_width=True)

        with c_chart2:
            bond_dist = get_bond_type_distribution(mol)
            fig_bonds = create_bond_distribution_chart(bond_dist)
            if fig_bonds:
                st.plotly_chart(fig_bonds, use_container_width=True)

        # Quick Actions Bar (CSV Export & Open in Reports)
        st.markdown("<hr style='border: none; border-top: 1px solid #344258; margin: 20px 0;'>", unsafe_allow_html=True)
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            prop_rows = [{"Descriptor": k, "Value": v} for k, v in props.items()]
            csv_bytes = pd.DataFrame(prop_rows).to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Export Descriptors CSV",
                data=csv_bytes,
                file_name=f"chemlab_{canonical[:10]}_descriptors.csv",
                mime="text/csv",
                use_container_width=True,
                key="lab_dl_csv"
            )
        with col_act2:
            if st.button("📑 Generate Official Laboratory Report", type="primary", use_container_width=True, key="lab_btn_to_reports"):
                st.session_state.current_page = "Reports"
                st.rerun()

    render_footer()


# ============================================================
# PAGE 3: MOLECULAR GEOMETRY LAB
# ============================================================
elif st.session_state.current_page == "Molecular Geometry":
    render_header()

    st.markdown("### 📐 Interactive Molecular Geometry Lab")
    st.markdown(
        "Explore **Valence Shell Electron Pair Repulsion (VSEPR)** theory and discover how electron domains, "
        "bonding pairs, and non-bonding lone pairs govern 3D spatial molecular shapes and bond angles."
    )

    tab_explore, tab_compare, tab_quiz = st.tabs([
        "🔬 VSEPR Molecule Explorer",
        "⚖️ Lone-Pair Repulsion Comparison",
        "🎯 Interactive Geometry Quiz"
    ])

    with tab_explore:
        selected_vsepr_name = st.selectbox(
            "Choose a Representative Geometry Example",
            list(VSEPR_DATABASE.keys()),
            key="vsepr_molecule_select"
        )

        v_data = VSEPR_DATABASE[selected_vsepr_name]
        v_mol, _ = parse_smiles(v_data["smiles"])
        v_mol3d = generate_3d_molecule(v_mol) if v_mol else None

        col_geom_vis, col_geom_info = st.columns([1.2, 1])

        with col_geom_vis:
            st.markdown(f"**3D Geometry Model: {selected_vsepr_name}**")
            if v_mol3d:
                render_3dmol(v_mol3d, style="Ball and Stick", height=420, bg_color=st.session_state.canvas_bg, viewer_id="geom_viewer")
            else:
                img = generate_2d_image(v_mol)
                if img:
                    st.image(img)

        with col_geom_info:
            st.markdown(f"#### {selected_vsepr_name}")
            st.markdown(f"**VSEPR Formula:** `{v_data['vsepr_formula']}` &nbsp;|&nbsp; **Central Atom:** {v_data['central_atom']}")

            # Key VSEPR descriptors
            g1, g2 = st.columns(2)
            with g1:
                render_metric_card("Molecular Geometry", v_data["molecular_geometry"])
                render_metric_card("Bonding Pairs", str(v_data["bonding_domains"]))
                render_metric_card("Ideal Bond Angle", f"{v_data['ideal_angle_deg']}°")
            with g2:
                render_metric_card("Electron-Domain Geom.", v_data["electron_domain_geometry"])
                render_metric_card("Lone Pairs (Central)", str(v_data["lone_pairs"]))
                render_metric_card("Experimental Angle", f"{v_data['experimental_angle_deg']}°")

            st.markdown(f"**Introductory Hybridization:** `{v_data['hybridization']}`")

        # Scientific mechanism callout
        st.markdown(f"""
        <div class="callout-teal">
            <b>Scientific Theory & Mechanism:</b><br>
            {v_data['explanation']}
        </div>
        """, unsafe_allow_html=True)

        # Real conformer angle measurement
        if v_mol3d:
            with st.expander("📏 Inspect Calculated 3D Conformer Angles", expanded=False):
                conformer_angles = calculate_conformer_angles(v_mol3d)
                if conformer_angles:
                    st.markdown("Measured bond angles computed directly from the minimized Cartesian coordinates:")
                    c_df = pd.DataFrame(conformer_angles)
                    st.dataframe(c_df[["label", "angle_deg"]].rename(columns={"label": "Bond Angle Connection", "angle_deg": "Calculated Conformer Angle (°)"}), use_container_width=True, hide_index=True)
                    st.caption("ℹ️ Note: Conformer angles computed via classical force fields (MMFF94) reflect minimum-energy steric configurations and may vary slightly from ideal gas-phase or crystallographic values.")
                else:
                    st.info("Structure contains fewer than 3 connected atoms to form a valence bond angle.")

    with tab_compare:
        st.markdown("#### ⚖️ The Classic Tetrahedral Series (CH₄ vs NH₃ vs H₂O)")
        st.markdown(
            "All three molecules possess a **tetrahedral electron-domain geometry** (Steric Number = 4), "
            "yet their actual molecular geometries and bond angles differ dramatically due to the electrostatic "
            "hierarchy of electron pair repulsion: **LP–LP > LP–BP > BP–BP**."
        )

        fig_vsepr_bar = create_vsepr_comparison_bar(TETRAHEDRAL_SERIES)
        st.plotly_chart(fig_vsepr_bar, use_container_width=True)

        comp_cols = st.columns(3)
        for i, s_item in enumerate(TETRAHEDRAL_SERIES):
            with comp_cols[i]:
                st.markdown(f"""
                <div class="lab-card">
                    <div class="lab-card-title">{s_item['name']}</div>
                    <p style="font-size: 13px; margin: 4px 0;"><b>Geometry:</b> {s_item['geometry']}</p>
                    <p style="font-size: 13px; margin: 4px 0;"><b>Bonding Domains:</b> {s_item['bonding']} &nbsp;|&nbsp; <b>Lone Pairs:</b> {s_item['lone_pairs']}</p>
                    <p style="font-size: 13px; margin: 4px 0;"><b>Bond Angle:</b> <span style="color: #2DD4BF; font-weight: 700;">{s_item['actual_angle']}°</span> (Ideal: {s_item['ideal_angle']}°)</p>
                    <hr style="margin: 8px 0; border: none; border-top: 1px solid #344258;">
                    <p style="font-size: 12px; color: #B6C2D2;">{s_item['repulsion_note']}</p>
                </div>
                """, unsafe_allow_html=True)

    with tab_quiz:
        st.markdown("#### 🎯 Predict the Geometry: VSEPR Assessment")
        st.markdown("Select your predicted answer for each question, then click **Submit Quiz** to check your score:")

        user_geom_answers = {}
        for q_idx, q in enumerate(GEOMETRY_QUIZ):
            st.markdown(f"**Q{q_idx + 1}. {q['question']}**")
            ans = st.radio(
                "Select one option:",
                q["options"],
                key=f"geom_quiz_radio_{q_idx}",
                index=None
            )
            user_geom_answers[q_idx] = ans
            st.markdown("---")

        c_sub1, c_sub2 = st.columns([1.5, 3])
        with c_sub1:
            if st.button("📝 Submit VSEPR Quiz", type="primary", use_container_width=True, key="btn_submit_vsepr_quiz"):
                st.session_state.geom_quiz_submitted = True
        with c_sub2:
            if st.button("🔄 Reset Quiz", use_container_width=False, key="btn_reset_vsepr_quiz"):
                st.session_state.geom_quiz_submitted = False
                st.rerun()

        if st.session_state.geom_quiz_submitted:
            score_vsepr = 0
            st.markdown("### 📋 Quiz Results & Explanations")
            for q_idx, q in enumerate(GEOMETRY_QUIZ):
                user_a = user_geom_answers.get(q_idx)
                if user_a == q["answer"]:
                    score_vsepr += 1
                    st.success(f"**Q{q_idx + 1}: Correct!** (Your answer: {user_a})<br>{q['explanation']}")
                else:
                    st.error(f"**Q{q_idx + 1}: Incorrect.** Your answer: {user_a or 'No answer'}. Correct: **{q['answer']}**<br>{q['explanation']}")
            
            pct = (score_vsepr / len(GEOMETRY_QUIZ)) * 100
            st.info(f"🏆 Final Score: **{score_vsepr} / {len(GEOMETRY_QUIZ)}** ({pct:.1f}%)")

    render_footer()


# ============================================================
# PAGE 4: CHEMICAL BONDING EXPLORER
# ============================================================
elif st.session_state.current_page == "Chemical Bonding":
    render_header()

    st.markdown("### 🔗 Chemical Bonding Explorer")
    st.markdown("Explore Lewis structures, covalent bond classification (σ and π framework), orbital hybridization, and molecular polarity vector cancellation.")

    b_tab_lewis, b_tab_inspect, b_tab_hybrid, b_tab_polar, b_tab_quiz = st.tabs([
        "🔬 Lewis Structures & Octet Rule",
        "🔍 Dynamic Structure Inspector",
        "🧪 Hybridization Models",
        "⚡ Molecular Polarity & Dipoles",
        "🎯 Bonding Practice Quiz"
    ])

    with b_tab_lewis:
        st.markdown("#### 🔬 Chemistry-Aware Lewis Structures")
        selected_lewis = st.selectbox(
            "Select Molecule for Lewis Analysis",
            list(LEWIS_DATABASE.keys()),
            key="lewis_select_dropdown"
        )
        l_info = LEWIS_DATABASE[selected_lewis]

        c_lew1, c_lew2 = st.columns([1.1, 1])

        with c_lew1:
            st.markdown(f"**Lewis Dot Representation: {selected_lewis}**")
            st.code(l_info["ascii_diagram"], language="text")

            render_metric_card("Total Valence Electrons", str(l_info["total_valence_electrons"]))
            render_metric_card("Bonding Pairs", str(l_info["bonding_pairs"]))

        with c_lew2:
            st.markdown("#### Structural Electronic Details")
            st.markdown(f"**Central Atom:** {l_info['central_atom']}")
            st.markdown(f"**Non-bonding Lone Pairs (Central):** {l_info['lone_pairs_central']}")
            st.markdown(f"**Ligand Lone Pairs:** {l_info['lone_pairs_ligands']}")

            st.markdown(f"""
            <div class="callout-teal">
                <b>Octet Rule Evaluation:</b><br>
                {l_info['octet_status']}
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="callout-blue">
                <b>Structural & Polarity Significance:</b><br>
                {l_info['notes']}
            </div>
            """, unsafe_allow_html=True)

    with b_tab_inspect:
        st.markdown("#### 🔍 Dynamic Atom & Bond Inspector")
        st.markdown("Inspect every atom and covalent bond in the currently active or user-entered structure:")

        inspect_smiles = st.text_input(
            "Enter SMILES for Inspection",
            value=st.session_state.active_smiles,
            key="inspect_smiles_field"
        )
        insp_mol, _ = parse_smiles(inspect_smiles)

        if insp_mol:
            insp_data = inspect_molecule_structure(insp_mol)

            st.markdown("##### Atoms in Molecule")
            st.dataframe(pd.DataFrame(insp_data["atoms"]), use_container_width=True, hide_index=True)

            st.markdown("##### Covalent Bonds (σ and π Decomposition)")
            st.dataframe(pd.DataFrame(insp_data["bonds"]), use_container_width=True, hide_index=True)
        else:
            st.warning("Please enter a valid SMILES string above.")

    with b_tab_hybrid:
        st.markdown("#### 🧪 Guided Hybridization Models")
        st.markdown(
            "In valence-bond theory, atomic orbitals hybridize to form equivalent directional orbitals "
            "that maximize bonding overlap and minimize electrostatic repulsion."
        )

        for hyb_key, h_data in HYBRIDIZATION_INFO.items():
            st.markdown(f"""
            <div class="lab-card">
                <div class="lab-card-title" style="color: #2DD4BF;">{h_data['name']} ({h_data['geometry']} — {h_data['bond_angle']})</div>
                <p style="font-size: 13px; margin: 4px 0;"><b>Orbital Mixing:</b> {h_data['orbital_mixing']}</p>
                <p style="font-size: 13px; margin: 4px 0;"><b>Unhybridized p Orbitals:</b> {h_data['unhybridized_p']}</p>
                <p style="font-size: 13px; margin: 4px 0;"><b>Representative Examples:</b> {h_data['examples']}</p>
                <p style="font-size: 12px; color: #B6C2D2; margin-top: 8px;"><b>Orbital Overlap Mechanism:</b> {h_data['overlap_description']}</p>
            </div>
            """, unsafe_allow_html=True)

    with b_tab_polar:
        st.markdown("#### ⚡ Molecular Polarity: Bond Dipoles vs Vector Cancellation")
        st.markdown(
            "A molecule with polar bonds is **not necessarily a polar molecule**. "
            "Overall molecular polarity is the **vector sum** of individual bond dipoles ($\vec{\mu}_{\\text{net}} = \sum \vec{\mu}_{\\text{bond}}$). "
            "Symmetric geometries can lead to exact vector cancellation!"
        )

        for pol in POLARITY_EXAMPLES:
            st.markdown(f"""
            <div class="lab-card">
                <div class="lab-card-title">{pol['molecule']} &nbsp;—&nbsp; <span style="font-size: 14px; font-weight: 700; color: #2DD4BF;">{pol['dipole_moment']}</span></div>
                <div style="font-size: 13px; color: #B6C2D2; margin-bottom: 6px;">
                    <b>Geometry & Symmetry:</b> {pol['geometry']} ({pol['symmetry']})<br>
                    <b>Bond Nature:</b> {pol['bonds']}
                </div>
                <div style="font-size: 12px; color: #F1F5F9; line-height: 1.5; background: #151F33; padding: 12px; border-radius: 6px; border-left: 3px solid #2DD4BF; border: 1px solid #344258;">
                    {pol['explanation']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with b_tab_quiz:
        st.markdown("#### 🎯 Chemical Bonding Mastery Quiz")
        st.markdown("Select your answer for each bonding question, then click **Submit Quiz**:")

        user_bonding_answers = {}
        for b_idx, b_q in enumerate(BONDING_QUIZ):
            st.markdown(f"**Q{b_idx + 1}. {b_q['question']}**")
            b_ans = st.radio(
                "Select one option:",
                b_q["options"],
                key=f"bonding_quiz_radio_{b_idx}",
                index=None
            )
            user_bonding_answers[b_idx] = b_ans
            st.markdown("---")

        cb_sub1, cb_sub2 = st.columns([1.5, 3])
        with cb_sub1:
            if st.button("📝 Submit Bonding Quiz", type="primary", use_container_width=True, key="btn_submit_bonding_quiz"):
                st.session_state.bonding_quiz_submitted = True
        with cb_sub2:
            if st.button("🔄 Reset Quiz", use_container_width=False, key="btn_reset_bonding_quiz"):
                st.session_state.bonding_quiz_submitted = False
                st.rerun()

        if st.session_state.bonding_quiz_submitted:
            score_b = 0
            st.markdown("### 📋 Quiz Results & Explanations")
            for b_idx, b_q in enumerate(BONDING_QUIZ):
                user_a = user_bonding_answers.get(b_idx)
                if user_a == b_q["answer"]:
                    score_b += 1
                    st.success(f"**Q{b_idx + 1}: Correct!** (Your answer: {user_a})<br>{b_q['explanation']}")
                else:
                    st.error(f"**Q{b_idx + 1}: Incorrect.** Your answer: {user_a or 'No answer'}. Correct: **{b_q['answer']}**<br>{b_q['explanation']}")
            
            pct_b = (score_b / len(BONDING_QUIZ)) * 100
            st.info(f"🏆 Final Score: **{score_b} / {len(BONDING_QUIZ)}** ({pct_b:.1f}%)")

    render_footer()


# ============================================================
# PAGE 5: COMPARATIVE ANALYSIS
# ============================================================
elif st.session_state.current_page == "Comparative Analysis":
    render_header()

    st.markdown("### 📊 Multi-Molecule Structure–Property Comparison")
    st.markdown(
        "Compare physicochemical properties and bonding parameters across multiple chemical structures simultaneously. "
        "Enter molecules in the format: `Molecule Name, SMILES`."
    )

    default_multi = (
        "Ethanol,CCO\n"
        "Benzene,c1ccccc1\n"
        "Phenol,Oc1ccccc1\n"
        "Acetic Acid,CC(=O)O\n"
        "Aspirin,CC(=O)Oc1ccccc1C(=O)O\n"
        "Caffeine,CN1C=NC2=C1C(=O)N(C(=O)N2C)C"
    )

    multi_text = st.text_area("Molecules to Compare", value=default_multi, height=160, key="multi_mol_textarea")

    rows = []
    radar_records = []

    for line in multi_text.splitlines():
        if "," not in line:
            continue
        parts = line.split(",", 1)
        name, smiles = parts[0].strip(), parts[1].strip()
        m, _ = parse_smiles(smiles)
        if m:
            p = calculate_properties(m)
            rows.append({
                "Molecule": name,
                "Formula": p["Molecular Formula"],
                "MW (g/mol)": p["Molecular Weight"],
                "LogP": p["LogP"],
                "TPSA (Å²)": p["TPSA"],
                "HBD": p["Hydrogen Bond Donors"],
                "HBA": p["Hydrogen Bond Acceptors"],
                "Rot. Bonds": p["Rotatable Bonds"],
                "Rings": p["Ring Count"],
                "Sigma (σ)": p["Sigma (σ) Bonds"],
                "Pi (π)": p["Pi (π) Bonds"]
            })
            radar_records.append({"name": name, "props": p})

    if rows:
        df_comp = pd.DataFrame(rows)
        st.dataframe(df_comp, use_container_width=True, hide_index=True)

        # Plotly Radar Comparison
        fig_radar = create_multi_property_radar(radar_records[:6])
        if fig_radar:
            st.plotly_chart(fig_radar, use_container_width=True)

        c_dl1, c_dl2 = st.columns(2)
        with c_dl1:
            csv_c = df_comp.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download Comparison CSV",
                data=csv_c,
                file_name="chemlab_multi_molecule_comparison.csv",
                mime="text/csv",
                key="btn_dl_multi_csv"
            )
        with c_dl2:
            if st.button("📑 Generate Batch Laboratory PDF Report", type="primary", use_container_width=True, key="btn_compare_to_reports"):
                st.session_state.current_page = "Reports"
                st.rerun()
    else:
        st.warning("Please enter valid lines in the format: Molecule Name, SMILES")

    render_footer()


# ============================================================
# PAGE 6: REPORTS (DEDICATED NAVIGATION SECTION)
# ============================================================
elif st.session_state.current_page == "Reports":
    render_header()

    st.markdown("### 📑 Scientific Report Generation Studio")
    st.markdown(
        "Generate and compile publication-quality PDF laboratory reports. "
        "Choose between a detailed Single-Molecule Analysis Report or a Multi-Molecule Batch Laboratory Report."
    )

    report_mode = st.radio(
        "Report Mode",
        ["Single Molecule Comprehensive Report", "Multi-Molecule Batch Laboratory Report"],
        horizontal=True,
        key="report_mode_radio"
    )

    st.markdown("<hr style='border: none; border-top: 1px solid #344258; margin: 16px 0;'>", unsafe_allow_html=True)

    if report_mode == "Single Molecule Comprehensive Report":
        st.markdown("#### 🔬 Single Target Molecular Report")
        
        c_rep1, c_rep2 = st.columns([3, 2])
        with c_rep1:
            report_smiles = st.text_input(
                "Target Molecule SMILES",
                value=st.session_state.active_smiles,
                key="rep_target_smiles"
            )
        with c_rep2:
            st.markdown(f"**Student Analyst:** {st.session_state.student_name or 'Alex Smith (Default)'}")
            st.markdown(f"**Registration ID:** {st.session_state.registration_number or 'RA2311003010 (Default)'}")

        r_mol, r_err = parse_smiles(report_smiles)

        if not report_smiles.strip():
            st.info("Enter a SMILES notation above to generate a report.")
        elif r_err or r_mol is None:
            st.error(f"❌ {r_err}")
        else:
            r_props = calculate_properties(r_mol)
            r_canon = get_canonical_smiles(r_mol)

            st.markdown(f"""
            <div class="callout-teal">
                <b>Ready to compile report for:</b> {r_props.get('Molecular Formula', '')} &nbsp;|&nbsp; 
                MW: {r_props.get('Molecular Weight', '')} g/mol &nbsp;|&nbsp;
                Canonical SMILES: <code>{r_canon}</code>
            </div>
            """, unsafe_allow_html=True)

            # Preview content summary
            with st.expander("👁️ Preview Report Summary & Content Sections", expanded=True):
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    st.markdown("**Section 1: Molecular Graphics**")
                    st.markdown("• 2D Graph Representation (Connectivity Matrix)")
                    st.markdown("• 3D Ball-and-Stick Conformer (PCA Spatial Projection)")
                    st.markdown("**Section 2: Covalent Framework**")
                    st.markdown(f"• Total Atoms: {r_props.get('Total Atoms (including H)', 0)} (Heavy Atoms: {r_props.get('Heavy Atoms', 0)})")
                    st.markdown(f"• Sigma (σ) Bonds: {r_props.get('Sigma (σ) Bonds', 0)}")
                    st.markdown(f"• Pi (π) Bonds: {r_props.get('Pi (π) Bonds', 0)}")
                with col_p2:
                    st.markdown("**Section 3: Physicochemical Descriptors**")
                    st.markdown(f"• Lipophilicity: LogP = {r_props.get('LogP', 'N/A')}")
                    st.markdown(f"• Polar Surface Area: TPSA = {r_props.get('TPSA', 'N/A')} Å²")
                    st.markdown(f"• Hydrogen Bonding: {r_props.get('Hydrogen Bond Donors', 0)} Donors, {r_props.get('Hydrogen Bond Acceptors', 0)} Acceptors")
                    st.markdown("**Section 4: Summary Conclusions & Interpretations**")

            with st.spinner("Compiling high-resolution molecular analysis PDF report..."):
                single_pdf = generate_molecule_pdf(
                    report_smiles,
                    r_mol,
                    r_props,
                    student_name=st.session_state.student_name,
                    reg_no=st.session_state.registration_number
                )

            st.download_button(
                "📄 Compile & Download PDF Laboratory Report",
                data=single_pdf,
                file_name=f"ChemLab_Report_{r_canon[:8]}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
                key="btn_download_single_pdf"
            )

    else:
        st.markdown("#### 📑 Multi-Molecule Batch Laboratory Report")
        st.markdown("Enter multiple SMILES strings (one per line) or use the batch below:")

        default_batch_smiles = "CCO\nc1ccccc1\nOc1ccccc1\nCC(=O)O\nCC(=O)Oc1ccccc1C(=O)O"
        batch_text = st.text_area("SMILES Batch List", value=default_batch_smiles, height=140, key="batch_smiles_area")

        valid_records = []
        invalid_list = []

        for line in batch_text.splitlines():
            smi = line.strip()
            if not smi: continue
            bmol, berr = parse_smiles(smi)
            if bmol:
                bprops = calculate_properties(bmol)
                valid_records.append((smi, bmol, bprops))
            else:
                invalid_list.append(smi)

        if invalid_list:
            st.warning(f"⚠️ Skipped invalid entries: {', '.join(invalid_list)}")

        if valid_records:
            st.success(f"✅ {len(valid_records)} valid molecules queued for multi-page batch report compilation.")

            preview_table = [
                {"Index": i, "SMILES": rec[0], "Formula": rec[2]["Molecular Formula"], "MW (g/mol)": rec[2]["Molecular Weight"]}
                for i, rec in enumerate(valid_records, start=1)
            ]
            st.dataframe(pd.DataFrame(preview_table), use_container_width=True, hide_index=True)

            with st.spinner(f"Compiling multi-page report for {len(valid_records)} molecules..."):
                multi_pdf = generate_multi_molecule_pdf(
                    student_name=st.session_state.student_name,
                    reg_no=st.session_state.registration_number,
                    molecule_records=valid_records
                )

            st.download_button(
                f"📄 Compile & Download Multi-Molecule Batch Report ({len(valid_records)} Molecules)",
                data=multi_pdf,
                file_name="ChemLab_Batch_Molecular_Report.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
                key="btn_download_multi_pdf"
            )
        else:
            st.info("Enter at least one valid SMILES string to compile the batch report.")

    render_footer()


# ============================================================
# PAGE 7: ABOUT
# ============================================================
elif st.session_state.current_page == "About":
    render_header()

    st.markdown("### ℹ️ About ChemLab")

    st.markdown("""
    **ChemLab** is an interactive virtual chemistry laboratory engineered to provide undergraduate engineering and science students
    with an intuitive, scientifically rigorous platform for molecular visualization, VSEPR geometry analysis, and chemical bonding exploration.
    """)

    st.markdown("""
    #### ⚙️ Technical Architecture & Stack
    * **Application Framework:** Streamlit (Python 3.8+)
    * **Cheminformatics Engine:** RDKit (MolFromSmiles, Descriptors, Crippen, Lipinski, AllChem ETKDGv3, MMFF94 force field)
    * **3D Molecular Rendering:** py3Dmol (WebGL / Three.js molecular graphics with CPK coloring and VDW surfaces)
    * **Scientific Data Visualization:** Plotly Graph Objects & Express (Midnight Laboratory Theme)
    * **Automated PDF Engine:** ReportLab DocumentTemplate with dynamic PCA conformer projection
    """)

    st.markdown("<hr style='border: none; border-top: 1px solid #344258; margin: 24px 0;'>", unsafe_allow_html=True)
    st.markdown("#### 👨‍🔬 Authorship & Academic Credits")
    st.markdown("**Application Enhancement & UI/UX Design:**")
    st.markdown("<div style='font-size: 16px; font-weight: 700; color: #2DD4BF;'>Designed by R Vishwa Janagan</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Original Foundation Project:**")
    st.markdown("""
    * **Dr. R. Subramanian**, Assistant Professor, Division of Chemistry, School of Sciences,
      Faculty of Engineering and Technology, SRM Institute of Science and Technology, Tiruchirappalli.
    * Original Source: *Cheminformatics Representation of 2D and 3D Chemical Structure*
    """)

    render_footer()
