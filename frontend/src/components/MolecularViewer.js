import React, { useEffect, useRef } from 'react';
import { Box, Typography } from '@mui/material';

const MolecularViewer = ({ pdbData, style = {} }) => {
  const viewerRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!pdbData || !containerRef.current) return;

    // Clear previous viewer if it exists
    if (viewerRef.current) {
      try {
        viewerRef.current.clear();
      } catch (error) {
        console.error('Error clearing viewer:', error);
      }
    }

    // Ensure 3Dmol is available
    if (typeof window === 'undefined' || !window.$3Dmol) {
      console.error('3Dmol.js not loaded');
      return;
    }

    try {
      // Initialize 3Dmol viewer
      const config = {
        backgroundColor: 'white',
        antialias: true,
        id: containerRef.current.id
      };
      
      const viewer = window.$3Dmol.createViewer(containerRef.current, config);
      viewerRef.current = viewer;

      // Add the molecule
      if (typeof pdbData === 'string') {
        viewer.addModel(pdbData, "pdb");

        // Style the protein
        viewer.setStyle({}, {
          cartoon: {
            color: 'spectrum'
          }
        });

        // Style hetero atoms (ligands)
        viewer.setStyle({hetflag: true}, {
          stick: {
            radius: 0.2,
            colorscheme: 'greenCarbon'
          }
        });

        // Add surface
        viewer.addSurface(window.$3Dmol.SurfaceType.VDW, {
          opacity: 0.7,
          color: 'white'
        });

        // Zoom to fit
        viewer.zoomTo();

        // Render the scene
        viewer.render();
      } else {
        throw new Error('Invalid PDB data format');
      }
    } catch (error) {
      console.error('Error initializing molecular viewer:', error);
    }

    // Cleanup function
    return () => {
      if (viewerRef.current) {
        try {
          viewerRef.current.clear();
        } catch (error) {
          console.error('Error cleaning up viewer:', error);
        }
      }
    };
  }, [pdbData]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (viewerRef.current) {
        try {
          viewerRef.current.resize();
        } catch (error) {
          console.error('Error resizing viewer:', error);
        }
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  if (!pdbData) {
    return (
      <Box sx={{ 
        height: '100%', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center' 
      }}>
        <Typography variant="body1" color="text.secondary">
          No structure to display
        </Typography>
      </Box>
    );
  }

  return (
    <Box
      ref={containerRef}
      id="molecular-viewer"
      sx={{
        width: '100%',
        height: '100%',
        ...style
      }}
    />
  );
};

export default MolecularViewer;
