import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box } from '@mui/material';
import Sidebar from './Sidebar';

export const AppLayout: React.FC = () => {
  return (
    <Box sx={{ display: 'flex', height: '100vh', bgcolor: '#fafafa' }}>
      <Sidebar />
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Box component="main" sx={{ flex: 1, overflow: 'auto' }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
};

export default AppLayout;
