"""
Molecular operations module for Dynamic Dock.
Handles protein structure analysis, ligand detection, and docking operations.
"""

from typing import Dict, List, Optional, Tuple
import os
import tempfile
from pathlib import Path
import numpy as np
from Bio import PDB
from Bio.PDB import PDBIO, Select
import subprocess
from rdkit import Chem
from rdkit.Chem import AllChem

class LigandSelect(Select):
    """Selector class for saving specific residues."""
    def __init__(self, residue):
        self.residue = residue

    def accept_residue(self, residue):
        return residue == self.residue

class MolecularHandler:
    def __init__(self):
        self.parser = PDB.PDBParser(QUIET=True)
        self.pdbl = PDB.PDBList()
        self.io = PDBIO()

    def fetch_structure(self, pdb_id: str) -> str:
        """Fetch a PDB structure from the PDB database."""
        pdb_path = self.pdbl.retrieve_pdb_file(
            pdb_id,
            pdir=tempfile.gettempdir(),
            file_format="pdb"
        )
        return pdb_path

    def analyze_structure(self, structure_path: str) -> Dict:
        """Analyze a PDB structure and return information about ligands and binding sites."""
        structure = self.parser.get_structure("structure", structure_path)
        ligands = self._find_ligands(structure)
        
        # Only determine active site if ligands were found
        active_site = self._determine_active_site(ligands) if ligands else {}
        
        # Create clean structure only if ligands were found
        clean_structure_path = self._remove_ligands(structure, structure_path) if ligands else structure_path
        
        print(f"Found {len(ligands)} ligands")  # Debug print
        if ligands:
            print(f"Main ligand: {ligands[0]}")  # Debug print
        
        return {
            "ligands": ligands,
            "active_site": active_site,
            "clean_structure_path": clean_structure_path
        }

    def _find_ligands(self, structure) -> List[Dict]:
        """Find ligands in the structure."""
        ligands = []
        excluded_residues = {'HOH', 'WAT', 'SOL', 'CL', 'NA', 'MG', 'CA', 'ZN'}  # Common non-ligand hetero molecules
        
        for model in structure:
            for chain in model:
                for residue in chain:
                    # Check if it's a hetero residue and not water/ions
                    if residue.id[0].strip() and residue.resname not in excluded_residues:
                        try:
                            # Get coordinates first
                            coords = self._get_centroid(residue)
                            if not coords:
                                continue
                                
                            # Try to get SMILES
                            smiles = self._get_smiles(residue)
                            if not smiles:
                                continue
                            
                            # Count non-hydrogen atoms
                            atom_count = len([atom for atom in residue if not atom.name.startswith('H')])
                            
                            if atom_count > 3:  # Only include if more than 3 non-hydrogen atoms
                                ligand_info = {
                                    "name": residue.resname,
                                    "chain": chain.id,
                                    "position": residue.id[1],
                                    "coordinates": {
                                        "x": coords[0],
                                        "y": coords[1],
                                        "z": coords[2]
                                    },
                                    "smiles": smiles,
                                    "atoms": atom_count,
                                    "residue_id": residue.id
                                }
                                ligands.append(ligand_info)
                                print(f"Found ligand: {residue.resname} with {atom_count} atoms")  # Debug print
                        except Exception as e:
                            print(f"Error processing residue {residue.resname}: {str(e)}")  # Debug print
                            continue
        
        # Sort ligands by size (number of atoms) to identify the main ligand
        ligands.sort(key=lambda x: x["atoms"], reverse=True)
        if ligands:
            ligands[0]["is_main_ligand"] = True
        
        return ligands

    def _get_centroid(self, residue) -> Optional[List[float]]:
        """Calculate the centroid of a residue."""
        coords = []
        for atom in residue:
            if not atom.name.startswith('H'):  # Exclude hydrogens
                coords.append(atom.get_coord())
        if not coords:
            return None
        return np.mean(coords, axis=0).tolist()

    def _get_smiles(self, residue) -> Optional[str]:
        """Convert a residue to SMILES format using RDKit."""
        try:
            # Create a temporary PDB file for just this residue
            temp_pdb = tempfile.mktemp(suffix='.pdb')
            self.io.set_structure(residue.get_parent().get_parent())
            self.io.save(temp_pdb, LigandSelect(residue))
            
            # Try to convert to SMILES using RDKit
            mol = Chem.MolFromPDBFile(temp_pdb, removeHs=False, sanitize=False)
            if mol is None:
                print(f"Failed to create RDKit mol for {residue.resname}")  # Debug print
                return None
                
            # Try to sanitize the molecule
            try:
                Chem.SanitizeMol(mol)
            except Exception as e:
                print(f"Failed to sanitize {residue.resname}: {str(e)}")  # Debug print
                return None
            
            smiles = Chem.MolToSmiles(mol)
            os.remove(temp_pdb)
            return smiles
            
        except Exception as e:
            print(f"Error in _get_smiles for {residue.resname}: {str(e)}")  # Debug print
            if os.path.exists(temp_pdb):
                os.remove(temp_pdb)
            return None

    def _determine_active_site(self, ligands: List[Dict]) -> Dict:
        """Determine the active site based on the main ligand position."""
        if not ligands:
            return {}
        
        # Use the largest ligand (first in the sorted list) as the main ligand
        main_ligand = ligands[0]
        print(f"Using {main_ligand['name']} as main ligand for active site")  # Debug print
        
        return {
            "x": main_ligand["coordinates"]["x"],
            "y": main_ligand["coordinates"]["y"],
            "z": main_ligand["coordinates"]["z"],
            "ligand_name": main_ligand["name"],
            "ligand_smiles": main_ligand["smiles"]
        }

    def _remove_ligands(self, structure, original_path: str) -> str:
        """Remove ligands from the structure and save a clean version."""
        clean_structure = structure.copy()
        
        # Define residues to keep (protein residues and important ions)
        protein_residues = {'GLY', 'ALA', 'VAL', 'LEU', 'ILE', 'PRO', 'PHE', 'TYR', 'TRP', 
                          'SER', 'THR', 'CYS', 'MET', 'ASN', 'GLN', 'ASP', 'GLU', 'LYS', 
                          'ARG', 'HIS'}
        important_ions = {'HOH', 'WAT', 'SOL', 'CL', 'NA', 'MG', 'CA', 'ZN', 'FE'}
        keep_residues = protein_residues.union(important_ions)
        
        # Identify residues to remove
        residues_to_remove = []
        for model in clean_structure:
            for chain in model:
                for residue in chain:
                    # Remove if it's a hetero residue (has 'H_' prefix) or not in keep_residues
                    if (residue.id[0].strip() and residue.resname not in important_ions) or \
                       (residue.resname not in keep_residues):
                        residues_to_remove.append((chain.id, residue.id))
        
        print(f"Removing {len(residues_to_remove)} ligands/non-protein residues from structure")  # Debug print
        
        # Remove the identified residues
        for chain_id, residue_id in residues_to_remove:
            try:
                chain = clean_structure[0][chain_id]
                chain.detach_child(residue_id)
                print(f"Removed residue {residue_id} from chain {chain_id}")  # Debug print
            except Exception as e:
                print(f"Error removing residue {residue_id} from chain {chain_id}: {str(e)}")  # Debug print
                continue
        
        # Save the clean structure
        clean_path = original_path.replace('.pdb', '_clean.pdb')
        self.io.set_structure(clean_structure)
        self.io.save(clean_path)
        
        print(f"Saved clean structure to {clean_path}")  # Debug print
        return clean_path

    def prepare_for_docking(self, protein_path: str, ligand_smiles: str) -> Tuple[str, str]:
        """Prepare protein and ligand for docking with AutoDock Vina."""
        try:
            # First, ensure we're using a structure without ligands
            if not protein_path.endswith('_clean.pdb'):
                # Load the structure
                structure = self.parser.get_structure("structure", protein_path)
                # Remove ligands and save clean structure
                protein_path = self._remove_ligands(structure, protein_path)
                print(f"Created clean protein structure at: {protein_path}")  # Debug print
            
            # Convert clean protein to PDBQT
            protein_pdbqt = self._convert_to_pdbqt(protein_path)
            print(f"Converted protein to PDBQT: {protein_pdbqt}")  # Debug print
            
            # Convert ligand SMILES to PDBQT
            ligand_pdbqt = self._prepare_ligand(ligand_smiles)
            print(f"Prepared ligand PDBQT: {ligand_pdbqt}")  # Debug print
            
            return protein_pdbqt, ligand_pdbqt
            
        except Exception as e:
            print(f"Error in prepare_for_docking: {str(e)}")  # Debug print
            raise RuntimeError(f"Failed to prepare structures for docking: {str(e)}")

    def _convert_to_pdbqt(self, pdb_path: str) -> str:
        """Convert PDB to PDBQT format for AutoDock Vina using OpenBabel."""
        pdbqt_path = pdb_path.replace('.pdb', '.pdbqt')
        try:
            cmd = ['obabel', pdb_path, '-O', pdbqt_path, '-xr']
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            if not os.path.exists(pdbqt_path):
                raise RuntimeError(f"Failed to create PDBQT file at {pdbqt_path}")
            return pdbqt_path
        except subprocess.CalledProcessError as e:
            print(f"Error converting to PDBQT: {e.output}")
            raise RuntimeError(f"Failed to convert {pdb_path} to PDBQT format")

    def _prepare_ligand(self, smiles: str) -> str:
        """Prepare ligand for docking from SMILES using RDKit and OpenBabel."""
        try:
            # Convert SMILES to 3D structure
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                raise RuntimeError(f"Failed to parse SMILES: {smiles}")
            
            mol = Chem.AddHs(mol)
            AllChem.EmbedMolecule(mol, randomSeed=42)
            AllChem.MMFFOptimizeMolecule(mol)
            
            # Save as PDB first
            temp_pdb = tempfile.mktemp(suffix='.pdb')
            Chem.MolToPDBFile(mol, temp_pdb)
            
            # Convert to PDBQT using OpenBabel
            temp_pdbqt = temp_pdb.replace('.pdb', '.pdbqt')
            cmd = ['obabel', temp_pdb, '-O', temp_pdbqt, '-xh']
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Clean up temporary PDB file
            os.remove(temp_pdb)
            
            if not os.path.exists(temp_pdbqt):
                raise RuntimeError(f"Failed to create PDBQT file at {temp_pdbqt}")
                
            return temp_pdbqt
            
        except Exception as e:
            print(f"Error preparing ligand: {str(e)}")
            if os.path.exists(temp_pdb):
                os.remove(temp_pdb)
            raise RuntimeError(f"Failed to prepare ligand: {str(e)}")
