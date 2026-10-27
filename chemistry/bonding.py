"""
ChemLab - Chemical Bonding Explorer Engine
Handles Lewis structures, bond classification, sigma/pi analysis,
hybridization models, Pauling electronegativities, dipole cancellation,
and interactive structure inspection.
"""

from rdkit import Chem

# Pauling Electronegativities
PAULING_ELECTRONEGATIVITY = {
    "H": 2.20, "B": 2.04, "C": 2.55, "N": 3.04,
    "O": 3.44, "F": 3.98, "Si": 1.90, "P": 2.19,
    "S": 2.58, "Cl": 3.16, "Br": 2.96, "I": 2.66
}

# Curated chemistry-aware Lewis structure representations and octet explanations
LEWIS_DATABASE = {
    "Water (H2O)": {
        "formula": "H₂O",
        "total_valence_electrons": 8,
        "central_atom": "Oxygen",
        "bonding_pairs": 2,
        "lone_pairs_central": 2,
        "lone_pairs_ligands": 0,
        "formal_charges": {"O": 0, "H": 0},
        "octet_status": "Complete octet on oxygen (8 electrons: 4 bonding + 4 non-bonding). Hydrogen achieves stable duet (2 electrons).",
        "ascii_diagram": (
            "    ..\n"
            "   : O :\n"
            "    / \\\n"
            "   H   H\n"
            "(Two O-H single bonds, 2 lone pairs on O)"
        ),
        "notes": "Bent geometry (~104.5°). Polar molecule with strong net dipole moment."
    },
    "Carbon Dioxide (CO2)": {
        "formula": "CO₂",
        "total_valence_electrons": 16,
        "central_atom": "Carbon",
        "bonding_pairs": 4,
        "lone_pairs_central": 0,
        "lone_pairs_ligands": 4,
        "formal_charges": {"C": 0, "O": 0},
        "octet_status": "Complete octet on all atoms. Carbon shares two double bonds (8 e⁻); each oxygen has 2 bonding pairs and 2 lone pairs (8 e⁻).",
        "ascii_diagram": (
            "  ..        ..\n"
            " : O = C = O :\n"
            "  ..        ..\n"
            "(Two C=O double bonds, two lone pairs on each O)"
        ),
        "notes": "Linear geometry (180°). Individual C=O bonds are polar, but equal and opposite vectors cancel completely (net dipole = 0)."
    },
    "Ammonia (NH3)": {
        "formula": "NH₃",
        "total_valence_electrons": 8,
        "central_atom": "Nitrogen",
        "bonding_pairs": 3,
        "lone_pairs_central": 1,
        "lone_pairs_ligands": 0,
        "formal_charges": {"N": 0, "H": 0},
        "octet_status": "Complete octet on nitrogen (6 bonding electrons from 3 N-H bonds + 2 non-bonding electrons). Duet on all hydrogens.",
        "ascii_diagram": (
            "     ..\n"
            "     N\n"
            "   / | \\\n"
            "  H  H  H\n"
            "(Three N-H single bonds, 1 lone pair on N)"
        ),
        "notes": "Trigonal pyramidal geometry (~107°). Polar molecule with lone pair contributing to net dipole."
    },
    "Methane (CH4)": {
        "formula": "CH₄",
        "total_valence_electrons": 8,
        "central_atom": "Carbon",
        "bonding_pairs": 4,
        "lone_pairs_central": 0,
        "lone_pairs_ligands": 0,
        "formal_charges": {"C": 0, "H": 0},
        "octet_status": "Complete octet on carbon (8 bonding electrons from 4 C-H single bonds). All hydrogens satisfy the duet rule.",
        "ascii_diagram": (
            "     H\n"
            "     |\n"
            " H - C - H\n"
            "     |\n"
            "     H\n"
            "(Four C-H single bonds, 0 lone pairs)"
        ),
        "notes": "Regular tetrahedral (109.5°). Symmetric nonpolar molecule; individual small C-H bond dipoles cancel completely."
    },
    "Boron Trifluoride (BF3)": {
        "formula": "BF₃",
        "total_valence_electrons": 24,
        "central_atom": "Boron",
        "bonding_pairs": 3,
        "lone_pairs_central": 0,
        "lone_pairs_ligands": 9,
        "formal_charges": {"B": 0, "F": 0},
        "octet_status": "Incomplete octet (Octet Deficient). Boron has only 6 valence electrons around it. Highly Lewis-acidic, eager to accept electron pairs.",
        "ascii_diagram": (
            "    :F: (3 lp)\n"
            "     |\n"
            "     B\n"
            "   /   \\\n"
            ":F:     :F: (each F has 3 lone pairs)"
        ),
        "notes": "Trigonal planar (120°). Classical example of an electron-deficient central atom violating the octet rule."
    },
    "Carbon Monoxide (CO)": {
        "formula": "CO",
        "total_valence_electrons": 10,
        "central_atom": "Carbon / Oxygen",
        "bonding_pairs": 3,
        "lone_pairs_central": 1,
        "lone_pairs_ligands": 1,
        "formal_charges": {"C": -1, "O": +1},
        "octet_status": "Complete octet for both atoms via a coordinate C≡O triple bond, leaving 1 lone pair on C and 1 lone pair on O.",
        "ascii_diagram": (
            " (-1)     (+1)\n"
            " : C ≡ O :\n"
            "(Triple bond: 1 coordinate bond from O to C)"
        ),
        "notes": "Significant formal charges: C has formal charge -1, O has formal charge +1, causing unusual reactivity as a ligand."
    },
    "Sulfur Hexafluoride (SF6)": {
        "formula": "SF₆",
        "total_valence_electrons": 48,
        "central_atom": "Sulfur",
        "bonding_pairs": 6,
        "lone_pairs_central": 0,
        "lone_pairs_ligands": 18,
        "formal_charges": {"S": 0, "F": 0},
        "octet_status": "Expanded octet (Hypervalent). Sulfur expands its valence shell using vacant low-lying 3d orbitals to accommodate 12 valence electrons (6 bonding pairs).",
        "ascii_diagram": (
            "    F   F\n"
            "     \\ /\n"
            "  F - S - F\n"
            "     / \\\n"
            "    F   F\n"
            "(6 S-F single bonds, 0 lp on S, 3 lp on each F)"
        ),
        "notes": "Regular octahedral (90°). Highly stable and chemically inert gas due to steric shielding and symmetric nonpolarity."
    }
}

# Guided Hybridization Models
HYBRIDIZATION_INFO = {
    "sp": {
        "name": "sp Hybridization",
        "orbital_mixing": "1 s orbital + 1 p orbital → 2 sp hybrid orbitals",
        "geometry": "Linear",
        "bond_angle": "180°",
        "unhybridized_p": "2 unhybridized p orbitals (capable of forming up to 2 π bonds)",
        "examples": "Acetylene (C₂H₂), Carbon dioxide (CO₂), Beryllium chloride (BeCl₂)",
        "overlap_description": "Frontal head-on overlap of sp hybrids forms strong σ bonds; parallel unhybridized p orbitals overlap sideways to form π bonds."
    },
    "sp2": {
        "name": "sp² Hybridization",
        "orbital_mixing": "1 s orbital + 2 p orbitals → 3 sp² hybrid orbitals",
        "geometry": "Trigonal Planar",
        "bond_angle": "120°",
        "unhybridized_p": "1 unhybridized p orbital (capable of forming 1 π bond)",
        "examples": "Ethene (C₂H₄), Benzene (C₆H₆), Boron trifluoride (BF₃), Formaldehyde (H₂CO)",
        "overlap_description": "The 3 sp² orbitals point towards vertices of an equilateral triangle at 120° forming 3 σ bonds; the remaining p orbital forms a π bond."
    },
    "sp3": {
        "name": "sp³ Hybridization",
        "orbital_mixing": "1 s orbital + 3 p orbitals → 4 sp³ hybrid orbitals",
        "geometry": "Tetrahedral",
        "bond_angle": "109.5° (ideal; modified by lone pairs)",
        "unhybridized_p": "0 unhybridized p orbitals (pure σ bonding framework or lone pairs)",
        "examples": "Methane (CH₄), Ethane (C₂H₆), Water (H₂O, bent), Ammonia (NH₃, pyramidal)",
        "overlap_description": "Four equivalent sp³ hybrid orbitals directed towards corners of a tetrahedron; overlap head-on to form strong localized σ bonds."
    }
}

# Molecular Polarity Reference and Vector Dipole Cancellation
POLARITY_EXAMPLES = [
    {
        "molecule": "Carbon Dioxide (CO2)",
        "geometry": "Linear (180°)",
        "bonds": "Two polar C=O bonds (ΔEN = 0.89)",
        "symmetry": "Center of inversion / symmetric linear",
        "dipole_moment": "0.00 D (Nonpolar)",
        "explanation": "Even though each C=O bond is strongly polar due to oxygen's higher electronegativity (3.44 vs 2.55), the two bond dipoles point in exactly opposite directions at 180° and cancel vectorially."
    },
    {
        "molecule": "Water (H2O)",
        "geometry": "Bent (~104.5°)",
        "bonds": "Two polar O-H bonds (ΔEN = 1.24)",
        "symmetry": "Asymmetric (C2v)",
        "dipole_moment": "1.85 D (Strongly Polar)",
        "explanation": "Because water is bent, the two O-H bond dipole vectors do not cancel. Instead, they reinforce each other toward the electronegative oxygen atom, augmented by the oxygen lone pairs."
    },
    {
        "molecule": "Methane (CH4)",
        "geometry": "Tetrahedral (109.5°)",
        "bonds": "Four C-H bonds (ΔEN = 0.35)",
        "symmetry": "Td regular tetrahedral",
        "dipole_moment": "0.00 D (Nonpolar)",
        "explanation": "In a regular tetrahedron, the four bond vectors cancel completely by vector symmetry. The molecule possesses zero net dipole moment."
    },
    {
        "molecule": "Ammonia (NH3)",
        "geometry": "Trigonal Pyramidal (~107°)",
        "bonds": "Three polar N-H bonds (ΔEN = 0.84)",
        "symmetry": "C3v pyramidal",
        "dipole_moment": "1.47 D (Polar)",
        "explanation": "The three N-H bond dipoles point toward the apex nitrogen atom and combine with the nitrogen lone pair, producing a substantial net dipole moment."
    }
]

def inspect_molecule_structure(mol):
    """
    Produce comprehensive atom-by-atom and bond-by-bond structural inspection data.
    """
    if mol is None:
        return {"atoms": [], "bonds": []}

    atoms_data = []
    for atom in mol.GetAtoms():
        idx = atom.GetIdx()
        symbol = atom.GetSymbol()
        en = PAULING_ELECTRONEGATIVITY.get(symbol, "N/A")
        fc = atom.GetFormalCharge()
        hybridization = str(atom.GetHybridization()).replace("UNSPECIFIED", "N/A")
        explicit_valence = atom.GetExplicitValence()
        total_h = atom.GetTotalNumHs()
        neighbors = [f"{nbr.GetSymbol()}{nbr.GetIdx()}" for nbr in atom.GetNeighbors()]
        
        atoms_data.append({
            "Index": idx,
            "Element": symbol,
            "Electronegativity (Pauling)": en,
            "Formal Charge": fc,
            "Hybridization": hybridization,
            "Valence": explicit_valence,
            "Hydrogen Count": total_h,
            "Neighbors": ", ".join(neighbors) if neighbors else "None"
        })

    bonds_data = []
    for bond in mol.GetBonds():
        b_idx = bond.GetIdx()
        a1 = bond.GetBeginAtom()
        a2 = bond.GetEndAtom()
        s1, s2 = a1.GetSymbol(), a2.GetSymbol()
        en1 = PAULING_ELECTRONEGATIVITY.get(s1, None)
        en2 = PAULING_ELECTRONEGATIVITY.get(s2, None)
        
        if en1 is not None and en2 is not None:
            delta_en = round(abs(en1 - en2), 2)
            if delta_en < 0.4:
                bond_polarity = f"Nonpolar Covalent (ΔEN={delta_en})"
            elif delta_en <= 1.7:
                bond_polarity = f"Polar Covalent (ΔEN={delta_en})"
            else:
                bond_polarity = f"Ionic Character (ΔEN={delta_en})"
        else:
            bond_polarity = "Unknown"

        btype = str(bond.GetBondType())
        b_order = bond.GetBondTypeAsDouble()
        
        # Sigma and Pi decomposition
        if bond.GetIsAromatic():
            sigma = 1
            pi = 0.5
        elif b_order == 1.0:
            sigma = 1
            pi = 0
        elif b_order == 2.0:
            sigma = 1
            pi = 1
        elif b_order == 3.0:
            sigma = 1
            pi = 2
        else:
            sigma = 1
            pi = 0

        bonds_data.append({
            "Bond Index": b_idx,
            "Connection": f"{s1}({a1.GetIdx()}) - {s2}({a2.GetIdx()})",
            "Type": btype,
            "Bond Order": b_order,
            "Sigma (σ)": sigma,
            "Pi (π)": pi,
            "Polarity Classification": bond_polarity,
            "Aromatic": "Yes" if bond.GetIsAromatic() else "No"
        })

    return {"atoms": atoms_data, "bonds": bonds_data}

BONDING_QUIZ = [
    {
        "question": "How many sigma (σ) and pi (π) bonds are in a carbon-carbon triple bond (C≡C)?",
        "options": [
            "1 sigma bond and 2 pi bonds",
            "2 sigma bonds and 1 pi bond",
            "3 sigma bonds and 0 pi bonds",
            "0 sigma bonds and 3 pi bonds"
        ],
        "answer": "1 sigma bond and 2 pi bonds",
        "explanation": "A triple bond consists of 1 direct axial head-on overlap (σ bond) and 2 mutually perpendicular lateral overlaps of unhybridized p orbitals (2 π bonds)."
    },
    {
        "question": "Why is Carbon Dioxide (CO2) a nonpolar molecule even though each C=O bond is polar?",
        "options": [
            "Carbon and oxygen have the same electronegativity",
            "The two equal and opposite C=O bond dipoles cancel out in a 180° linear geometry",
            "Double bonds cannot have a dipole moment",
            "Carbon possesses two lone pairs that neutralize the charge"
        ],
        "answer": "The two equal and opposite C=O bond dipoles cancel out in a 180° linear geometry",
        "explanation": "Molecular dipole moment is the vector sum of all individual bond dipoles. In linear CO2, the two opposite dipoles point in 180° directions and sum to zero."
    },
    {
        "question": "Which of the following molecules has an incomplete octet (electron deficient central atom)?",
        "options": ["CH4", "BF3", "H2O", "NH3"],
        "answer": "BF3",
        "explanation": "In BF3, Boron forms 3 single bonds with 0 lone pairs, giving only 6 valence electrons around boron (octet-deficient)."
    },
    {
        "question": "What is the formal charge on the oxygen atom in Carbon Monoxide (C≡O)?",
        "options": ["0", "-1", "+1", "+2"],
        "answer": "+1",
        "explanation": "Valence electrons of O = 6. In C≡O, O has 1 lone pair (2 electrons) and shares 3 bonds (3 electrons), so Formal Charge = 6 - (2 + 3) = +1. Carbon has formal charge 4 - (2 + 3) = -1."
    },
    {
        "question": "Which hybridization is associated with a planar carbon center having 120° bond angles (e.g. in ethene)?",
        "options": ["sp", "sp²", "sp³", "sp³d"],
        "answer": "sp²",
        "explanation": "sp² hybridization mixes one s and two p orbitals into three planar hybrid orbitals at 120° angles, leaving one unhybridized p orbital for π bonding."
    }
]
