"""
ChemLab - Core Chemistry Engine
Handles SMILES parsing, RDKit molecule representations, 2D image rendering,
3D conformer generation, and comprehensive molecular descriptor calculations.
"""

from io import BytesIO
import numpy as np
from rdkit import Chem
from rdkit.Chem import (
    Draw,
    AllChem,
    Descriptors,
    Crippen,
    Lipinski,
    rdMolDescriptors
)

EXAMPLE_MOLECULES = {
    "Ethanol": "CCO",
    "Benzene": "c1ccccc1",
    "Phenol": "Oc1ccccc1",
    "Acetic Acid": "CC(=O)O",
    "Aspirin": "CC(=O)Oc1ccccc1C(=O)O",
    "Caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
    "Methane": "C",
    "Ammonia": "N",
    "Water": "O"
}

def parse_smiles(smiles: str):
    """
    Safely parse a SMILES string into an RDKit Mol object.
    Returns (mol, error_message).
    """
    if not smiles or not smiles.strip():
        return None, "SMILES input is empty."

    cleaned_smiles = smiles.strip()
    try:
        mol = Chem.MolFromSmiles(cleaned_smiles)
        if mol is None:
            return None, f"Could not parse SMILES '{cleaned_smiles}'. Please verify the chemical syntax."
        return mol, None
    except Exception as e:
        return None, f"Parsing error: {str(e)}"

def get_canonical_smiles(mol) -> str:
    """Return canonical SMILES string."""
    if mol is None:
        return ""
    try:
        return Chem.MolToSmiles(mol, isomericSmiles=True)
    except Exception:
        return Chem.MolToSmiles(mol)

def calculate_bond_information(mol):
    """
    Calculate:
    - Heavy-atom bonds
    - Sigma (σ) bonds, including bonds to explicit/implicit hydrogens
    - Pi (π) bonds
    - Total bond components (σ + π)
    - Total atoms including hydrogens
    """
    if mol is None:
        return {
            "Heavy Atom Bonds": 0,
            "Sigma Bonds": 0,
            "Pi Bonds": 0,
            "Total Bonds": 0,
            "Total Atoms Including H": 0,
        }

    heavy_atom_bonds = mol.GetNumBonds()

    # Count pi bonds using Kekule representation for aromatic systems
    kekule_mol = Chem.Mol(mol)
    try:
        Chem.Kekulize(kekule_mol, clearAromaticFlags=True)
    except Exception:
        pass

    pi_bonds = 0.0
    for bond in kekule_mol.GetBonds():
        btype = bond.GetBondType()
        if btype == Chem.BondType.DOUBLE:
            pi_bonds += 1
        elif btype == Chem.BondType.TRIPLE:
            pi_bonds += 2
        elif btype == Chem.BondType.QUADRUPLE:
            pi_bonds += 3
        elif bond.GetIsAromatic():
            pi_bonds += 0.5

    # Each bond in molecule with explicit hydrogens represents exactly one sigma framework bond
    mol_with_h = Chem.AddHs(Chem.Mol(mol))
    sigma_bonds = mol_with_h.GetNumBonds()
    total_bonds = sigma_bonds + int(pi_bonds)

    return {
        "Heavy Atom Bonds": heavy_atom_bonds,
        "Sigma Bonds": sigma_bonds,
        "Pi Bonds": int(pi_bonds) if pi_bonds.is_integer() else pi_bonds,
        "Total Bonds": total_bonds,
        "Total Atoms Including H": mol_with_h.GetNumAtoms(),
    }

def calculate_properties(mol):
    """
    Calculate full set of molecular descriptors with scientific units and precision.
    """
    if mol is None:
        return {}

    bond_info = calculate_bond_information(mol)
    formula = rdMolDescriptors.CalcMolFormula(mol)

    try:
        mol_wt = round(Descriptors.MolWt(mol), 3)
    except Exception:
        mol_wt = None

    try:
        exact_mol_wt = round(Descriptors.ExactMolWt(mol), 4)
    except Exception:
        exact_mol_wt = None

    try:
        logp = round(Crippen.MolLogP(mol), 3)
    except Exception:
        logp = None

    try:
        tpsa = round(rdMolDescriptors.CalcTPSA(mol), 3)
    except Exception:
        tpsa = None

    try:
        fraction_csp3 = round(rdMolDescriptors.CalcFractionCSP3(mol), 3)
    except Exception:
        fraction_csp3 = 0.0

    try:
        molar_refractivity = round(Crippen.MolMR(mol), 3)
    except Exception:
        molar_refractivity = None

    return {
        "Molecular Formula": formula,
        "Molecular Weight": mol_wt,
        "Exact Molecular Weight": exact_mol_wt,
        "LogP": logp,
        "TPSA": tpsa,
        "Hydrogen Bond Donors": Lipinski.NumHDonors(mol),
        "Hydrogen Bond Acceptors": Lipinski.NumHAcceptors(mol),
        "Rotatable Bonds": Lipinski.NumRotatableBonds(mol),
        "Ring Count": Lipinski.RingCount(mol),
        "Aromatic Rings": rdMolDescriptors.CalcNumAromaticRings(mol),
        "Aliphatic Rings": rdMolDescriptors.CalcNumAliphaticRings(mol),
        "Number of Atoms": mol.GetNumAtoms(),
        "Heavy Atoms": mol.GetNumHeavyAtoms(),
        "Heavy Atom Bonds": bond_info["Heavy Atom Bonds"],
        "Sigma (σ) Bonds": bond_info["Sigma Bonds"],
        "Pi (π) Bonds": bond_info["Pi Bonds"],
        "Total Bonds (σ + π)": bond_info["Total Bonds"],
        "Total Atoms (including H)": bond_info["Total Atoms Including H"],
        "Fraction Csp3": fraction_csp3,
        "Molar Refractivity": molar_refractivity
    }

def generate_2d_image(mol, size=(700, 480)):
    """Generate high quality 2D image for RDKit Mol."""
    if mol is None:
        return None
    try:
        d2d = Draw.MolDraw2DCairo(size[0], size[1])
        opts = d2d.drawOptions()
        opts.addAtomIndices = False
        opts.bondLineWidth = 2.0
        d2d.DrawMolecule(mol)
        d2d.FinishDrawing()
        bio = BytesIO(d2d.GetDrawingText())
        from PIL import Image as PILImage
        return PILImage.open(bio)
    except Exception:
        # Fallback to standard MolToImage
        return Draw.MolToImage(mol, size=size)

def generate_3d_molecule(mol):
    """
    Generate optimized 3D coordinates using ETKDGv3 with MMFF / UFF fallbacks.
    Returns mol3d or None.
    """
    if mol is None:
        return None

    try:
        mol3d = Chem.AddHs(mol)
        
        # Primary attempt: ETKDGv3
        params = AllChem.ETKDGv3()
        params.randomSeed = 42
        params.useSmallRingTorsions = True
        status = AllChem.EmbedMolecule(mol3d, params)

        # Fallback 1: ETKDGv2 / basic embed if v3 fails
        if status != 0:
            params2 = AllChem.ETKDG()
            params2.randomSeed = 42
            status = AllChem.EmbedMolecule(mol3d, params2)

        # Fallback 2: random coordinates if distance geometry fails
        if status != 0:
            status = AllChem.EmbedMolecule(mol3d, useRandomCoords=True, randomSeed=42)

        if status != 0:
            return None

        # Energy minimization: MMFF94 first, then UFF
        try:
            if AllChem.MMFFHasAllMoleculeParams(mol3d):
                AllChem.MMFFOptimizeMolecule(mol3d, maxIters=500)
            else:
                AllChem.UFFOptimizeMolecule(mol3d, maxIters=500)
        except Exception:
            try:
                AllChem.UFFOptimizeMolecule(mol3d, maxIters=500)
            except Exception:
                pass

        return mol3d
    except Exception:
        return None

def get_element_composition(mol):
    """Return dictionary of element symbol -> count in molecule (including hydrogens)."""
    if mol is None:
        return {}
    mol_with_h = Chem.AddHs(Chem.Mol(mol))
    counts = {}
    for atom in mol_with_h.GetAtoms():
        sym = atom.GetSymbol()
        counts[sym] = counts.get(sym, 0) + 1
    return counts

def get_bond_type_distribution(mol):
    """Return counts of single, double, triple, aromatic bonds."""
    if mol is None:
        return {}
    kekule_mol = Chem.Mol(mol)
    try:
        Chem.Kekulize(kekule_mol, clearAromaticFlags=True)
    except Exception:
        pass

    counts = {"Single (C-C / C-X)": 0, "Double (=)": 0, "Triple (≡)": 0, "Aromatic": 0}
    for bond in mol.GetBonds():
        if bond.GetIsAromatic():
            counts["Aromatic"] += 1
        elif bond.GetBondType() == Chem.BondType.SINGLE:
            counts["Single (C-C / C-X)"] += 1
        elif bond.GetBondType() == Chem.BondType.DOUBLE:
            counts["Double (=)"] += 1
        elif bond.GetBondType() == Chem.BondType.TRIPLE:
            counts["Triple (≡)"] += 1
        else:
            counts["Single (C-C / C-X)"] += 1

    # Add implicit/explicit C-H and X-H single bonds
    mol_with_h = Chem.AddHs(Chem.Mol(mol))
    h_bonds = mol_with_h.GetNumBonds() - mol.GetNumBonds()
    counts["Bonds to Hydrogen (Single σ)"] = h_bonds

    return counts
