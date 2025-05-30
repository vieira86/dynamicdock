import React, { useState } from 'react';
import {
  Paper,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Typography,
  Grid,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import axios from 'axios';
import config from '../config';

const DockingConfig = ({ proteinPath, activesite }) => {
  const [ligandSmiles, setLigandSmiles] = useState('');
  const [boxSize, setBoxSize] = useState({ x: 20, y: 20, z: 20 });
  const [outputDir] = useState('/Users/rafaelvieira/Desktop/Dynamic_Dock/vina');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);

  const formatErrorMessage = (error) => {
    if (typeof error === 'string') return error;
    if (error?.response?.data?.detail) {
      const detail = error.response.data.detail;
      if (typeof detail === 'string') return detail;
      if (Array.isArray(detail)) {
        return detail.map(err => err.msg || String(err)).join('. ');
      }
      if (typeof detail === 'object') {
        return detail.msg || JSON.stringify(detail);
      }
    }
    return error?.message || 'An error occurred during docking';
  };

  const handleDocking = async () => {
    try {
      setLoading(true);
      setError('');
      setResults(null);

      const dockingData = {
        receptor_path: proteinPath,
        ligand_smiles: ligandSmiles,
        center_x: activesite.x,
        center_y: activesite.y,
        center_z: activesite.z,
        size_x: boxSize.x,
        size_y: boxSize.y,
        size_z: boxSize.z,
        output_dir: outputDir
      };

      console.log('Sending docking request:', dockingData);

      const response = await axios.post(`${config.apiUrl}/api/dock`, dockingData);

      if (!response.data) {
        throw new Error('Empty response from server');
      }

      const { binding_affinity, poses_path, complex_path } = response.data;
      
      setResults({
        binding_affinity: typeof binding_affinity === 'number' ? binding_affinity : null,
        poses_path: typeof poses_path === 'string' ? poses_path : null,
        complex_path: typeof complex_path === 'string' ? complex_path : null
      });

    } catch (err) {
      console.error('Docking error:', err);
      setError(formatErrorMessage(err));
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom color="primary">
        Dock New Ligand
      </Typography>

      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Typography variant="body2" color="textSecondary" gutterBottom>
            Using AutoDock Vina from: {outputDir}
          </Typography>
        </Grid>

        {activesite && (
          <Grid item xs={12}>
            <TableContainer component={Paper} variant="outlined" sx={{ mb: 3 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell colSpan={2}>
                      <Typography variant="subtitle2" color="primary">
                        Active Site Location
                      </Typography>
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell component="th" sx={{ width: '40%' }}>X Coordinate</TableCell>
                    <TableCell>{activesite.x.toFixed(2)} Å</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell component="th">Y Coordinate</TableCell>
                    <TableCell>{activesite.y.toFixed(2)} Å</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell component="th">Z Coordinate</TableCell>
                    <TableCell>{activesite.z.toFixed(2)} Å</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>
        )}

        <Grid item xs={12}>
          <TextField
            fullWidth
            multiline
            rows={2}
            label="Ligand SMILES"
            value={ligandSmiles}
            onChange={(e) => setLigandSmiles(e.target.value)}
            disabled={loading}
            placeholder="Enter SMILES string of the ligand to dock"
            helperText="Example: CC(=O)OC1=CC=CC=C1C(=O)O for Aspirin"
          />
        </Grid>

        <Grid item xs={12}>
          <Typography variant="subtitle2" gutterBottom>
            Search Box Size
          </Typography>
        </Grid>
        <Grid item xs={4}>
          <TextField
            fullWidth
            type="number"
            label="Size X (Å)"
            value={boxSize.x}
            onChange={(e) => setBoxSize({ ...boxSize, x: Number(e.target.value) })}
            disabled={loading}
            inputProps={{ min: 1 }}
          />
        </Grid>
        <Grid item xs={4}>
          <TextField
            fullWidth
            type="number"
            label="Size Y (Å)"
            value={boxSize.y}
            onChange={(e) => setBoxSize({ ...boxSize, y: Number(e.target.value) })}
            disabled={loading}
            inputProps={{ min: 1 }}
          />
        </Grid>
        <Grid item xs={4}>
          <TextField
            fullWidth
            type="number"
            label="Size Z (Å)"
            value={boxSize.z}
            onChange={(e) => setBoxSize({ ...boxSize, z: Number(e.target.value) })}
            disabled={loading}
            inputProps={{ min: 1 }}
          />
        </Grid>

        <Grid item xs={12}>
          <Button
            fullWidth
            variant="contained"
            onClick={handleDocking}
            disabled={loading || !proteinPath || !ligandSmiles}
          >
            {loading ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <CircularProgress size={24} color="inherit" />
                <Typography>Running Docking...</Typography>
              </Box>
            ) : (
              'Start Docking'
            )}
          </Button>
        </Grid>

        {error && (
          <Grid item xs={12}>
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          </Grid>
        )}

        {results && (
          <Grid item xs={12}>
            <Paper variant="outlined" sx={{ p: 2, mt: 2 }}>
              <Typography variant="subtitle1" color="primary" gutterBottom>
                Docking Results
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell component="th" sx={{ fontWeight: 'bold' }}>
                        Best Binding Affinity
                      </TableCell>
                      <TableCell>
                        {results.binding_affinity !== null
                          ? `${results.binding_affinity.toFixed(2)} kcal/mol`
                          : 'N/A'
                        }
                      </TableCell>
                    </TableRow>
                    {results.poses_path && (
                      <TableRow>
                        <TableCell component="th" sx={{ fontWeight: 'bold' }}>
                          Download
                        </TableCell>
                        <TableCell>
                          <Grid container spacing={1}>
                            <Grid item>
                              <Button
                                variant="outlined"
                                size="small"
                                onClick={() => {
                                  const downloadUrl = `${config.apiUrl}/api/download/${results.complex_path}`;
                                  window.open(downloadUrl, '_blank');
                                }}
                              >
                                Download Complex (PDB)
                              </Button>
                            </Grid>
                            <Grid item>
                              <Button
                                variant="outlined"
                                size="small"
                                onClick={() => {
                                  const downloadUrl = `${config.apiUrl}/api/download/${results.poses_path}`;
                                  window.open(downloadUrl, '_blank');
                                }}
                              >
                                Download All Poses (PDBQT)
                              </Button>
                            </Grid>
                          </Grid>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Paper>
  );
};

export default DockingConfig;
