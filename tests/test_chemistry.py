"""
Unit tests for ChemLab chemistry engine, geometry calculations,
bonding explorer, and PDF reporting.
"""

import unittest
from chemistry.core import (
    parse_smiles,
    get_canonical_smiles,
    calculate_bond_information,
    calculate_properties,
    generate_3d_molecule,
    get_element_composition,
    get_bond_type_distribution
)
from chemistry.geometry import (
    VSEPR_DATABASE,
    TETRAHEDRAL_SERIES,
    calculate_conformer_angles
)
from chemistry.bonding import (
    LEWIS_DATABASE,
    inspect_molecule_structure
)
from chemistry.reporting import generate_molecule_pdf, generate_multi_molecule_pdf

class TestChemLabCore(unittest.TestCase):

    def test_smiles_parsing_valid(self):
        mol, err = parse_smiles("CCO")
        self.assertIsNotNone(mol)
        self.assertIsNone(err)
        self.assertEqual(get_canonical_smiles(mol), "CCO")

    def test_smiles_parsing_invalid(self):
        mol, err = parse_smiles("Invalid_Smiles_123!!")
        self.assertIsNone(mol)
        self.assertIsNotNone(err)

    def test_empty_smiles(self):
        mol, err = parse_smiles("")
        self.assertIsNone(mol)
        self.assertIn("empty", err.lower())

    def test_bond_information_ethanol(self):
        mol, _ = parse_smiles("CCO")
        info = calculate_bond_information(mol)
        self.assertEqual(info["Heavy Atom Bonds"], 2)
        self.assertEqual(info["Sigma Bonds"], 8)
        self.assertEqual(info["Pi Bonds"], 0)
        self.assertEqual(info["Total Bonds"], 8)
        self.assertEqual(info["Total Atoms Including H"], 9)

    def test_bond_information_benzene(self):
        mol, _ = parse_smiles("c1ccccc1")
        info = calculate_bond_information(mol)
        self.assertEqual(info["Sigma Bonds"], 12)
        self.assertEqual(info["Pi Bonds"], 3)
        self.assertEqual(info["Total Bonds"], 15)
        self.assertEqual(info["Total Atoms Including H"], 12)

    def test_bond_information_co2(self):
        mol, _ = parse_smiles("O=C=O")
        info = calculate_bond_information(mol)
        self.assertEqual(info["Sigma Bonds"], 2)
        self.assertEqual(info["Pi Bonds"], 2)
        self.assertEqual(info["Total Bonds"], 4)

    def test_properties_calculation(self):
        mol, _ = parse_smiles("CCO")
        props = calculate_properties(mol)
        self.assertEqual(props["Molecular Formula"], "C2H6O")
        self.assertAlmostEqual(props["Molecular Weight"], 46.069, places=1)
        self.assertEqual(props["Hydrogen Bond Donors"], 1)
        self.assertEqual(props["Hydrogen Bond Acceptors"], 1)

    def test_3d_conformer_generation(self):
        mol, _ = parse_smiles("CCO")
        mol3d = generate_3d_molecule(mol)
        self.assertIsNotNone(mol3d)
        self.assertGreater(mol3d.GetNumConformers(), 0)

    def test_element_composition(self):
        mol, _ = parse_smiles("CCO")
        counts = get_element_composition(mol)
        self.assertEqual(counts.get("C"), 2)
        self.assertEqual(counts.get("H"), 6)
        self.assertEqual(counts.get("O"), 1)

    def test_vsepr_database_completeness(self):
        required = [
            "Carbon Dioxide (CO2)",
            "Boron Trifluoride (BF3)",
            "Methane (CH4)",
            "Ammonia (NH3)",
            "Water (H2O)",
            "Ethene (C2H4)",
            "Ethyne (C2H2)"
        ]
        for name in required:
            self.assertIn(name, VSEPR_DATABASE)
            entry = VSEPR_DATABASE[name]
            self.assertIn("electron_domain_geometry", entry)
            self.assertIn("molecular_geometry", entry)
            self.assertIn("ideal_angle_deg", entry)
            self.assertIn("hybridization", entry)

    def test_lewis_database_completeness(self):
        self.assertIn("Water (H2O)", LEWIS_DATABASE)
        self.assertIn("Carbon Dioxide (CO2)", LEWIS_DATABASE)
        self.assertIn("Boron Trifluoride (BF3)", LEWIS_DATABASE)
        self.assertIn("Carbon Monoxide (CO)", LEWIS_DATABASE)
        self.assertIn("Sulfur Hexafluoride (SF6)", LEWIS_DATABASE)

    def test_structure_inspection(self):
        mol, _ = parse_smiles("CC(=O)O")
        insp = inspect_molecule_structure(mol)
        self.assertEqual(len(insp["atoms"]), 4)
        self.assertGreater(len(insp["bonds"]), 0)

    def test_pdf_report_generation(self):
        mol, _ = parse_smiles("CCO")
        props = calculate_properties(mol)
        pdf_bytes = generate_molecule_pdf("CCO", mol, props, student_name="Test Student", reg_no="REG123")
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 1000)

    def test_multi_pdf_report_generation(self):
        m1, _ = parse_smiles("CCO")
        p1 = calculate_properties(m1)
        m2, _ = parse_smiles("c1ccccc1")
        p2 = calculate_properties(m2)
        records = [("CCO", m1, p1), ("c1ccccc1", m2, p2)]
        pdf_bytes = generate_multi_molecule_pdf("Test Student", "REG123", records)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 2000)

if __name__ == "__main__":
    unittest.main()
