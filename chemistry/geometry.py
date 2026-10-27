"""
ChemLab - Molecular Geometry & VSEPR Engine
Contains VSEPR data, electron-domain and molecular geometry analysis,
conformer bond angle calculation, comparative repulsion models, and interactive quiz bank.
"""

import math
import numpy as np
from rdkit import Chem
from rdkit.Chem import rdMolTransforms

# Comprehensive VSEPR curated reference database for core and extended molecules
VSEPR_DATABASE = {
    "Carbon Dioxide (CO2)": {
        "smiles": "O=C=O",
        "central_atom": "Carbon (C)",
        "bonding_domains": 2,
        "lone_pairs": 0,
        "total_domains": 2,
        "steric_number": 2,
        "electron_domain_geometry": "Linear",
        "molecular_geometry": "Linear",
        "ideal_angle_deg": 180.0,
        "experimental_angle_deg": 180.0,
        "hybridization": "sp",
        "explanation": (
            "The central carbon atom has 2 double bonds to oxygen atoms (2 electron domains) "
            "and no non-bonding lone pairs. According to VSEPR theory, two electron domains "
            "repel each other to maximize separation, adopting a linear arrangement with a 180° bond angle."
        ),
        "vsepr_formula": "AX₂",
        "angle_labels": ["O=C=O"]
    },
    "Boron Trifluoride (BF3)": {
        "smiles": "FB(F)F",
        "central_atom": "Boron (B)",
        "bonding_domains": 3,
        "lone_pairs": 0,
        "total_domains": 3,
        "steric_number": 3,
        "electron_domain_geometry": "Trigonal Planar",
        "molecular_geometry": "Trigonal Planar",
        "ideal_angle_deg": 120.0,
        "experimental_angle_deg": 120.0,
        "hybridization": "sp²",
        "explanation": (
            "Boron forms 3 single bonds with fluorine atoms with 0 lone pairs on the central boron atom. "
            "The three equivalent bonding domains arrange themselves symmetrically in a single plane "
            "at 120° angles to minimize electrostatic repulsion. Note that BF₃ is electron-deficient (incomplete octet, 6 valence electrons)."
        ),
        "vsepr_formula": "AX₃",
        "angle_labels": ["F-B-F"]
    },
    "Methane (CH4)": {
        "smiles": "C",
        "central_atom": "Carbon (C)",
        "bonding_domains": 4,
        "lone_pairs": 0,
        "total_domains": 4,
        "steric_number": 4,
        "electron_domain_geometry": "Tetrahedral",
        "molecular_geometry": "Tetrahedral",
        "ideal_angle_deg": 109.5,
        "experimental_angle_deg": 109.5,
        "hybridization": "sp³",
        "explanation": (
            "The central carbon atom forms 4 equivalent C-H single bonds directed toward the four vertices "
            "of a regular tetrahedron with 0 non-bonding lone pairs. Because all four domains are identical bonding pairs, "
            "all H-C-H bond angles are precisely 109.5°."
        ),
        "vsepr_formula": "AX₄",
        "angle_labels": ["H-C-H"]
    },
    "Ammonia (NH3)": {
        "smiles": "N",
        "central_atom": "Nitrogen (N)",
        "bonding_domains": 3,
        "lone_pairs": 1,
        "total_domains": 4,
        "steric_number": 4,
        "electron_domain_geometry": "Tetrahedral",
        "molecular_geometry": "Trigonal Pyramidal",
        "ideal_angle_deg": 109.5,
        "experimental_angle_deg": 107.0,
        "hybridization": "sp³",
        "explanation": (
            "Nitrogen has 4 electron domains (3 N-H bonding pairs + 1 non-bonding lone pair). "
            "While the electron-domain geometry is tetrahedral, the lone pair occupies more spatial volume "
            "and exerts stronger electrostatic repulsion (Lone Pair–Bonding Pair > Bonding Pair–Bonding Pair). "
            "This compresses the H-N-H bond angles from the ideal 109.5° down to approximately 107.0°."
        ),
        "vsepr_formula": "AX₃E",
        "angle_labels": ["H-N-H"]
    },
    "Water (H2O)": {
        "smiles": "O",
        "central_atom": "Oxygen (O)",
        "bonding_domains": 2,
        "lone_pairs": 2,
        "total_domains": 4,
        "steric_number": 4,
        "electron_domain_geometry": "Tetrahedral",
        "molecular_geometry": "Bent",
        "ideal_angle_deg": 109.5,
        "experimental_angle_deg": 104.5,
        "hybridization": "sp³",
        "explanation": (
            "Oxygen possesses 4 electron domains: 2 O-H bonding pairs and 2 lone pairs. "
            "Strong lone pair–lone pair repulsion followed by lone pair–bonding pair repulsion pushes the "
            "bonding pairs significantly closer together, reducing the H-O-H bond angle to approximately 104.5°."
        ),
        "vsepr_formula": "AX₂E₂",
        "angle_labels": ["H-O-H"]
    },
    "Ethene (C2H4)": {
        "smiles": "C=C",
        "central_atom": "Each Carbon (C)",
        "bonding_domains": 3,
        "lone_pairs": 0,
        "total_domains": 3,
        "steric_number": 3,
        "electron_domain_geometry": "Trigonal Planar",
        "molecular_geometry": "Trigonal Planar (around each carbon)",
        "ideal_angle_deg": 120.0,
        "experimental_angle_deg": 121.3,
        "hybridization": "sp²",
        "explanation": (
            "Each carbon is bonded to 2 hydrogen atoms and double-bonded to the adjacent carbon atom, "
            "constituting 3 electron domains per carbon with 0 lone pairs. Both carbon centres are planar, "
            "giving a completely flat molecular structure with C=C-H angles of ~121.3° and H-C-H angle of ~117.4°."
        ),
        "vsepr_formula": "AX₃ (per C)",
        "angle_labels": ["C=C-H (~121.3°)", "H-C-H (~117.4°)"]
    },
    "Ethyne (C2H2)": {
        "smiles": "C#C",
        "central_atom": "Each Carbon (C)",
        "bonding_domains": 2,
        "lone_pairs": 0,
        "total_domains": 2,
        "steric_number": 2,
        "electron_domain_geometry": "Linear",
        "molecular_geometry": "Linear (around each carbon)",
        "ideal_angle_deg": 180.0,
        "experimental_angle_deg": 180.0,
        "hybridization": "sp",
        "explanation": (
            "Each carbon atom forms a single σ bond to a hydrogen and a triple bond (1 σ + 2 π bonds) to the "
            "partner carbon atom. With 2 electron domains and 0 lone pairs per carbon, the geometry around each carbon is linear (180°)."
        ),
        "vsepr_formula": "AX₂ (per C)",
        "angle_labels": ["H-C≡C"]
    },
    "Sulfur Tetrafluoride (SF4)": {
        "smiles": "FS(F)(F)F",
        "central_atom": "Sulfur (S)",
        "bonding_domains": 4,
        "lone_pairs": 1,
        "total_domains": 5,
        "steric_number": 5,
        "electron_domain_geometry": "Trigonal Bipyramidal",
        "molecular_geometry": "Seesaw",
        "ideal_angle_deg": 120.0,
        "experimental_angle_deg": 101.6,
        "hybridization": "sp³d (expanded octet)",
        "explanation": (
            "Sulfur has 5 electron domains (4 S-F bonds + 1 lone pair). The lone pair occupies an equatorial position "
            "to minimize 90° repulsions, leading to a distorted 'seesaw' molecular geometry. Axial F-S-F angle is ~173° and equatorial is ~102°."
        ),
        "vsepr_formula": "AX₄E",
        "angle_labels": ["F_eq-S-F_eq (~102°)", "F_ax-S-F_ax (~173°)"]
    },
    "Chlorine Trifluoride (ClF3)": {
        "smiles": "FCl(F)F",
        "central_atom": "Chlorine (Cl)",
        "bonding_domains": 3,
        "lone_pairs": 2,
        "total_domains": 5,
        "steric_number": 5,
        "electron_domain_geometry": "Trigonal Bipyramidal",
        "molecular_geometry": "T-shaped",
        "ideal_angle_deg": 90.0,
        "experimental_angle_deg": 87.5,
        "hybridization": "sp³d (expanded octet)",
        "explanation": (
            "Chlorine has 5 electron domains: 3 Cl-F bonds and 2 equatorial lone pairs. "
            "Because both lone pairs reside in the equatorial plane, the bonded atoms form an asymmetric T-shape with angles slightly bent to ~87.5°."
        ),
        "vsepr_formula": "AX₃E₂",
        "angle_labels": ["F_ax-Cl-F_eq (~87.5°)"]
    },
    "Phosphorus Pentachloride (PCl5)": {
        "smiles": "ClP(Cl)(Cl)(Cl)Cl",
        "central_atom": "Phosphorus (P)",
        "bonding_domains": 5,
        "lone_pairs": 0,
        "total_domains": 5,
        "steric_number": 5,
        "electron_domain_geometry": "Trigonal Bipyramidal",
        "molecular_geometry": "Trigonal Bipyramidal",
        "ideal_angle_deg": 120.0,
        "experimental_angle_deg": 120.0,
        "hybridization": "sp³d (expanded octet)",
        "explanation": (
            "Phosphorus expands its valence shell to 10 electrons forming 5 P-Cl bonds with 0 lone pairs. "
            "Three equatorial bonds lie at 120° in a plane, while two axial bonds sit perpendicular at 90°."
        ),
        "vsepr_formula": "AX₅",
        "angle_labels": ["Cl_eq-P-Cl_eq (120°)", "Cl_ax-P-Cl_eq (90°)"]
    },
    "Sulfur Hexafluoride (SF6)": {
        "smiles": "FS(F)(F)(F)(F)F",
        "central_atom": "Sulfur (S)",
        "bonding_domains": 6,
        "lone_pairs": 0,
        "total_domains": 6,
        "steric_number": 6,
        "electron_domain_geometry": "Octahedral",
        "molecular_geometry": "Octahedral",
        "ideal_angle_deg": 90.0,
        "experimental_angle_deg": 90.0,
        "hybridization": "sp³d² (expanded octet)",
        "explanation": (
            "Sulfur is bonded to 6 fluorine atoms with 0 lone pairs. All 6 positions are geometrically equivalent, "
            "forming a highly symmetric regular octahedron with all adjacent F-S-F angles at 90°."
        ),
        "vsepr_formula": "AX₆",
        "angle_labels": ["F-S-F (90°)"]
    }
}

# The classic tetrahedral series demonstrating lone-pair repulsion
TETRAHEDRAL_SERIES = [
    {
        "name": "Methane (CH4)",
        "formula": "CH₄",
        "smiles": "C",
        "domains": 4,
        "bonding": 4,
        "lone_pairs": 0,
        "geometry": "Tetrahedral",
        "ideal_angle": 109.5,
        "actual_angle": 109.5,
        "repulsion_note": "No lone pairs; four equivalent bonding pairs maintain perfect tetrahedral symmetry."
    },
    {
        "name": "Ammonia (NH3)",
        "formula": "NH₃",
        "smiles": "N",
        "domains": 4,
        "bonding": 3,
        "lone_pairs": 1,
        "geometry": "Trigonal Pyramidal",
        "ideal_angle": 109.5,
        "actual_angle": 107.0,
        "repulsion_note": "1 lone pair repels bonding pairs more strongly, reducing the angle by ~2.5°."
    },
    {
        "name": "Water (H2O)",
        "formula": "H₂O",
        "smiles": "O",
        "domains": 4,
        "bonding": 2,
        "lone_pairs": 2,
        "geometry": "Bent",
        "ideal_angle": 109.5,
        "actual_angle": 104.5,
        "repulsion_note": "2 lone pairs exert strong lone pair–lone pair repulsion, compressing the angle by ~5.0°."
    }
]

def calculate_conformer_angles(mol3d):
    """
    Calculate real geometric bond angles (in degrees) from the generated 3D conformer coordinates.
    Returns list of dicts: {'atoms': (idx1, central_idx, idx2), 'symbols': (s1, sc, s2), 'angle': float}
    """
    if mol3d is None or mol3d.GetNumConformers() == 0:
        return []

    conf = mol3d.GetConformer()
    angles = []
    
    for atom in mol3d.GetAtoms():
        neighbors = atom.GetNeighbors()
        if len(neighbors) < 2:
            continue
        c_idx = atom.GetIdx()
        c_sym = atom.GetSymbol()
        
        # Calculate angles between all pairs of neighbors
        for i in range(len(neighbors)):
            for j in range(i + 1, len(neighbors)):
                idx1 = neighbors[i].GetIdx()
                idx2 = neighbors[j].GetIdx()
                s1 = neighbors[i].GetSymbol()
                s2 = neighbors[j].GetSymbol()
                
                try:
                    deg = rdMolTransforms.GetAngleDeg(conf, idx1, c_idx, idx2)
                    angles.append({
                        "central_index": c_idx,
                        "central_symbol": c_sym,
                        "label": f"{s1}({idx1}) - {c_sym}({c_idx}) - {s2}({idx2})",
                        "angle_deg": round(deg, 1)
                    })
                except Exception:
                    pass

    return angles

# Interactive VSEPR Quiz Questions
GEOMETRY_QUIZ = [
    {
        "question": "What is the molecular geometry of Carbon Dioxide (CO2)?",
        "options": ["Bent", "Linear", "Tetrahedral", "Trigonal Planar"],
        "answer": "Linear",
        "explanation": "CO2 has 2 electron domains (two C=O double bonds) and 0 lone pairs on carbon. These 2 domains repel to opposite sides, giving a 180° linear geometry."
    },
    {
        "question": "What is the electron-domain geometry of Water (H2O)?",
        "options": ["Bent", "Tetrahedral", "Linear", "Trigonal Pyramidal"],
        "answer": "Tetrahedral",
        "explanation": "H2O has 4 total electron domains (2 single bonds + 2 lone pairs on oxygen). Therefore its electron-domain geometry is tetrahedral, while its molecular geometry is bent."
    },
    {
        "question": "Why is the bond angle in NH3 (~107°) smaller than the ideal tetrahedral angle (109.5°)?",
        "options": [
            "Lone pairs are less electronegative",
            "Lone-pair electrons occupy more space and exert stronger repulsion than bonding pairs",
            "Hydrogen atoms attract each other",
            "Nitrogen does not use hybrid orbitals"
        ],
        "answer": "Lone-pair electrons occupy more space and exert stronger repulsion than bonding pairs",
        "explanation": "VSEPR repulsion order is: Lone Pair–Lone Pair > Lone Pair–Bonding Pair > Bonding Pair–Bonding Pair. The lone pair pushes the three N-H bonds closer together."
    },
    {
        "question": "What is the conventional hybridization model assigned to the boron atom in BF3?",
        "options": ["sp", "sp²", "sp³", "sp³d"],
        "answer": "sp²",
        "explanation": "Boron has 3 electron domains and trigonal planar geometry, which in introductory valence-bond theory corresponds to mixing one 2s and two 2p orbitals to form three sp² hybrids."
    },
    {
        "question": "What is the molecular geometry of Sulfur Hexafluoride (SF6)?",
        "options": ["Trigonal Bipyramidal", "Octahedral", "Square Planar", "Tetrahedral"],
        "answer": "Octahedral",
        "explanation": "SF6 features 6 bonding pairs and 0 lone pairs on sulfur, yielding a regular octahedral molecular geometry with 90° bond angles."
    }
]
