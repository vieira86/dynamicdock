"""
Docking operations module for Dynamic Dock.
Handles AutoDock Vina docking operations and result processing.
"""

import os
import tempfile
import subprocess
from typing import Dict, List, Optional
import json
from pathlib import Path

class DockingHandler:
    def __init__(self, vina_executable: str = "vina"):
        self.vina_executable = vina_executable
        self.temp_dir = tempfile.mkdtemp(prefix='docking_')

    def prepare_docking_config(
        self,
        center_x: float,
        center_y: float,
        center_z: float,
        size_x: float = 20.0,
        size_y: float = 20.0,
        size_z: float = 20.0,
        exhaustiveness: int = 8,
        num_modes: int = 9
    ) -> str:
        """
        Prepare AutoDock Vina configuration file.
        """
        config_path = os.path.join(self.temp_dir, "config.txt")
        
        config = {
            "center_x": center_x,
            "center_y": center_y,
            "center_z": center_z,
            "size_x": size_x,
            "size_y": size_y,
            "size_z": size_z,
            "exhaustiveness": exhaustiveness,
            "num_modes": num_modes
        }
        
        with open(config_path, 'w') as f:
            for key, value in config.items():
                f.write(f"{key} = {value}\n")
        
        return config_path

    def run_docking(
        self,
        receptor_path: str,
        ligand_path: str,
        config_path: str,
        output_path: Optional[str] = None
    ) -> Dict:
        """
        Run molecular docking using AutoDock Vina.
        """
        if output_path is None:
            output_path = os.path.join(self.temp_dir, "output.pdbqt")

        try:
            cmd = [
                self.vina_executable,
                "--receptor", receptor_path,
                "--ligand", ligand_path,
                "--config", config_path,
                "--out", output_path
            ]
            
            print("Running command:", " ".join(cmd))  # Debug print
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                return {
                    "success": False,
                    "error": f"Vina error: {stderr}"
                }
            
            # Parse scores from stdout
            scores = []
            reading_scores = False
            
            for line in stdout.split('\n'):
                # Start reading scores after this marker
                if "-----+------------+----------+----------" in line:
                    reading_scores = True
                    continue
                
                # Stop reading when we hit an empty line after scores
                if reading_scores and not line.strip():
                    break
                
                # Parse score lines
                if reading_scores and line.strip():
                    try:
                        parts = line.split()
                        if len(parts) >= 4:  # mode, affinity, rmsd l.b., rmsd u.b.
                            scores.append({
                                "mode": int(parts[0]),
                                "affinity": float(parts[1]),
                                "rmsd_lb": float(parts[2]),
                                "rmsd_ub": float(parts[3])
                            })
                    except (IndexError, ValueError) as e:
                        print(f"Error parsing line: {line}, Error: {str(e)}")
                        continue
            
            print(f"Parsed {len(scores)} binding modes")  # Debug print
            for score in scores:
                print(f"Mode {score['mode']}: {score['affinity']} kcal/mol")  # Debug print
            
            return {
                "success": True,
                "scores": scores,
                "output_path": output_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def save_docked_complex(self, receptor_path: str, docked_ligand_path: str, output_path: str = None) -> str:
        """
        Convert docked ligand from PDBQT to PDB and combine with receptor.
        """
        try:
            if output_path is None:
                output_path = os.path.join(self.temp_dir, "docked_complex.pdb")
                
            # Convert receptor to PDB if it's PDBQT
            receptor_pdb = receptor_path
            if receptor_path.endswith('.pdbqt'):
                receptor_pdb = receptor_path.replace('.pdbqt', '.pdb')
                cmd = ['obabel', receptor_path, '-O', receptor_pdb]
                subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Convert docked ligand to PDB
            ligand_pdb = docked_ligand_path.replace('.pdbqt', '_ligand.pdb')
            cmd = ['obabel', docked_ligand_path, '-O', ligand_pdb]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Combine receptor and ligand into a single PDB file
            with open(output_path, 'w') as outfile:
                # Write receptor
                with open(receptor_pdb, 'r') as f:
                    for line in f:
                        if not line.startswith('END'):  # Skip END card from receptor
                            outfile.write(line)
                
                # Write ligand
                with open(ligand_pdb, 'r') as f:
                    outfile.write('\n')  # Add a blank line between structures
                    for line in f:
                        outfile.write(line)
            
            # Clean up temporary files
            if receptor_path.endswith('.pdbqt') and os.path.exists(receptor_pdb):
                os.remove(receptor_pdb)
            if os.path.exists(ligand_pdb):
                os.remove(ligand_pdb)
                
            return output_path
            
        except Exception as e:
            print(f"Error saving docked complex: {str(e)}")
            raise RuntimeError(f"Failed to save docked complex: {str(e)}")

    def prepare_for_md(self, docked_complex_path: str) -> Dict:
        """
        Prepare docked complex for molecular dynamics simulation.
        This is a placeholder for future implementation.
        """
        return {
            "status": "not_implemented",
            "message": "MD preparation will be implemented in future versions"
        }
