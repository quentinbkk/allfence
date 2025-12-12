import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Alert,
  Chip,
} from '@mui/material';
import { useRecordResultsMutation } from '../../api/tournaments';
import { Tournament } from '../../types';

interface Participant {
  result_id: number;
  fencer_id: number;
  full_name: string;
  club_name?: string;
  weapon: string;
  placement?: number | null;
  points_awarded: number;
}

interface RecordResultsDialogProps {
  open: boolean;
  tournament: Tournament;
  participants: Participant[];
  onClose: () => void;
  onSuccess: () => void;
}

// Point structure by competition type
const POINT_STRUCTURES: Record<string, { 1: number; 2: number; 3: number }> = {
  Local: { 1: 50, 2: 38, 3: 25 },
  Regional: { 1: 100, 2: 75, 3: 50 },
  National: { 1: 150, 2: 113, 3: 75 },
  Championship: { 1: 200, 2: 150, 3: 100 },
  International: { 1: 250, 2: 188, 3: 125 },
};

export const RecordResultsDialog: React.FC<RecordResultsDialogProps> = ({
  open,
  tournament,
  participants,
  onClose,
  onSuccess,
}) => {
  const [placements, setPlacements] = useState<Record<number, number>>({});
  const [error, setError] = useState('');

  const [recordResults, { isLoading }] = useRecordResultsMutation();

  // Initialize placements from existing data
  useEffect(() => {
    const initialPlacements: Record<number, number> = {};
    participants.forEach((p) => {
      if (p.placement && p.placement > 0) {
        initialPlacements[p.fencer_id] = p.placement;
      }
    });
    setPlacements(initialPlacements);
  }, [participants]);

  const handlePlacementChange = (fencerId: number, value: string) => {
    const placement = parseInt(value);
    if (value === '' || (placement > 0 && placement <= participants.length)) {
      setPlacements((prev) => ({
        ...prev,
        [fencerId]: placement || 0,
      }));
    }
  };

  const handleSubmit = async () => {
    setError('');

    // Validate all participants have placements
    const missingPlacements = participants.filter((p) => !placements[p.fencer_id]);
    if (missingPlacements.length > 0) {
      setError('All participants must have a placement assigned');
      return;
    }

    // Check for duplicate placements
    const placementValues = Object.values(placements);
    const uniquePlacements = new Set(placementValues);
    if (placementValues.length !== uniquePlacements.size) {
      setError('Each placement must be unique');
      return;
    }

    try {
      // Format results for API
      const results = Object.entries(placements).map(([fencer_id, placement]) => ({
        fencer_id: parseInt(fencer_id),
        placement,
      }));

      await recordResults({
        tournament_id: tournament.tournament_id,
        results,
      }).unwrap();

      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.data?.error || 'Failed to record results');
    }
  };

  const handleClose = () => {
    setError('');
    onClose();
  };

  const pointStructure = POINT_STRUCTURES[tournament.competition_type] || POINT_STRUCTURES.Regional;

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Record Results - {tournament.tournament_name}
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          {tournament.date} • {tournament.competition_type}
        </Typography>
      </DialogTitle>
      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Point Structure ({tournament.competition_type})
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Chip label={`1st: ${pointStructure[1]} pts`} color="primary" size="small" />
            <Chip label={`2nd: ${pointStructure[2]} pts`} color="primary" size="small" />
            <Chip label={`3rd: ${pointStructure[3]} pts`} color="primary" size="small" />
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Placement</TableCell>
                <TableCell>Fencer</TableCell>
                <TableCell>Club</TableCell>
                <TableCell>Weapon</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {participants.map((participant) => (
                <TableRow key={participant.fencer_id}>
                  <TableCell>
                    <TextField
                      type="number"
                      size="small"
                      value={placements[participant.fencer_id] || ''}
                      onChange={(e) => handlePlacementChange(participant.fencer_id, e.target.value)}
                      inputProps={{
                        min: 1,
                        max: participants.length,
                        style: { width: '60px' },
                      }}
                      placeholder="#"
                    />
                  </TableCell>
                  <TableCell>{participant.full_name}</TableCell>
                  <TableCell>{participant.club_name || 'N/A'}</TableCell>
                  <TableCell>{participant.weapon}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {participants.length === 0 && (
          <Alert severity="info" sx={{ mt: 2 }}>
            No participants registered for this tournament yet.
          </Alert>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={isLoading || participants.length === 0}
        >
          {isLoading ? 'Recording...' : 'Record Results'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
