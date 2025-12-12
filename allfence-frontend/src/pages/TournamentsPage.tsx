import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
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
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useGetTournamentsQuery, useCreateTournamentMutation } from '../api/tournaments';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { setTournamentFilters } from '../store/slices/uiSlice';
import { LoadingSpinner, ErrorMessage, StatusBadge } from '../components/common';
import { formatDate } from '../utils/formatters';
import { WEAPON_CHOICES, BRACKET_CHOICES } from '../utils/constants';
import { TournamentStatus, WeaponType, AgeBracket } from '../types';
import TournamentFormDialog from '../components/forms/TournamentFormDialog';

export const TournamentsPage: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const filters = useAppSelector((state) => state.ui.tournamentFilters);
  const { user } = useAppSelector((state) => state.auth);
  const [searchText, setSearchText] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);

  // Fetch tournaments with filters
  const { data: tournaments = [], isLoading, error, refetch } = useGetTournamentsQuery(filters);
  const [createTournament] = useCreateTournamentMutation();

  // Filter tournaments by search text
  const filteredTournaments = tournaments.filter((t) =>
    t.tournament_name.toLowerCase().includes(searchText.toLowerCase())
  );

  const handleStatusChange = (status: TournamentStatus | '') => {
    dispatch(
      setTournamentFilters({
        ...filters,
        status: status ? (status as TournamentStatus) : undefined,
      })
    );
  };

  const handleWeaponChange = (weapon: string | '') => {
    dispatch(
      setTournamentFilters({
        ...filters,
        weapon: weapon ? (weapon as WeaponType) : undefined,
      })
    );
  };

  const handleBracketChange = (bracket: string | '') => {
    dispatch(
      setTournamentFilters({
        ...filters,
        bracket: bracket ? (bracket as AgeBracket) : undefined,
      })
    );
  };

  const handleCreateTournament = async (data: any) => {
    await createTournament(data).unwrap();
    refetch();
  };

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message="Failed to load tournaments" onRetry={refetch} />;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          🏆 Tournaments
        </Typography>
        {user?.is_admin && (
          <Button variant="contained" color="primary" onClick={() => setDialogOpen(true)}>
            + New Tournament
          </Button>
        )}
      </Box>

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
                placeholder="Tournament name..."
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                variant="outlined"
                size="small"
              />
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status || ''}
                  onChange={(e) => handleStatusChange(e.target.value as TournamentStatus | '')}
                  label="Status"
                >
                  <MenuItem value="">All Statuses</MenuItem>
                  {Object.values(TournamentStatus).map((status) => (
                    <MenuItem key={status} value={status}>
                      {status}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
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
          </Grid>
        </CardContent>
      </Card>

      {/* Tournaments Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Tournament</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Weapon</TableCell>
              <TableCell>Bracket</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Participants</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredTournaments.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} sx={{ textAlign: 'center', py: 3, color: 'textSecondary' }}>
                  No tournaments found
                </TableCell>
              </TableRow>
            ) : (
              filteredTournaments.map((tournament) => (
                <TableRow key={tournament.tournament_id} hover>
                  <TableCell 
                    sx={{ 
                      fontWeight: 'semibold',
                      color: 'primary.main',
                      cursor: 'pointer',
                      '&:hover': { textDecoration: 'underline' }
                    }}
                    onClick={() => navigate(`/tournaments/${tournament.tournament_id}`)}
                  >
                    {tournament.tournament_name}
                  </TableCell>
                  <TableCell>{formatDate(tournament.date)}</TableCell>
                  <TableCell>{tournament.weapon}</TableCell>
                  <TableCell>{tournament.bracket}</TableCell>
                  <TableCell>
                    <StatusBadge status={tournament.status} />
                  </TableCell>
                  <TableCell>
                    {tournament.participant_count}
                    {tournament.max_participants ? ` / ${tournament.max_participants}` : ''}
                  </TableCell>
                  <TableCell>{tournament.competition_type}</TableCell>
                  <TableCell>
                    <Button
                      size="small"
                      color="primary"
                      onClick={() => navigate(`/tournaments/${tournament.tournament_id}`)}
                    >
                      View
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {filteredTournaments.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 6 }}>
          <Typography variant="body1" color="textSecondary">
            No tournaments to display. {searchText && 'Try adjusting your filters.'}
          </Typography>
        </Box>
      )}

      <TournamentFormDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onSubmit={handleCreateTournament}
      />
    </Container>
  );
};

export default TournamentsPage;
