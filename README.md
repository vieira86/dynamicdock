# Dynamic Dock

A molecular docking platform that enables protein-ligand docking analysis and molecular dynamics preparation.

## Features

- PDB structure loading (via PDB ID or file upload)
- Co-crystallized ligand analysis and visualization
- Active site identification
- Molecular docking using AutoDock Vina
- Results download and molecular dynamics preparation

## Project Structure

```
dynamic_dock/
├── frontend/           # React frontend application
├── backend/           # Python FastAPI backend
├── docker/            # Docker configuration files
└── README.md         # This file
```

## Prerequisites

- Node.js 16+
- Python 3.8+
- Docker (optional)
- AutoDock Vina
- RDKit
- OpenBabel

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Start the backend server:
```bash
poetry run uvicorn app.main:app --reload
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will be available at http://localhost:3000

## License

MIT
