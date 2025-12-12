import React from 'react';
import { Alert, Box } from '@mui/material';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, onRetry }) => {
  return (
    <Box margin={2}>
      <Alert severity="error">
        {message}
        {onRetry && (
          <button onClick={onRetry} style={{ marginLeft: 8, textDecoration: 'underline', cursor: 'pointer' }}>
            Retry
          </button>
        )}
      </Alert>
    </Box>
  );
};

export default ErrorMessage;
