import React, { useState, useEffect } from 'react';
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
import { WEAPON_CHOICES } from '../../utils/constants';
import { Gender, Fencer } from '../../types';

interface FencerEditDialogProps {
  open: boolean;
  fencer: Fencer;
  clubs: Array<{ club_id: string; club_name: string }>;
  onClose: () => void;
  onSubmit: (data: any) => Promise<void>;
}

export const FencerEditDialog: React.FC<FencerEditDialogProps> = ({ 
  open, 
  fencer, 
  clubs,
  onClose, 
  onSubmit 
}) => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    dob: '',
    gender: '',
    weapon: '',
    club_id: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Update form when fencer or dialog opens
  useEffect(() => {
    if (open && fencer) {
      setFormData({
        first_name: fencer.first_name || '',
        last_name: fencer.last_name || '',
        dob: fencer.dob || '',
        gender: fencer.gender || '',
        weapon: fencer.weapon || '',
        club_id: fencer.club_id || '',
      });
    }
  }, [fencer, open]);

  const handleChange = (field: string, value: any) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await onSubmit(formData);
      onClose();
    } catch (err: any) {
      setError(err.data?.error || 'Failed to update fencer');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>✏️ Edit Fencer Profile</DialogTitle>
        <DialogContent>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="First Name"
                value={formData.first_name}
                onChange={(e) => handleChange('first_name', e.target.value)}
                required
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Last Name"
                value={formData.last_name}
                onChange={(e) => handleChange('last_name', e.target.value)}
                required
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Date of Birth"
                type="date"
                value={formData.dob}
                onChange={(e) => handleChange('dob', e.target.value)}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>Gender</InputLabel>
                <Select
                  value={formData.gender}
                  onChange={(e) => handleChange('gender', e.target.value)}
                  label="Gender"
                >
                  <MenuItem value={Gender.MALE}>Male</MenuItem>
                  <MenuItem value={Gender.FEMALE}>Female</MenuItem>
                </Select>
              </FormControl>
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

            <Grid item xs={12}>
              <FormControl fullWidth required>
                <InputLabel>Club</InputLabel>
                <Select
                  value={formData.club_id}
                  onChange={(e) => handleChange('club_id', e.target.value)}
                  label="Club"
                >
                  {clubs.map((club) => (
                    <MenuItem key={club.club_id} value={club.club_id}>
                      {club.club_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} disabled={loading}>Cancel</Button>
          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? 'Saving...' : 'Save Changes'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default FencerEditDialog;
