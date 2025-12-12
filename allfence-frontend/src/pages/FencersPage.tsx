import React, { useState } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Avatar,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useGetFencersQuery } from '../api/fencers';
import { useGetClubsQuery } from '../api/clubs';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { setFencerFilters } from '../store/slices/uiSlice';
import { LoadingSpinner, ErrorMessage } from '../components/common';
import { getInitials } from '../utils/formatters';
import { WEAPON_CHOICES, BRACKET_CHOICES, GENDER_CHOICES } from '../utils/constants';
import { WeaponType, AgeBracket, Gender } from '../types';

export const FencersPage: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const filters = useAppSelector((state) => state.ui.fencerFilters);
  const [searchText, setSearchText] = useState('');

  // Fetch fencers with filters
  const { data: fencers = [], isLoading, error, refetch } = useGetFencersQuery(filters);
  const { data: clubs = [] } = useGetClubsQuery();

  // Create club lookup map
  const clubMap = new Map(clubs.map((club) => [club.club_id, club.club_name]));

  // Filter by search text and sort alphabetically
  const filteredFencers = fencers
    .filter((f) => f.full_name.toLowerCase().includes(searchText.toLowerCase()))
    .sort((a, b) => a.full_name.localeCompare(b.full_name));

  const handleWeaponChange = (weapon: string | '') => {
    dispatch(
      setFencerFilters({
        ...filters,
        weapon: weapon ? (weapon as WeaponType) : undefined,
      })
    );
  };

  const handleBracketChange = (bracket: string | '') => {
    dispatch(
      setFencerFilters({
        ...filters,
        bracket: bracket ? (bracket as AgeBracket) : undefined,
      })
    );
  };

  const handleGenderChange = (gender: string | '') => {
    dispatch(
      setFencerFilters({
        ...filters,
        gender: gender ? (gender as Gender) : undefined,
      })
    );
  };

  const handleClubChange = (clubId: string | '') => {
    dispatch(
      setFencerFilters({
        ...filters,
        club_id: clubId || undefined,
      })
    );
  };

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message="Failed to load fencers" onRetry={refetch} />;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 4 }}>
        👥 Fencers ({filteredFencers.length})
      </Typography>

      {/* Filters Card */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
            Filters
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="Search"
                placeholder="Fencer name..."
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                variant="outlined"
                size="small"
              />
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Weapon</InputLabel>
                <Select
                  value={filters.weapon || ''}
                  onChange={(e) => handleWeaponChange(e.target.value)}
                  label="Weapon"
                >
                  <MenuItem value="">All Weapons</MenuItem>
                  {WEAPON_CHOICES.map((w) => (
                    <MenuItem key={w} value={w}>
                      {w}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Bracket</InputLabel>
                <Select
                  value={filters.bracket || ''}
                  onChange={(e) => handleBracketChange(e.target.value)}
                  label="Bracket"
                >
                  <MenuItem value="">All Brackets</MenuItem>
                  {BRACKET_CHOICES.map((b) => (
                    <MenuItem key={b} value={b}>
                      {b}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Gender</InputLabel>
                <Select
                  value={filters.gender || ''}
                  onChange={(e) => handleGenderChange(e.target.value)}
                  label="Gender"
                >
                  <MenuItem value="">All Genders</MenuItem>
                  {GENDER_CHOICES.map((g) => (
                    <MenuItem key={g} value={g}>
                      {g === 'M' ? 'Male' : 'Female'}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Club</InputLabel>
                <Select
                  value={filters.club_id || ''}
                  onChange={(e) => handleClubChange(e.target.value)}
                  label="Club"
                >
                  <MenuItem value="">All Clubs</MenuItem>
                  {clubs.map((club) => (
                    <MenuItem key={club.club_id} value={club.club_id}>
                      {club.club_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Fencers Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }} width="50"></TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Name</TableCell>
              <TableCell>Age</TableCell>
              <TableCell>Bracket</TableCell>
              <TableCell>Weapon</TableCell>
              <TableCell>Gender</TableCell>
              <TableCell>Club</TableCell>
              <TableCell>Points</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredFencers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={9} sx={{ textAlign: 'center', py: 3, color: 'textSecondary' }}>
                  No fencers found
                </TableCell>
              </TableRow>
            ) : (
              filteredFencers.map((fencer) => {
                const ranking = fencer.rankings[0];
                return (
                  <TableRow key={fencer.fencer_id} hover>
                    <TableCell>
                      <Avatar alt={fencer.full_name} sx={{ width: 32, height: 32, fontSize: '0.9rem' }}>
                        {getInitials(fencer.full_name)}
                      </Avatar>
                    </TableCell>
                    <TableCell sx={{ fontWeight: 'semibold' }}>{fencer.full_name}</TableCell>
                    <TableCell>{fencer.age}</TableCell>
                    <TableCell>{ranking?.bracket_name || 'N/A'}</TableCell>
                    <TableCell>{fencer.weapon}</TableCell>
                    <TableCell>{fencer.gender === 'M' ? 'Male' : 'Female'}</TableCell>
                    <TableCell>{clubMap.get(fencer.club_id) || 'Unknown'}</TableCell>
                    <TableCell sx={{ fontWeight: 'semibold' }}>{ranking?.points || 0}</TableCell>
                    <TableCell>
                      <Button
                        size="small"
                        color="primary"
                        onClick={() => navigate(`/fencers/${fencer.fencer_id}`)}
                      >
                        View
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default FencersPage;
