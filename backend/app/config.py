import os
import tempfile
import platform

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADS_DIR = os.path.join(tempfile.gettempdir(), 'dynamic_dock_uploads')
RESULTS_DIR = os.path.join(tempfile.gettempdir(), 'dynamic_dock_results')

# Create directories if they don't exist
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Vina path based on platform
system = platform.system().lower()
if system == 'darwin':  # macOS
    VINA_PATH = os.path.join(BASE_DIR, 'bin', 'mac', 'vina')
elif system == 'linux':
    VINA_PATH = os.path.join(BASE_DIR, 'bin', 'linux', 'vina')
else:
    raise RuntimeError(f"Unsupported platform: {system}")

# Ensure Vina exists and is executable
if os.path.exists(VINA_PATH):
    os.chmod(VINA_PATH, 0o755)  # Make executable
