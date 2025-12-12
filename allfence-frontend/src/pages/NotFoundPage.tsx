import React from 'react';
import { Container, Typography, Box } from '@mui/material';

export const NotFoundPage: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 8 }}>
      <Box sx={{ textAlign: 'center' }}>
        <Typography variant="h2" sx={{ fontWeight: 'bold', mb: 2 }}>
          404
        </Typography>
        <Typography variant="h4" color="textSecondary" sx={{ mb: 4 }}>
          Page Not Found
        </Typography>
        <Typography variant="body1" color="textSecondary">
          The page you're looking for doesn't exist.
        </Typography>
      </Box>
    </Container>
  );
};

export default NotFoundPage;
