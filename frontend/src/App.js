import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  Grid,
  Button,
  Alert,
  Box,
  Divider,
  CircularProgress
} from '@mui/material';
import axios from 'axios';
import config from './config';
import MolecularViewer from './components/MolecularViewer';
import LigandInfo from './components/LigandInfo';
import DockingConfig from './components/DockingConfig';

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [proteinData, setProteinData] = useState(null);
  const [pdbContent, setPdbContent] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file size (max 10MB)
    const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB in bytes
    if (file.size > MAX_FILE_SIZE) {
      setError('File size exceeds 10MB limit');
      return;
    }

    // Validate file extension
    if (!file.name.toLowerCase().endsWith('.pdb')) {
      setError('Only .pdb files are allowed');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setPdbContent(null);
      setProteinData(null);
      
      const fileContent = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(new Error('Failed to read file'));
        reader.readAsText(file);
      });

      if (!fileContent || typeof fileContent !== 'string') {
        throw new Error('Invalid PDB file content');
      }

      setPdbContent(fileContent);
      
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(`${config.apiUrl}/api/upload-pdb`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, // 30 second timeout
        maxContentLength: MAX_FILE_SIZE,
        retry: 3,
        retryDelay: 1000,
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          console.log(`Upload Progress: ${percentCompleted}%`);
        }
      });

      if (!response.data || typeof response.data !== 'object') {
        throw new Error('Invalid server response');
      }

      setProteinData(response.data);
      setUploadedFile(file);
    } catch (err) {
      console.error('Upload error:', err);
      let errorMessage;
      
      if (err.code === 'ECONNABORTED') {
        errorMessage = 'Connection timeout. Please try again.';
      } else if (err.message === 'Network Error') {
        errorMessage = 'Network error. Please check your connection and make sure the server is running.';
      } else if (err.response) {
        // Server responded with error
        errorMessage = err.response.data?.detail || 'Server error occurred';
      } else if (err.request) {
        // Request made but no response
        errorMessage = 'No response from server. Please check if the server is running.';
      } else {
        errorMessage = err.message || 'Failed to upload PDB file';
      }
      
      setError(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
      setPdbContent(null);
      setProteinData(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ 
      minHeight: '100vh',
      backgroundColor: '#f5f5f5',
      py: 3
    }}>
      <Container maxWidth="xl">
        <Box sx={{ maxWidth: '1600px', margin: '0 auto' }}>
          <Typography variant="h4" gutterBottom sx={{ color: '#1976d2', mb: 2 }}>
            Dynamic Dock
          </Typography>
          <Divider sx={{ mb: 3 }} />

          <Grid container spacing={3}>
            {/* Left Column - Controls */}
            <Grid item xs={12} md={4}>
              {/* Upload Section */}
              <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
                <Typography variant="h6" gutterBottom color="primary">
                  Upload Protein Structure
                </Typography>
                <Button
                  variant="contained"
                  component="label"
                  fullWidth
                  disabled={loading}
                  sx={{ mb: 2 }}
                >
                  {loading ? (
                    <CircularProgress size={24} color="inherit" />
                  ) : (
                    uploadedFile?.name || 'Choose PDB File'
                  )}
                  <input
                    type="file"
                    hidden
                    accept=".pdb"
                    onChange={handleFileUpload}
                    disabled={loading}
                  />
                </Button>

                {error && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {error}
                  </Alert>
                )}
              </Paper>

              {/* Ligand Info Section */}
              {proteinData?.ligands && (
                <LigandInfo
                  ligands={proteinData.ligands || []}
                  mainLigand={proteinData.main_ligand || null}
                />
              )}

              {/* Docking Config Section */}
              {proteinData?.clean_structure_path && proteinData?.active_site_coords && (
                <DockingConfig
                  proteinPath={proteinData.clean_structure_path}
                  activesite={proteinData.active_site_coords}
                />
              )}
            </Grid>

            {/* Right Column - Viewer */}
            <Grid item xs={12} md={8}>
              <Paper 
                elevation={2} 
                sx={{ 
                  height: '600px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: '#f8f9fa',
                  position: 'relative',
                  overflow: 'hidden'
                }}
              >
                {loading ? (
                  <Box sx={{ textAlign: 'center' }}>
                    <CircularProgress />
                    <Typography sx={{ mt: 2 }}>Loading structure...</Typography>
                  </Box>
                ) : pdbContent ? (
                  <Box sx={{ width: '100%', height: '100%', position: 'absolute' }}>
                    <MolecularViewer
                      pdbData={pdbContent}
                      style={{ width: '100%', height: '100%' }}
                    />
                  </Box>
                ) : (
                  <Typography variant="h6" color="text.secondary">
                    Upload a PDB file to view the structure
                  </Typography>
                )}
              </Paper>
            </Grid>
          </Grid>
        </Box>
      </Container>
    </Box>
  );
}

export default App;
