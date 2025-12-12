import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Grid,
  Typography,
  TextField,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Checkbox,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow as SimulateIcon,
  CheckCircle as SuccessIcon,
  Info as InfoIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import {
  useGetSeasonsQuery,
  useCreateSeasonMutation,
  useSimulateSeasonMutation,
  useDeleteSeasonMutation,
} from '../api/seasons';
import { useResetAllRankingsMutation, rankingsApi } from '../api/rankings';
import { fencersApi } from '../api/fencers';
import { clubsApi } from '../api/clubs';
import { tournamentsApi } from '../api/tournaments';
import { useDispatch } from 'react-redux';

const SeasonSimulationPage: React.FC = () => {
  const dispatch = useDispatch();
  const { data: seasons, isLoading: loadingSeasons } = useGetSeasonsQuery();
  const [createSeason] = useCreateSeasonMutation();
  const [simulateSeason, { isLoading: simulating }] = useSimulateSeasonMutation();
  const [deleteSeason] = useDeleteSeasonMutation();
  const [resetAllRankings, { isLoading: resettingRankings }] = useResetAllRankingsMutation();

  const [openDialog, setOpenDialog] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [seasonToDelete, setSeasonToDelete] = useState<{ id: number; name: string } | null>(null);
  const [seasonName, setSeasonName] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [numTournaments, setNumTournaments] = useState(100);
  const [resetRankings, setResetRankings] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [simulationStats, setSimulationStats] = useState<any>(null);

  const [dialogError, setDialogError] = useState<string | null>(null);

  const handleCreateSeason = async () => {
    try {
      setDialogError(null);
      setError(null);
      setSuccess(null);

      if (!seasonName || !startDate || !endDate) {
        setDialogError('Please fill in all required fields');
        return;
      }

      await createSeason({
        name: seasonName,
        start_date: startDate,
        end_date: endDate,
        status: 'Upcoming',
      }).unwrap();

      setSuccess(`Season "${seasonName}" created successfully!`);
      setOpenDialog(false);
      setSeasonName('');
      setStartDate('');
      setEndDate('');
      setDialogError(null);
    } catch (err: any) {
      const errorMessage = err.data?.error || err.error || 'Failed to create season';
      setDialogError(errorMessage);
    }
  };

  const handleSimulateSeason = async (seasonId: number, seasonName: string) => {
    try {
      setError(null);
      setSuccess(null);
      setSimulationStats(null);

      const result = await simulateSeason({
        season_id: seasonId,
        options: {
          num_tournaments: numTournaments,
          reset_rankings: resetRankings,
        },
      }).unwrap();

      // Manually invalidate all caches after simulation to ensure data consistency
      // This includes tournaments so the home page completed count updates
      dispatch(rankingsApi.util.invalidateTags(['Ranking']));
      dispatch(fencersApi.util.invalidateTags(['Fencer']));
      dispatch(clubsApi.util.invalidateTags(['Club']));
      dispatch(tournamentsApi.util.invalidateTags(['Tournament']));

      setSuccess(`Season "${seasonName}" simulated successfully!`);
      setSimulationStats(result.statistics);
    } catch (err: any) {
      setError(err.data?.error || 'Failed to simulate season');
    }
  };

  const handleDeleteClick = (seasonId: number, seasonName: string) => {
    setSeasonToDelete({ id: seasonId, name: seasonName });
    setDeleteConfirmOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!seasonToDelete) return;

    try {
      setError(null);
      setSuccess(null);

      const result = await deleteSeason(seasonToDelete.id).unwrap();
      setSuccess(`${result.message}. ${result.tournaments_unlinked} tournaments were unlinked.`);
      setDeleteConfirmOpen(false);
      setSeasonToDelete(null);
    } catch (err: any) {
      setError(err.data?.error || 'Failed to delete season');
      setDeleteConfirmOpen(false);
    }
  };

  const handleResetRankings = async () => {
    if (!window.confirm('⚠️ This will reset ALL fencer rankings to zero. Are you sure?')) {
      return;
    }

    try {
      setError(null);
      setSuccess(null);
      
      const result = await resetAllRankings().unwrap();
      
      // Manually invalidate all caches to update all UI components
      // This ensures home page stats, club rankings, cumulative charts, etc. all refresh
      dispatch(rankingsApi.util.invalidateTags(['Ranking']));
      dispatch(fencersApi.util.invalidateTags(['Fencer']));
      dispatch(clubsApi.util.invalidateTags(['Club']));
      dispatch(tournamentsApi.util.invalidateTags(['Tournament']));
      
      setSuccess(`✅ ${result.message} (${result.rankings_reset} rankings reset)`);
    } catch (err: any) {
      setError(err.data?.error || 'Failed to reset rankings');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Active':
        return 'success';
      case 'Completed':
        return 'default';
      case 'Upcoming':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box>
            <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
              Season Simulation (DEV)
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Create and simulate fencing seasons with automated tournaments and results
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              color="error"
              onClick={handleResetRankings}
              disabled={resettingRankings}
            >
              {resettingRankings ? 'Resetting...' : 'Reset All Rankings'}
            </Button>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setOpenDialog(true)}
            >
              Create Season
            </Button>
          </Box>
        </Box>

        <Alert severity="warning" icon={<InfoIcon />}>
          <strong>Development Tool:</strong> This page is for testing and development purposes only.
          Season simulation will generate random tournaments and results.
        </Alert>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 2 }} icon={<SuccessIcon />}>
          {success}
        </Alert>
      )}

      {/* Simulation Statistics */}
      {simulationStats && (
        <Card sx={{ mb: 4, bgcolor: 'success.light', color: 'success.contrastText' }}>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
              Simulation Results
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2">Tournaments Created</Typography>
                <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                  {simulationStats.tournaments_created}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2">Total Results</Typography>
                <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                  {simulationStats.total_results}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2">Avg Participants</Typography>
                <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                  {simulationStats.avg_participants.toFixed(1)}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2">Season</Typography>
                <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                  {simulationStats.season_name}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Simulation Settings */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
            Simulation Settings
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Number of Tournaments"
                value={numTournaments}
                onChange={(e) => setNumTournaments(parseInt(e.target.value) || 100)}
                helperText="Number of tournaments to generate in the season"
                inputProps={{ min: 1, max: 500 }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={resetRankings}
                    onChange={(e) => setResetRankings(e.target.checked)}
                  />
                }
                label="Reset all rankings before simulation"
              />
              <Typography variant="caption" display="block" color="text.secondary">
                This will set all fencer rankings to 0 before generating results
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Seasons List */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
            All Seasons
          </Typography>
          <Divider sx={{ mb: 2 }} />

          {loadingSeasons ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : seasons && seasons.length > 0 ? (
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow sx={{ bgcolor: 'grey.100' }}>
                    <TableCell sx={{ fontWeight: 'bold' }}>Season Name</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Start Date</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>End Date</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Tournaments</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }} align="right">
                      Actions
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {seasons.map((season) => (
                    <TableRow key={season.season_id} hover>
                      <TableCell sx={{ fontWeight: 'medium' }}>{season.name}</TableCell>
                      <TableCell>{new Date(season.start_date).toLocaleDateString()}</TableCell>
                      <TableCell>{new Date(season.end_date).toLocaleDateString()}</TableCell>
                      <TableCell>
                        <Chip
                          label={season.status}
                          color={getStatusColor(season.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{season.tournament_count}</TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                          <Button
                            variant="contained"
                            size="small"
                            startIcon={simulating ? <CircularProgress size={16} /> : <SimulateIcon />}
                            onClick={() => handleSimulateSeason(season.season_id, season.name)}
                            disabled={simulating}
                          >
                            {simulating ? 'Simulating...' : 'Simulate'}
                          </Button>
                          <Button
                            variant="outlined"
                            color="error"
                            size="small"
                            startIcon={<DeleteIcon />}
                            onClick={() => handleDeleteClick(season.season_id, season.name)}
                            disabled={simulating}
                          >
                            Delete
                          </Button>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" color="text.secondary">
                No seasons found. Create a season to get started.
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Create Season Dialog */}
      <Dialog open={openDialog} onClose={() => { setOpenDialog(false); setDialogError(null); }} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Season</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            {dialogError && (
              <Alert severity="error" onClose={() => setDialogError(null)} sx={{ mb: 2 }}>
                {dialogError}
              </Alert>
            )}
            <TextField
              fullWidth
              label="Season Name"
              value={seasonName}
              onChange={(e) => setSeasonName(e.target.value)}
              placeholder="e.g., 2024-2025"
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              type="date"
              label="Start Date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              type="date"
              label="End Date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setOpenDialog(false); setDialogError(null); }}>Cancel</Button>
          <Button onClick={handleCreateSeason} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmOpen} onClose={() => setDeleteConfirmOpen(false)}>
        <DialogTitle>Delete Season?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the season <strong>"{seasonToDelete?.name}"</strong>?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            This will unlink all tournaments from this season, but tournaments will not be deleted.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirmOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} variant="contained" color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default SeasonSimulationPage;
