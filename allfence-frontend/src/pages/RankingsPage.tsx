import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
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
import { useGetRankingsQuery } from '../api/rankings';
import { LoadingSpinner, ErrorMessage } from '../components/common';
import { BRACKET_CHOICES, WEAPON_CHOICES } from '../utils/constants';
import { AgeBracket, WeaponType, Gender } from '../types';
import { getInitials } from '../utils/formatters';

export const RankingsPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedBracket, setSelectedBracket] = useState<AgeBracket>(AgeBracket.SENIOR);
  const [selectedWeapon, setSelectedWeapon] = useState<WeaponType | ''>('');
  const [selectedGender, setSelectedGender] = useState<Gender | ''>('');

  // Fetch rankings for selected bracket and weapon
  const { data: rankings = [], isLoading, error } = useGetRankingsQuery({
    bracket: selectedBracket,
    weapon: selectedWeapon || undefined,
  });

  // Filter by gender on frontend (since rankings don't have gender, we filter by fencer)
  const filteredRankings = selectedGender
    ? rankings.filter(r => r.fencer?.gender === selectedGender)
    : rankings;

  // Sort rankings by points descending
  const sortedRankings = [...filteredRankings].sort((a, b) => b.points - a.points);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message="Failed to load rankings" />;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          📊 Rankings Leaderboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            onClick={() => navigate('/rankings/progress')}
          >
            📈 Progress Chart
          </Button>
          <Button
            variant="outlined"
            onClick={() => navigate('/rankings/clubs')}
          >
            🏛️ Club Rankings
          </Button>
        </Box>
      </Box>

      {/* Bracket and Weapon Selectors */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Select Bracket</InputLabel>
                <Select
                  value={selectedBracket}
                  onChange={(e) => setSelectedBracket(e.target.value as AgeBracket)}
                  label="Select Bracket"
                >
                  {BRACKET_CHOICES.map((bracket) => (
                    <MenuItem key={bracket} value={bracket}>
                      {bracket}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Weapon</InputLabel>
                <Select
                  value={selectedWeapon}
                  onChange={(e) => setSelectedWeapon(e.target.value as WeaponType | '')}
                  label="Weapon"
                >
                  <MenuItem value="">All Weapons</MenuItem>
                  {WEAPON_CHOICES.map((weapon) => (
                    <MenuItem key={weapon} value={weapon}>
                      {weapon}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Gender</InputLabel>
                <Select
                  value={selectedGender}
                  onChange={(e) => setSelectedGender(e.target.value as Gender | '')}
                  label="Gender"
                >
                  <MenuItem value="">All Genders</MenuItem>
                  <MenuItem value={Gender.MALE}>Male</MenuItem>
                  <MenuItem value={Gender.FEMALE}>Female</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Rankings Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead sx={{ background: 'linear-gradient(to right, #1976d2, #1565c0)', color: 'white' }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold', color: 'white' }}>Rank</TableCell>
              <TableCell sx={{ fontWeight: 'bold', color: 'white' }}></TableCell>
              <TableCell sx={{ fontWeight: 'bold', color: 'white' }}>Name</TableCell>
              <TableCell sx={{ fontWeight: 'bold', color: 'white' }}>Club</TableCell>
              <TableCell sx={{ fontWeight: 'bold', color: 'white', textAlign: 'right' }}>
                Points
              </TableCell>
              <TableCell sx={{ fontWeight: 'bold', color: 'white' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedRankings.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} sx={{ textAlign: 'center', py: 3, color: 'textSecondary' }}>
                  No fencers in this bracket
                </TableCell>
              </TableRow>
            ) : (
              sortedRankings.map((ranking, index) => {
                const fencer = ranking.fencer;
                const medalEmoji =
                  index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '';

                return (
                  <TableRow
                    key={ranking.ranking_id}
                    sx={{
                      backgroundColor: index < 3 ? '#fffde7' : 'transparent',
                      '&:hover': { backgroundColor: index < 3 ? '#fff9c4' : '#f5f5f5' },
                    }}
                  >
                    <TableCell sx={{ fontWeight: 'bold', fontSize: '1.1rem' }}>
                      {medalEmoji || index + 1}
                    </TableCell>
                    <TableCell>
                      {fencer && (
                        <Avatar alt={fencer.full_name} sx={{ width: 32, height: 32, fontSize: '0.9rem' }}>
                          {getInitials(fencer.full_name)}
                        </Avatar>
                      )}
                    </TableCell>
                    <TableCell sx={{ fontWeight: 'semibold' }}>
                      {fencer?.full_name || 'Unknown'}
                    </TableCell>
                    <TableCell>{fencer?.club_name || fencer?.club_id || 'N/A'}</TableCell>
                    <TableCell sx={{ fontWeight: 'bold', fontSize: '1.05rem', textAlign: 'right' }}>
                      {ranking.points}
                    </TableCell>
                    <TableCell>
                      {fencer && (
                        <Button
                          size="small"
                          color="primary"
                          onClick={() => navigate(`/fencers/${fencer.fencer_id}`)}
                        >
                          Profile
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Statistics */}
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                  {sortedRankings.length}
                </Typography>
                <Typography color="textSecondary">Fencers in {selectedBracket}</Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                  {Math.max(...sortedRankings.map((r) => r.points), 0)}
                </Typography>
                <Typography color="textSecondary">Highest Points</Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                  {sortedRankings.length > 0
                    ? (sortedRankings.reduce((sum, r) => sum + r.points, 0) / sortedRankings.length).toFixed(0)
                    : 0}
                </Typography>
                <Typography color="textSecondary">Average Points</Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Container>
  );
};

export default RankingsPage;
