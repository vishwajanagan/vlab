"""
ChemLab - Scientific Reporting Engine
Generates comprehensive student molecular analysis PDF reports using ReportLab,
incorporating 2D/3D structure graphics, descriptor tables, interpretations, and educational code.
"""

# Compatibility fix for Python 3.8 openssl_md5 not supporting usedforsecurity
import hashlib
_original_md5 = hashlib.md5
def _safe_md5(*args, **kwargs):
    kwargs.pop("usedforsecurity", None)
    return _original_md5(*args, **kwargs)
hashlib.md5 = _safe_md5

from io import BytesIO
import os
import tempfile
import numpy as np
import matplotlib.pyplot as plt
from rdkit import Chem
from rdkit.Chem import Draw

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
    Preformatted
)
from reportlab.lib.units import inch

from .core import generate_3d_molecule

def save_2d_structure_png(mol):
    """Save 2D depiction as a clean temporary PNG file for PDF inclusion."""
    if mol is None:
        return None
    try:
        img = Draw.MolToImage(mol, size=(700, 500))
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp.close()
        img.save(tmp.name)
        return tmp.name
    except Exception:
        return None

def save_3d_structure_png(mol):
    """
    Project 3D conformer coordinates onto the principal viewing plane (PCA)
    and produce a high-resolution ball-and-stick diagram for ReportLab.
    """
    if mol is None:
        return None

    mol3d = generate_3d_molecule(mol)
    if mol3d is None or mol3d.GetNumConformers() == 0:
        return None

    try:
        conf = mol3d.GetConformer()
        n_atoms = mol3d.GetNumAtoms()

        coords = np.array([
            [conf.GetAtomPosition(i).x, conf.GetAtomPosition(i).y, conf.GetAtomPosition(i).z]
            for i in range(n_atoms)
        ], dtype=float)

        centered = coords - coords.mean(axis=0)
        if n_atoms >= 3 and np.linalg.matrix_rank(centered) >= 2:
            _, _, vh = np.linalg.svd(centered, full_matrices=False)
            projected = centered @ vh[:2].T
        else:
            projected = centered[:, :2]

        cpk = {
            "H": "#FFFFFF", "C": "#3F3F3F", "N": "#2F5BFF",
            "O": "#E53935", "F": "#65C466", "P": "#F39C12",
            "S": "#F4D03F", "Cl": "#27AE60", "Br": "#8E3B2F",
            "I": "#8E44AD"
        }
        sizes = {
            "H": 80, "C": 240, "N": 270, "O": 285, "F": 260,
            "P": 300, "S": 310, "Cl": 310, "Br": 330, "I": 350
        }

        fig, ax = plt.subplots(figsize=(8.5, 6.0), facecolor="white")
        ax.set_facecolor("white")

        # Draw bonds
        for bond in mol3d.GetBonds():
            i, j = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
            x1, y1 = projected[i]
            x2, y2 = projected[j]
            dx, dy = x2 - x1, y2 - y1
            length = float(np.hypot(dx, dy))
            if length == 0:
                continue

            px, py = -dy / length, dx / length
            btype = bond.GetBondType()
            if btype == Chem.BondType.DOUBLE:
                offsets = (-0.035, 0.035)
            elif btype == Chem.BondType.TRIPLE:
                offsets = (-0.055, 0.0, 0.055)
            else:
                offsets = (0.0,)

            for off in offsets:
                ax.plot(
                    [x1 + px * off, x2 + px * off],
                    [y1 + py * off, y2 + py * off],
                    color="#64748B", linewidth=2.8,
                    solid_capstyle="round", zorder=1
                )

        # Draw atoms
        for i, atom in enumerate(mol3d.GetAtoms()):
            sym = atom.GetSymbol()
            x, y = projected[i]
            ax.scatter(
                x, y,
                s=sizes.get(sym, 240),
                c=cpk.get(sym, "#CBD5E1"),
                edgecolors="#1E293B",
                linewidths=1.2,
                zorder=3
            )
            if sym not in ("H", "C"):
                ax.text(
                    x, y, sym,
                    ha="center", va="center",
                    fontsize=8, fontweight="bold",
                    color="black", zorder=4
                )

        xmin, ymin = projected.min(axis=0)
        xmax, ymax = projected.max(axis=0)
        width = max(xmax - xmin, 1.0)
        height = max(ymax - ymin, 1.0)
        pad = 0.22 * max(width, height)

        ax.set_xlim(xmin - pad, xmax + pad)
        ax.set_ylim(ymin - pad, ymax + pad)
        ax.set_aspect("equal", adjustable="box")
        ax.axis("off")
        ax.set_title("3D Conformer Projection (Ball-and-Stick)", fontsize=14, fontweight="bold", pad=12, color="#0F172A")

        fig.tight_layout(pad=1.0)

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp.close()
        fig.savefig(tmp.name, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return tmp.name
    except Exception:
        return None

def get_property_interpretation(property_name, value, properties):
    """Educational interpretation for molecular descriptors."""
    if property_name == "Molecular Formula":
        return "Shows elemental composition; basis for stoichiometry and empirical analysis."
    if property_name == "Molecular Weight":
        return f"Average mass {value} g/mol; directly correlates with size, volatility, and membrane permeability."
    if property_name == "Exact Molecular Weight":
        return "Monoisotopic mass calculated from exact isotopic masses; essential for high-resolution MS."
    if property_name == "LogP":
        if value < 0:
            return f"LogP = {value}: Strongly hydrophilic; favours aqueous phase."
        elif value < 1:
            return f"LogP = {value}: Low to moderate lipophilicity with good water solubility."
        elif value < 3:
            return f"LogP = {value}: Balanced hydrophilic/lipophilic ratio; optimal for drug-like absorption."
        else:
            return f"LogP = {value}: High lipophilicity; strong membrane affinity and lower water solubility."
    if property_name == "TPSA":
        if value < 60:
            return f"TPSA = {value} Å²: Low polar surface area; high membrane permeability and BBB penetration potential."
        elif value < 140:
            return f"TPSA = {value} Å²: Moderate polar surface area; suitable for oral bio-availability."
        else:
            return f"TPSA = {value} Å²: High polar surface area; increased water solubility but limited membrane crossing."
    if property_name == "Hydrogen Bond Donors":
        return f"{value} donor site(s) (OH, NH) capable of donating hydrogen bonds."
    if property_name == "Hydrogen Bond Acceptors":
        return f"{value} acceptor site(s) (O, N, F) capable of accepting hydrogen bonds."
    if property_name == "Rotatable Bonds":
        return f"{value} rotatable bond(s); quantifies molecular conformational flexibility."
    if property_name == "Ring Count":
        return f"{value} total ring(s); contributes to rigidity and 3D structural complexity."
    if property_name == "Aromatic Rings":
        return f"{value} aromatic ring(s); indicates π-electron delocalization and planar regions."
    if property_name == "Aliphatic Rings":
        return f"{value} saturated/aliphatic ring(s); provides non-aromatic 3D conformation."
    if property_name == "Sigma (σ) Bonds":
        return f"{value} σ bonds forming the core covalent single-bond structural framework."
    if property_name == "Pi (π) Bonds":
        return f"{value} π bonds from multiple bonds and aromatic systems responsible for reactivity and resonance."
    if property_name == "Fraction Csp3":
        return f"{value}: Ratio of sp³ hybridized carbons to total carbons; reflects non-planar saturation."
    return "Computational structural descriptor evaluated via RDKit."

def build_key_interpretation_points(properties):
    """Generate concise educational conclusion bullet points."""
    points = [
        f"<b>Molecular Identity:</b> Formula <b>{properties.get('Molecular Formula', 'N/A')}</b> with Molecular Weight <b>{properties.get('Molecular Weight', 'N/A')} g/mol</b>.",
        f"<b>Lipophilicity & Polarity:</b> LogP = <b>{properties.get('LogP', 'N/A')}</b> and TPSA = <b>{properties.get('TPSA', 'N/A')} Å²</b>. Demonstrates balance between aqueous solubility and membrane affinity.",
        f"<b>Intermolecular Forces:</b> Contains <b>{properties.get('Hydrogen Bond Donors', 0)}</b> H-bond donor(s) and <b>{properties.get('Hydrogen Bond Acceptors', 0)}</b> acceptor(s).",
        f"<b>Bonding Framework:</b> Calculated <b>{properties.get('Sigma (σ) Bonds', 0)}</b> σ bonds and <b>{properties.get('Pi (π) Bonds', 0)}</b> π bonds across <b>{properties.get('Total Atoms (including H)', 0)}</b> atoms."
    ]
    return points

def generate_molecule_pdf(input_smiles, mol, properties, student_name="Student", reg_no="N/A"):
    """Generate comprehensive single-molecule PDF report."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "LabTitle", parent=styles["Title"],
        fontSize=18, leading=22, alignment=TA_CENTER, textColor=HexColor("#0F172A")
    )
    subtitle_style = ParagraphStyle(
        "LabSubtitle", parent=styles["Normal"],
        fontSize=11, leading=14, alignment=TA_CENTER, textColor=HexColor("#0D9488")
    )
    heading_style = ParagraphStyle(
        "LabHeading", parent=styles["Heading2"],
        fontSize=12, leading=16, textColor=HexColor("#1E293B"), spaceBefore=10, spaceAfter=6
    )
    body_style = ParagraphStyle(
        "LabBody", parent=styles["BodyText"],
        fontSize=9, leading=13, alignment=TA_JUSTIFY, textColor=HexColor("#334155")
    )
    small_style = ParagraphStyle(
        "LabSmall", parent=styles["Normal"],
        fontSize=8, leading=10, textColor=HexColor("#1E293B")
    )
    header_cell = ParagraphStyle(
        "LabHeaderCell", parent=styles["Normal"],
        fontSize=8, leading=10, textColor=colors.white, alignment=TA_CENTER, fontName="Helvetica-Bold"
    )

    story = [
        Paragraph("CHEMLAB — VIRTUAL CHEMISTRY LABORATORY", title_style),
        Spacer(1, 4),
        Paragraph("MOLECULAR ANALYSIS AND CHEMINFORMATICS REPORT", subtitle_style),
        Spacer(1, 12)
    ]

    # Student metadata table
    meta_data = [
        ["Student Name", student_name or "Student Analyst", "Date / Time", "Computational Lab Session"],
        ["Registration No.", reg_no or "N/A", "Input SMILES", input_smiles],
        ["Canonical SMILES", Chem.MolToSmiles(mol), "Formula", properties.get("Molecular Formula", "N/A")]
    ]
    meta_table = Table(meta_data, colWidths=[1.5*inch, 2.0*inch, 1.4*inch, 2.3*inch])
    meta_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 0), (0, -1), HexColor("#F1F5F9")),
        ("BACKGROUND", (2, 0), (2, -1), HexColor("#F1F5F9")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("PADDING", (0, 0), (-1, -1), 4)
    ]))
    story += [meta_table, Spacer(1, 10)]

    # Molecular structures (2D and 3D)
    img2d = save_2d_structure_png(mol)
    img3d = save_3d_structure_png(mol)
    temp_images = [img for img in [img2d, img3d] if img]

    if img2d and img3d:
        struct_table = Table([[
            Image(img2d, width=3.2*inch, height=2.2*inch),
            Image(img3d, width=3.2*inch, height=2.2*inch)
        ]], colWidths=[3.5*inch, 3.5*inch])
        struct_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
        ]))
        story += [
            Paragraph("1. Molecular Structures (2D Connectivity & 3D Conformer)", heading_style),
            struct_table,
            Spacer(1, 6),
            Paragraph("<b>Figure 1:</b> Left: 2D constitutional graph connectivity. Right: 3D ball-and-stick geometry optimized with MMFF94 force field.", body_style),
            Spacer(1, 10)
        ]
    elif img2d:
        story += [
            Paragraph("1. 2D Molecular Structure", heading_style),
            Image(img2d, width=4.5*inch, height=3.0*inch),
            Spacer(1, 10)
        ]

    # Property table with interpretations
    story.append(Paragraph("2. Calculated Descriptors and Scientific Interpretation", heading_style))
    prop_rows = [[
        Paragraph("Descriptor", header_cell),
        Paragraph("Calculated Value", header_cell),
        Paragraph("Scientific Interpretation", header_cell)
    ]]

    for key, value in properties.items():
        interp = get_property_interpretation(key, value, properties)
        prop_rows.append([
            Paragraph(f"<b>{key}</b>", small_style),
            Paragraph(str(value), small_style),
            Paragraph(interp, small_style)
        ])

    prop_table = Table(prop_rows, colWidths=[1.8*inch, 1.1*inch, 4.1*inch], repeatRows=1)
    prop_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#0D9488")),
        ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), HexColor("#F8FAFC")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 3.5)
    ]))
    story += [prop_table, Spacer(1, 10)]

    # Key takeaway points
    story.append(Paragraph("3. Summary & Educational Conclusions", heading_style))
    for pt in build_key_interpretation_points(properties):
        story.append(Paragraph(f"• {pt}", body_style))
        story.append(Spacer(1, 4))

    # Footer note
    story += [
        Spacer(1, 12),
        Paragraph(
            "<font size='7' color='#64748B'>ChemLab — Interactive Virtual Chemistry Laboratory | Designed by R Vishwa Janagan | © R Vishwa Janagan</font>",
            ParagraphStyle("ReportFoot", alignment=TA_CENTER)
        )
    ]

    try:
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        return pdf_bytes
    finally:
        buffer.close()
        for path in temp_images:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass

def generate_multi_molecule_pdf(student_name, reg_no, molecule_records):
    """
    Generate unified multi-page PDF laboratory report for a batch of molecules.
    Each record is a tuple: (smiles_str, mol_obj, properties_dict).
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=38, rightMargin=38, topMargin=40, bottomMargin=40
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "MultiTitle", parent=styles["Title"],
        fontSize=18, leading=22, alignment=TA_CENTER, textColor=HexColor("#0F172A")
    )
    heading_style = ParagraphStyle(
        "MultiHeading", parent=styles["Heading2"],
        fontSize=12, leading=16, textColor=HexColor("#0D9488"), spaceBefore=8, spaceAfter=6
    )
    body_style = ParagraphStyle(
        "MultiBody", parent=styles["BodyText"],
        fontSize=9, leading=13, alignment=TA_JUSTIFY, textColor=HexColor("#334155")
    )
    small_style = ParagraphStyle(
        "MultiSmall", parent=styles["Normal"],
        fontSize=7.8, leading=9.8, textColor=HexColor("#1E293B")
    )
    header_cell = ParagraphStyle(
        "MultiHeaderCell", parent=styles["Normal"],
        fontSize=8, leading=10, textColor=colors.white, alignment=TA_CENTER, fontName="Helvetica-Bold"
    )

    story = [
        Paragraph("CHEMLAB — VIRTUAL CHEMISTRY LABORATORY", title_style),
        Spacer(1, 4),
        Paragraph("MULTI-MOLECULE BATCH ANALYSIS REPORT", heading_style),
        Paragraph(f"<b>Student:</b> {student_name or 'Not specified'} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Reg No:</b> {reg_no or 'N/A'} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Molecules Evaluated:</b> {len(molecule_records)}", body_style),
        Spacer(1, 12)
    ]

    temp_images = []

    for idx, (smiles_str, mol, props) in enumerate(molecule_records, start=1):
        if idx > 1:
            story.append(PageBreak())

        story.append(Paragraph(f"Molecule {idx}: {props.get('Molecular Formula', 'Compound')} (SMILES: {smiles_str})", heading_style))

        # Basic metadata table
        basic_data = [
            ["Input SMILES", smiles_str, "Canonical", Chem.MolToSmiles(mol)],
            ["Formula", props.get("Molecular Formula", ""), "Molecular Weight", f"{props.get('Molecular Weight', '')} g/mol"]
        ]
        basic_table = Table(basic_data, colWidths=[1.5*inch, 2.2*inch, 1.4*inch, 2.1*inch])
        basic_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CBD5E1")),
            ("BACKGROUND", (0, 0), (0, -1), HexColor("#F1F5F9")),
            ("BACKGROUND", (2, 0), (2, -1), HexColor("#F1F5F9")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("PADDING", (0, 0), (-1, -1), 4)
        ]))
        story += [basic_table, Spacer(1, 8)]

        # Structure graphics
        img2d = save_2d_structure_png(mol)
        img3d = save_3d_structure_png(mol)
        if img2d: temp_images.append(img2d)
        if img3d: temp_images.append(img3d)

        if img2d and img3d:
            st_table = Table([[
                Image(img2d, width=3.1*inch, height=2.0*inch),
                Image(img3d, width=3.1*inch, height=2.0*inch)
            ]], colWidths=[3.4*inch, 3.4*inch])
            st_table.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
            ]))
            story += [st_table, Spacer(1, 8)]
        elif img2d:
            story += [Image(img2d, width=4.5*inch, height=2.8*inch), Spacer(1, 8)]

        # Descriptors table
        prop_rows = [[
            Paragraph("Descriptor", header_cell),
            Paragraph("Value", header_cell),
            Paragraph("Interpretation", header_cell)
        ]]
        for key, value in props.items():
            interp = get_property_interpretation(key, value, props)
            prop_rows.append([
                Paragraph(f"<b>{key}</b>", small_style),
                Paragraph(str(value), small_style),
                Paragraph(interp, small_style)
            ])

        prop_table = Table(prop_rows, colWidths=[1.8*inch, 1.0*inch, 4.2*inch], repeatRows=1)
        prop_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#0D9488")),
            ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#CBD5E1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), HexColor("#F8FAFC")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 3)
        ]))
        story += [prop_table, Spacer(1, 8)]

    # Final educational note page
    story.append(PageBreak())
    story.append(Paragraph("Cheminformatics Methodologies & Technologies", heading_style))
    story.append(Paragraph(
        "All calculations were executed computationally using RDKit (MolFromSmiles, Crippen LogP, Lipinski parameters, "
        "rdMolDescriptors TPSA, ETKDGv3 conformer generation, and MMFF94 force field). "
        "Reports were synthesized dynamically via ReportLab Platypus engine.",
        body_style
    ))
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "<font size='8' color='#64748B'>ChemLab — Interactive Virtual Chemistry Laboratory | Designed by R Vishwa Janagan | © R Vishwa Janagan</font>",
        ParagraphStyle("MultiFoot", alignment=TA_CENTER)
    ))

    try:
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        return pdf_bytes
    finally:
        buffer.close()
        for path in temp_images:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass
