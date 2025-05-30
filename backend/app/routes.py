"""
API routes for Dynamic Dock.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import tempfile
import os
import subprocess
from typing import Optional
from pydantic import BaseModel
from .molecular import MolecularHandler
from .docking import DockingHandler
from . import config

router = APIRouter()
molecular_handler = MolecularHandler()

# Use path from config
vina_path = config.VINA_PATH
if not os.path.exists(vina_path):
    raise RuntimeError(f"AutoDock Vina not found at {vina_path}")

print(f"Using Vina from: {vina_path}")  # Debug print
docking_handler = DockingHandler(vina_executable=vina_path)

class VinaSetupRequest(BaseModel):
    output_dir: str

class DockingRequest(BaseModel):
    receptor_path: str
    ligand_smiles: str
    center_x: float
    center_y: float
    center_z: float
    size_x: float
    size_y: float
    size_z: float
    output_dir: str

@router.post("/setup-vina")
async def setup_vina(request: VinaSetupRequest):
    """Set up Vina in the selected directory."""
    try:
        output_dir = os.path.join(config.RESULTS_DIR, request.output_dir)
        os.makedirs(output_dir, exist_ok=True)
        return {"success": True, "message": "Vina setup completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set up Vina: {str(e)}")

@router.get("/fetch-pdb/{pdb_id}")
async def fetch_pdb(pdb_id: str):
    """Fetch and analyze a PDB structure."""
    try:
        structure_path = molecular_handler.fetch_structure(pdb_id)
        analysis = molecular_handler.analyze_structure(structure_path)
        
        # Get the main ligand information
        main_ligand = next((l for l in analysis["ligands"] if "is_main_ligand" in l), None)
        
        return {
            "structure_id": pdb_id,
            "ligands": analysis["ligands"],
            "active_site_coords": analysis["active_site"],
            "main_ligand": main_ligand,
            "clean_structure_path": analysis["clean_structure_path"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload-pdb")
async def upload_pdb(file: UploadFile = File(...)):
    """Process an uploaded PDB file."""
    try:
        # Use the uploads directory
        temp_path = os.path.join(config.UPLOADS_DIR, file.filename)
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        analysis = molecular_handler.analyze_structure(temp_path)
        
        # Update the clean structure path to be relative
        if analysis["clean_structure_path"]:
            analysis["clean_structure_path"] = os.path.join(
                config.UPLOADS_DIR,
                os.path.basename(analysis["clean_structure_path"])
            )
        
        # Get the main ligand information
        main_ligand = next((l for l in analysis["ligands"] if "is_main_ligand" in l), None)
        
        return {
            "structure_id": "uploaded",
            "ligands": analysis["ligands"],
            "active_site_coords": analysis["active_site"],
            "main_ligand": main_ligand,
            "clean_structure_path": analysis["clean_structure_path"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/dock")
async def dock_ligand(request: DockingRequest):
    """Perform molecular docking."""
    try:
        print("Received docking request:", request.dict())  # Debug print
        
        # Use the results directory for output
        output_dir = os.path.join(config.RESULTS_DIR, request.output_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        # Update receptor path to use the uploads directory
        receptor_path = os.path.join(config.UPLOADS_DIR, os.path.basename(request.receptor_path))
        if not os.path.exists(receptor_path):
            raise HTTPException(
                status_code=400,
                detail="Clean protein structure not found. Please reload the protein."
            )
        
        # Prepare receptor and ligand
        protein_pdbqt, ligand_pdbqt = molecular_handler.prepare_for_docking(
            receptor_path, request.ligand_smiles
        )
        
        print(f"Prepared PDBQT files: Protein: {protein_pdbqt}, Ligand: {ligand_pdbqt}")  # Debug print
        
        # Prepare docking configuration
        config_path = docking_handler.prepare_docking_config(
            request.center_x, request.center_y, request.center_z,
            request.size_x, request.size_y, request.size_z
        )
        
        # Set output paths in results directory
        docking_result_pdbqt = os.path.join(output_dir, "docking_result.pdbqt")
        complex_pdb = os.path.join(output_dir, "docked_complex.pdb")
        
        # Run docking
        result = docking_handler.run_docking(
            protein_pdbqt,
            ligand_pdbqt,
            config_path,
            docking_result_pdbqt
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Docking failed: {result['error']}"
            )
        
        # Get the best binding affinity
        best_score = min(result["scores"], key=lambda x: x["affinity"]) if result["scores"] else None
        binding_affinity = best_score["affinity"] if best_score else None
        
        # Generate the complex PDB file
        complex_path = docking_handler.save_docked_complex(
            receptor_path,  # Original PDB file
            docking_result_pdbqt,  # Docked ligand
            complex_pdb  # Output path
        )
        
        if not os.path.exists(complex_pdb):
            raise HTTPException(
                status_code=500,
                detail="Failed to generate complex PDB file"
            )
        
        return {
            "success": True,
            "binding_affinity": binding_affinity,
            "poses_path": os.path.relpath(docking_result_pdbqt, config.BASE_DIR),
            "complex_path": os.path.relpath(complex_pdb, config.BASE_DIR)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{file_path:path}")
async def download_file(file_path: str):
    """Download a file."""
    try:
        # Convert relative path to absolute path within our directories
        if file_path.startswith(config.UPLOADS_DIR) or file_path.startswith(config.RESULTS_DIR):
            abs_path = file_path
        else:
            abs_path = os.path.join(config.BASE_DIR, file_path)
        
        abs_path = os.path.abspath(abs_path)
        
        # Security check: ensure file is within allowed directories
        if not (abs_path.startswith(config.UPLOADS_DIR) or 
                abs_path.startswith(config.RESULTS_DIR) or
                abs_path.startswith(config.BASE_DIR)):
            raise HTTPException(status_code=403, detail="Access denied")
            
        if not os.path.exists(abs_path):
            raise HTTPException(status_code=404, detail="File not found")
            
        # Get the file name from the path
        file_name = os.path.basename(abs_path)
        
        # Return the file as a download
        return FileResponse(
            path=abs_path,
            filename=file_name,
            media_type="application/octet-stream"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/prepare-md")
async def prepare_for_md(docked_complex_path: str):
    """Prepare a docked complex for molecular dynamics."""
    try:
        result = docking_handler.prepare_for_md(docked_complex_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
