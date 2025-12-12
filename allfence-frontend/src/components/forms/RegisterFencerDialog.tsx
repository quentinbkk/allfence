import React, { useState } from 'react';
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
  Checkbox,
  Typography,
  Alert,
  Chip,
} from '@mui/material';
import { useGetFencersQuery } from '../../api/fencers';
import { useRegisterFencerMutation } from '../../api/tournaments';
import { Tournament } from '../../types';

interface RegisterFencerDialogProps {
  open: boolean;
  tournament: Tournament;
  onClose: () => void;
  onSuccess: () => void;
}

export const RegisterFencerDialog: React.FC<RegisterFencerDialogProps> = ({
  open,
  tournament,
  onClose,
  onSuccess,
}) => {
  const [searchText, setSearchText] = useState('');
  const [selectedFencers, setSelectedFencers] = useState<number[]>([]);
  const [error, setError] = useState('');

  const { data: allFencers = [], refetch } = useGetFencersQuery();
  const [registerFencer, { isLoading }] = useRegisterFencerMutation();

  // Refetch fencers when dialog opens to ensure fresh data
  React.useEffect(() => {
    if (open) {
      refetch();
    }
  }, [open, refetch]);

  // Filter fencers based on eligibility and search
  const eligibleFencers = allFencers.filter((fencer) => {
    // Check name matches search
    if (searchText && !fencer.full_name.toLowerCase().includes(searchText.toLowerCase())) {
      return false;
    }

    // Check bracket matches (use computed bracket field)
    const bracketMatch = fencer.bracket === tournament.bracket;
    
    // Check weapon matches
    const weaponMatch = fencer.weapon === tournament.weapon;
    
    // Check gender matches (if tournament specifies)
    const genderMatch = !tournament.gender || fencer.gender === tournament.gender;

    // Debug individual fencer (first 3 only)
    if (open && allFencers.indexOf(fencer) < 3) {
      console.log(`Fencer ${fencer.full_name}:`, {
        bracket: fencer.bracket,
        tournamentBracket: tournament.bracket,
        bracketMatch,
        weapon: fencer.weapon,
        tournamentWeapon: tournament.weapon,
        weaponMatch,
        gender: fencer.gender,
        tournamentGender: tournament.gender,
        genderMatch,
        passes: bracketMatch && weaponMatch && genderMatch
      });
    }

    return bracketMatch && weaponMatch && genderMatch;
  });

  // Debug logging
  React.useEffect(() => {
    if (open) {
      console.log('Tournament:', tournament);
      console.log('All fencers count:', allFencers.length);
      console.log('Sample fencer:', allFencers[0]);
      console.log('Eligible fencers count:', eligibleFencers.length);
      console.log('First 3 eligible:', eligibleFencers.slice(0, 3));
    }
  }, [open, allFencers, eligibleFencers, tournament]);

  const handleToggleFencer = (fencerId: number) => {
    setSelectedFencers((prev) =>
      prev.includes(fencerId) ? prev.filter((id) => id !== fencerId) : [...prev, fencerId]
    );
  };

  const handleSelectAll = () => {
    if (selectedFencers.length === eligibleFencers.length) {
      setSelectedFencers([]);
    } else {
      setSelectedFencers(eligibleFencers.map((f) => f.fencer_id));
    }
  };

  const handleRegister = async () => {
    setError('');
    try {
      // Register all selected fencers
      const promises = selectedFencers.map((fencer_id) =>
        registerFencer({ tournament_id: tournament.tournament_id, fencer_id }).unwrap()
      );

      await Promise.all(promises);
      
      setSelectedFencers([]);
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.data?.error || 'Failed to register some fencers');
    }
  };

  const handleClose = () => {
    setSelectedFencers([]);
    setError('');
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>📝 Register Fencers for Tournament</DialogTitle>
      <DialogContent>
        {/* Tournament Info */}
        <Box sx={{ mb: 3, p: 2, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
            Tournament Requirements:
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Chip label={`Bracket: ${tournament.bracket}`} size="small" />
            <Chip label={`Weapon: ${tournament.weapon}`} size="small" />
            {tournament.gender && <Chip label={`Gender: ${tournament.gender}`} size="small" />}
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Search Box */}
        <TextField
          fullWidth
          label="Search Fencers"
          placeholder="Enter fencer name..."
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          sx={{ mb: 2 }}
        />

        {/* Stats */}
        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="body2" color="textSecondary">
            {eligibleFencers.length} eligible fencers found
          </Typography>
          <Typography variant="body2" color="primary" sx={{ fontWeight: 'bold' }}>
            {selectedFencers.length} selected
          </Typography>
        </Box>

        {/* Fencers Table */}
        <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={selectedFencers.length === eligibleFencers.length && eligibleFencers.length > 0}
                    indeterminate={selectedFencers.length > 0 && selectedFencers.length < eligibleFencers.length}
                    onChange={handleSelectAll}
                  />
                </TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Name</TableCell>
                <TableCell>Club</TableCell>
                <TableCell>Weapon</TableCell>
                <TableCell>Bracket</TableCell>
                <TableCell>Points</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {eligibleFencers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} sx={{ textAlign: 'center', py: 3, color: 'textSecondary' }}>
                    No eligible fencers found
                  </TableCell>
                </TableRow>
              ) : (
                eligibleFencers.map((fencer) => (
                  <TableRow
                    key={fencer.fencer_id}
                    hover
                    onClick={() => handleToggleFencer(fencer.fencer_id)}
                    sx={{ cursor: 'pointer' }}
                  >
                    <TableCell padding="checkbox">
                      <Checkbox checked={selectedFencers.includes(fencer.fencer_id)} />
                    </TableCell>
                    <TableCell>{fencer.full_name}</TableCell>
                    <TableCell>{fencer.club_name || fencer.club_id}</TableCell>
                    <TableCell>{fencer.weapon}</TableCell>
                    <TableCell>{fencer.rankings[0]?.bracket_name || 'N/A'}</TableCell>
                    <TableCell>{fencer.rankings[0]?.points || 0}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={isLoading}>
          Cancel
        </Button>
        <Button
          onClick={handleRegister}
          variant="contained"
          disabled={selectedFencers.length === 0 || isLoading}
        >
          {isLoading ? 'Registering...' : `Register ${selectedFencers.length} Fencer${selectedFencers.length !== 1 ? 's' : ''}`}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RegisterFencerDialog;
