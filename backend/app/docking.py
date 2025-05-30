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

    def save_docked_complex(self, receptor_path, docked_ligand_path, output_path):
        """
        Generate a PDB file containing both the receptor and the best docked pose.
        """
        try:
            # Read the receptor PDB file
            with open(receptor_path, 'r') as f:
                receptor_lines = f.readlines()

            # Read the docked ligand PDBQT file (we'll only use the first/best pose)
            with open(docked_ligand_path, 'r') as f:
                ligand_lines = []
                reading_model = False
                for line in f:
                    if line.startswith('MODEL 1'):
                        reading_model = True
                        continue
                    elif line.startswith('MODEL ') or line.startswith('ENDMDL'):
                        reading_model = False
                        continue
                    elif reading_model and line.startswith('ATOM'):
                        # Convert PDBQT atom lines to PDB format
                        # Remove charge columns and keep only essential PDB fields
                        pdb_line = line[:66] + '  1.00  0.00           ' + line[77:78] + '\n'
                        ligand_lines.append(pdb_line)

            # Write the combined PDB file
            with open(output_path, 'w') as f:
                # Write receptor atoms
                for line in receptor_lines:
                    if not line.startswith('END'):
                        f.write(line)
                
                # Write ligand atoms
                f.write('TER\n')  # Terminate receptor chain
                for line in ligand_lines:
                    f.write(line)
                f.write('END\n')

            return output_path

        except Exception as e:
            print(f"Error generating complex PDB: {str(e)}")
            return None

    def prepare_for_md(self, docked_complex_path: str) -> Dict:
        """
        Prepare docked complex for molecular dynamics simulation.
        This is a placeholder for future implementation.
        """
        return {
            "status": "not_implemented",
            "message": "MD preparation will be implemented in future versions"
        }
