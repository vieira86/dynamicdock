import React from 'react';
import {
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Box
} from '@mui/material';

const LigandInfo = ({ ligands = [], mainLigand = null }) => {
  // Helper function to format coordinates
  const formatCoord = (coord) => {
    return typeof coord === 'number' ? coord.toFixed(2) : 'N/A';
  };

  // Helper function to format ligand data
  const formatLigandData = (ligand) => {
    if (!ligand || typeof ligand !== 'object') return null;

    return {
      name: ligand.name || 'Unknown',
      smiles: ligand.smiles || 'N/A',
      coordinates: ligand.coordinates || {},
      isMain: mainLigand?.name === ligand.name
    };
  };

  // Format main ligand data
  const formattedMainLigand = formatLigandData(mainLigand);

  // Format all ligands data
  const formattedLigands = ligands
    .map(formatLigandData)
    .filter(Boolean); // Remove null values

  if (!formattedMainLigand && formattedLigands.length === 0) {
    return null;
  }

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom color="primary">
        Ligand Information
      </Typography>

      {/* Main Ligand Section */}
      {formattedMainLigand && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom color="primary">
            Main Ligand
          </Typography>
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableBody>
                <TableRow>
                  <TableCell component="th" sx={{ fontWeight: 'bold', width: '30%' }}>
                    Name
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={formattedMainLigand.name} 
                      color="primary" 
                      variant="outlined" 
                      size="small" 
                    />
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell component="th" sx={{ fontWeight: 'bold' }}>
                    SMILES
                  </TableCell>
                  <TableCell sx={{ wordBreak: 'break-all' }}>
                    {formattedMainLigand.smiles}
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell component="th" sx={{ fontWeight: 'bold' }}>
                    Coordinates
                  </TableCell>
                  <TableCell>
                    X: {formatCoord(formattedMainLigand.coordinates.x)}, 
                    Y: {formatCoord(formattedMainLigand.coordinates.y)}, 
                    Z: {formatCoord(formattedMainLigand.coordinates.z)}
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}

      {/* Other Ligands Section */}
      {formattedLigands.length > 0 && (
        <Box>
          <Typography variant="subtitle2" gutterBottom color="primary">
            Other Ligands
          </Typography>
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Name</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>SMILES</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Coordinates</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {formattedLigands.map((ligand, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      <Chip 
                        label={ligand.name} 
                        color={ligand.isMain ? 'primary' : 'default'} 
                        variant="outlined" 
                        size="small" 
                      />
                    </TableCell>
                    <TableCell sx={{ wordBreak: 'break-all' }}>
                      {ligand.smiles}
                    </TableCell>
                    <TableCell>
                      X: {formatCoord(ligand.coordinates.x)}, 
                      Y: {formatCoord(ligand.coordinates.y)}, 
                      Z: {formatCoord(ligand.coordinates.z)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}
    </Paper>
  );
};

export default LigandInfo;
