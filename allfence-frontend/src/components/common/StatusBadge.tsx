import React from 'react';
import { Chip } from '@mui/material';
import { TournamentStatus } from '../../types';

interface StatusBadgeProps {
  status: TournamentStatus;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const statusColors: Record<TournamentStatus, 'default' | 'success' | 'error' | 'warning' | 'info'> = {
    [TournamentStatus.UPCOMING]: 'warning',
    [TournamentStatus.REGISTRATION_OPEN]: 'info',
    [TournamentStatus.IN_PROGRESS]: 'warning',
    [TournamentStatus.COMPLETED]: 'success',
    [TournamentStatus.CANCELLED]: 'error',
  };

  return <Chip label={status} color={statusColors[status]} variant="outlined" />;
};

export default StatusBadge;
