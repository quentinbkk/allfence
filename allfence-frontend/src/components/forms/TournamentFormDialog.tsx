import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Alert,
} from '@mui/material';
import { WEAPON_CHOICES, BRACKET_CHOICES } from '../../utils/constants';
import { WeaponType, AgeBracket, Gender, CompetitionType, TournamentStatus } from '../../types';

interface TournamentFormDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: any) => Promise<void>;
}

export const TournamentFormDialog: React.FC<TournamentFormDialogProps> = ({ open, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    tournament_name: '',
    date: '',
    weapon: WeaponType.EPEE,
    bracket: AgeBracket.SENIOR,
    competition_type: CompetitionType.LOCAL,
    gender: '' as Gender | '',
    location: '',
    max_participants: '',
    description: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (field: string, value: any) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await onSubmit({
        ...formData,
        max_participants: formData.max_participants ? parseInt(formData.max_participants) : undefined,
        gender: formData.gender || undefined,
      });
      onClose();
      // Reset form
      setFormData({
        tournament_name: '',
        date: '',
        weapon: WeaponType.EPEE,
        bracket: AgeBracket.SENIOR,
        competition_type: CompetitionType.LOCAL,
        gender: '',
        location: '',
        max_participants: '',
        description: '',
      });
    } catch (err: any) {
      setError(err.data?.error || 'Failed to create tournament');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>🏆 Create New Tournament</DialogTitle>
        <DialogContent>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Tournament Name"
                value={formData.tournament_name}
                onChange={(e) => handleChange('tournament_name', e.target.value)}
                required
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Date"
                type="date"
                value={formData.date}
                onChange={(e) => handleChange('date', e.target.value)}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Location"
                value={formData.location}
                onChange={(e) => handleChange('location', e.target.value)}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>Weapon</InputLabel>
                <Select
                  value={formData.weapon}
                  onChange={(e) => handleChange('weapon', e.target.value)}
                  label="Weapon"
                >
                  {WEAPON_CHOICES.map((weapon) => (
                    <MenuItem key={weapon} value={weapon}>{weapon}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>Age Bracket</InputLabel>
                <Select
                  value={formData.bracket}
                  onChange={(e) => handleChange('bracket', e.target.value)}
                  label="Age Bracket"
                >
                  {BRACKET_CHOICES.map((bracket) => (
                    <MenuItem key={bracket} value={bracket}>{bracket}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>Competition Type</InputLabel>
                <Select
                  value={formData.competition_type}
                  onChange={(e) => handleChange('competition_type', e.target.value)}
                  label="Competition Type"
                >
                  <MenuItem value={CompetitionType.LOCAL}>Local</MenuItem>
                  <MenuItem value={CompetitionType.REGIONAL}>Regional</MenuItem>
                  <MenuItem value={CompetitionType.NATIONAL}>National</MenuItem>
                  <MenuItem value={CompetitionType.INTERNATIONAL}>International</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Gender</InputLabel>
                <Select
                  value={formData.gender}
                  onChange={(e) => handleChange('gender', e.target.value)}
                  label="Gender"
                >
                  <MenuItem value="">Mixed</MenuItem>
                  <MenuItem value={Gender.MALE}>Male</MenuItem>
                  <MenuItem value={Gender.FEMALE}>Female</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Max Participants"
                type="number"
                value={formData.max_participants}
                onChange={(e) => handleChange('max_participants', e.target.value)}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} disabled={loading}>Cancel</Button>
          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? 'Creating...' : 'Create Tournament'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default TournamentFormDialog;
