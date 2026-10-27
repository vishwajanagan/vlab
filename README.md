# ⚗️ ChemLab — Interactive Virtual Chemistry Laboratory

> *"Explore molecules. Understand bonding. Visualise chemistry."*

**Designed by R Vishwa Janagan**  
*Based on the original cheminformatics foundation by Dr. R. Subramanian (SRMIST)*

---

## 🔬 Overview

**ChemLab** is a premium scientific-computing virtual chemistry laboratory engineered for undergraduate engineering and science students. Built on Python, Streamlit, and RDKit, ChemLab couples computational cheminformatics with high-performance WebGL 3D molecular visualization (`py3Dmol`), interactive Plotly data visualizations, modular educational labs (Molecular Geometry Lab & Chemical Bonding Explorer), and an automated PDF laboratory reporting studio.

The interface is built upon the **Midnight Laboratory** visual design system, delivering a focused, dark-slate scientific workstation aesthetic.

---

## 🎨 Midnight Laboratory Design System

ChemLab is styled with a custom dark-slate scientific theme:
* **Canvas / Main Background:** `#0B1020`
* **Sidebar:** `#10182A`
* **Workspace Panels:** `#151F33`
* **Elevated Cards:** `#1C2940`
* **Primary Accent:** `#2DD4BF` (Scientific Teal)
* **Secondary Accent:** `#7DD3FC` (Cyan)
* **Primary Text:** `#F1F5F9` (High Contrast)
* **Secondary Text:** `#B6C2D2` (Muted Slate)
* **Borders:** `#344258`
* **Typography:** `Inter`, with clean sans-serif system fallbacks.

---

## 📁 Application Architecture & Grouped Navigation

```
WORKSPACE
├── Introduction           # Scientific workstation overview & quick-launch targets
├── Laboratory             # Primary molecular analysis, 3D viewport, and descriptors
├── Molecular Geometry     # VSEPR theory, Cartesian conformer angles, and quiz
├── Chemical Bonding       # Lewis dot structures, σ/π decomposition, polarity cancellation
└── Comparative Analysis   # Multi-molecule property tables and Plotly radar profiles

OUTPUTS
└── Reports                # Dedicated PDF Laboratory Reporting Studio (Single & Batch)

INFORMATION
└── About                  # Architecture, technologies, and creator credits
```

---

## ✨ Core Features & Enhancements

### 1. 🧪 Laboratory Workspace
* **Robust Molecular Input:** Accepts standard SMILES strings with input validation, instant feedback, and a curated library of common molecules (Ethanol, Benzene, Phenol, Acetic Acid, Aspirin, Caffeine, Methane, Ammonia, Water).
* **Multi-Format Visualisation:**
  * High-resolution 2D chemical graph depiction.
  * Interactive 3D molecular viewer (`py3Dmol`) supporting multiple representation styles: **Ball and Stick**, **Stick**, **Space Filling (VDW)**, **Wireframe**, and **Cartoon**.
  * Dynamic van der Waals surface overlay.
  * Working toolbar controls embedded inside the viewport: **🔄 Reset Camera** (restores zoom and centers model) and **🌀 Auto-Spin** (toggles continuous rotation cleanly without orphan intervals).
* **Comprehensive Descriptor Engine:** Computes Molecular Weight, Exact Mass, LogP (lipophilicity), Topological Polar Surface Area (TPSA), Hydrogen-Bond Donors (HBD) and Acceptors (HBA), Rotatable Bonds, Total Rings, Aromatic Rings, Fraction Csp³, and Molar Refractivity.
* **Covalent Framework Breakdown:** Automatically calculates heavy-atom bonds, framework $\sigma$ bonds (including implicit/explicit hydrogens), and $\pi$ bonds (using aromatic Kekulé delocalization).

### 2. 📐 Interactive Molecular Geometry Lab
* **VSEPR Theory Explorer:** Learn how electron-pair repulsion dictates 3D geometry across steric numbers 2 through 6 ($\text{CO}_2$, $\text{BF}_3$, $\text{CH}_4$, $\text{NH}_3$, $\text{H}_2\text{O}$, $\text{C}_2\text{H}_4$, $\text{C}_2\text{H}_2$, $\text{SF}_4$, $\text{ClF}_3$, $\text{PCl}_5$, $\text{SF}_6$).
* **Angle Precision & Comparison:** Delineates ideal textbook angles, experimental literature values, and real Cartesian conformer angles measured directly from 3D coordinates.
* **Tetrahedral Series Comparison:** Interactive Plotly bar chart comparing $\text{CH}_4$ ($109.5^\circ$), $\text{NH}_3$ ($107.0^\circ$), and $\text{H}_2\text{O}$ ($104.5^\circ$) showing the electrostatic repulsion hierarchy: $\text{LP–LP} > \text{LP–BP} > \text{BP–BP}$.
* **Predictive VSEPR Quiz:** Interactive self-assessment with instant feedback, scoring, and explanations.

### 3. 🔗 Chemical Bonding Explorer
* **Chemistry-Aware Lewis Structures:** Curated dot diagrams detailing valence electrons, bonding pairs, central and ligand lone pairs, formal charges, and octet status (incomplete octet in $\text{BF}_3$, coordinate bonding in $\text{CO}$, and expanded octet in $\text{SF}_6$).
* **Dynamic Atom & Bond Inspector:** Inspect element electronegativities, formal charges, valences, hybridizations, bond orders, and bond polarities ($\Delta\text{EN}$ classification).
* **Hybridization Models:** Guided explanations of $sp$, $sp^2$, and $sp^3$ orbital mixing and unhybridized $p$-orbital $\pi$ overlap.
* **Molecular Polarity & Dipole Cancellation:** Vector analysis showing why molecules with polar bonds (such as linear $\text{CO}_2$ or tetrahedral $\text{CH}_4$) possess zero net molecular dipole moment due to symmetry cancellation.

### 4. 📑 Dedicated Report Generation Studio
* **Single-Molecule Analysis Report:** Compiles a comprehensive PDF laboratory report with student metadata, 2D connectivity, 3D PCA projection, descriptor tables with scientific interpretations, and takeaway points.
* **Multi-Molecule Batch Laboratory Report:** Compiles a multi-page PDF document evaluating a collection of chemical targets with page breaks, comparative tables, and cheminformatics methodology notes.

---

## 🚀 Quickstart Guide

### 1. Launch ChemLab
From the project workspace:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### 2. Run Automated Unit Tests
```bash
python -m unittest discover -s tests -p "test_*.py"
```
All 14 automated unit tests verify SMILES parsing, descriptor calculations, $\sigma/\pi$ bond decompositions, VSEPR database integrity, structure inspection, and PDF compilation.

---

## 📄 Authorship & Credits

* **Application Enhancement & UI/UX Design:** Designed by **R Vishwa Janagan**
* **Original Foundation:** Developed by **Dr. R. Subramanian**, Division of Chemistry, School of Sciences, SRM Institute of Science and Technology, Tiruchirappalli.
* **Footer Notice:** © R Vishwa Janagan
