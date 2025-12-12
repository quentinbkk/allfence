import React from 'react';
import { CircularProgress, Box } from '@mui/material';

export const LoadingSpinner: React.FC = () => {
  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
      <CircularProgress />
    </Box>
  );
};

export default LoadingSpinner;
