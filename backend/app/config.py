import os
import tempfile

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADS_DIR = os.path.join(tempfile.gettempdir(), 'dynamic_dock_uploads')
RESULTS_DIR = os.path.join(tempfile.gettempdir(), 'dynamic_dock_results')

# Create directories if they don't exist
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Vina path
VINA_DIR = os.path.join(BASE_DIR, '..', 'vina')
VINA_PATH = os.path.join(VINA_DIR, 'vina')
