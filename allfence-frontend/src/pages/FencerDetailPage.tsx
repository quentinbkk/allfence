import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Card,
  CardContent,
  Button,
  Typography,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Avatar,
  Chip,
} from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useGetFencerByIdQuery, useUpdateFencerMutation, useGetFencerResultsQuery, useGetFencerUpcomingTournamentsQuery } from '../api/fencers';
import { useGetClubsQuery } from '../api/clubs';
import { useAppSelector } from '../store/hooks';
import { LoadingSpinner, ErrorMessage } from '../components/common';
import { formatDate, getInitials } from '../utils/formatters';
import FencerEditDialog from '../components/forms/FencerEditDialog';

export const FencerDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const fencerId = parseInt(id || '0');
  const { user } = useAppSelector((state) => state.auth);
  const [dialogOpen, setDialogOpen] = useState(false);

  const { data: fencer, isLoading, error, refetch } = useGetFencerByIdQuery(fencerId);
  const { data: tournamentResults = [] } = useGetFencerResultsQuery(fencerId);
  const { data: upcomingTournaments = [] } = useGetFencerUpcomingTournamentsQuery(fencerId);
  const { data: clubs = [] } = useGetClubsQuery();
  const [updateFencer] = useUpdateFencerMutation();

  const handleUpdateFencer = async (data: any) => {
    await updateFencer({ id: fencerId, data }).unwrap();
    refetch();
  };

  if (isLoading) return <LoadingSpinner />;
  if (error || !fencer) return <ErrorMessage message="Failed to load fencer" onRetry={refetch} />;

  const totalPoints = fencer.rankings.reduce((sum, r) => sum + r.points, 0);

  // Prepare data for performance graph (chronological order with cumulative points)
  let cumulativePoints = 0;
  const performanceData = [...tournamentResults]
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .map((result, index) => {
      cumulativePoints += result.points_awarded;
      return {
        name: `T${index + 1}`, // Simple tournament numbering
        fullName: result.tournament_name,
        date: result.date,
        placement: result.placement,
        points: result.points_awarded,
        cumulativePoints: cumulativePoints,
      };
    });

  // Calculate Y-axis domain for cumulative points
  const maxPoints = Math.max(...performanceData.map(d => d.cumulativePoints), 100);

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Button onClick={() => navigate('/fencers')}>
          ← Back to Fencers
        </Button>
        {user?.is_admin && (
          <Button variant="contained" color="primary" onClick={() => setDialogOpen(true)}>
            ✏️ Edit Profile
          </Button>
        )}
      </Box>

      {/* Fencer Header */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 3, mb: 3 }}>
            <Avatar
              alt={fencer.full_name}
              sx={{ width: 120, height: 120, fontSize: '3rem' }}
            >
              {getInitials(fencer.full_name)}
            </Avatar>

            <Box sx={{ flex: 1 }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                {fencer.full_name}
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                ID: {fencer.fencer_id}
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                    Date of Birth
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 'semibold' }}>
                    {formatDate(fencer.dob)}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    ({fencer.age} years)
                  </Typography>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                    Gender
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 'semibold' }}>
                    {fencer.gender === 'M' ? 'Male' : 'Female'}
                  </Typography>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                    Weapon
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 'semibold' }}>
                    {fencer.weapon}
                  </Typography>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                    Club
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{
                      fontWeight: 'semibold',
                      color: 'primary.main',
                      cursor: 'pointer',
                      '&:hover': {
                        textDecoration: 'underline',
                      },
                    }}
                    onClick={() => navigate(`/clubs/${fencer.club_id}`)}
                  >
                    {fencer.club_name || fencer.club_id}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Rankings Section */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
            Rankings & Points
          </Typography>

          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Bracket</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Points</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {fencer.rankings.map((ranking) => (
                  <TableRow key={ranking.ranking_id}>
                    <TableCell>{ranking.bracket_name}</TableCell>
                    <TableCell sx={{ fontWeight: 'semibold' }}>{ranking.points}</TableCell>
                  </TableRow>
                ))}
                <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                  <TableCell sx={{ fontWeight: 'bold' }}>Total</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>{totalPoints}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Performance Graph */}
      {performanceData.length > 0 && (
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
              Performance Over Time
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={performanceData} margin={{ top: 20, right: 30, left: 20, bottom: 80 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="name" 
                  angle={-45}
                  textAnchor="end"
                  height={100}
                  interval={0}
                  tick={{ fontSize: 11 }}
                />
                <YAxis 
                  label={{ value: 'Cumulative Ranking Points', angle: -90, position: 'insideLeft' }}
                  domain={[0, maxPoints]}
                />
                <Tooltip 
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <Paper sx={{ p: 1.5, border: '1px solid #ccc' }}>
                          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                            {data.fullName}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            Date: {formatDate(data.date)}
                          </Typography>
                          <Typography variant="body2">
                            Placement: {data.placement}
                            {data.placement === 1 ? 'st' : data.placement === 2 ? 'nd' : data.placement === 3 ? 'rd' : 'th'}
                          </Typography>
                          <Typography variant="body2" color="primary">
                            Points Earned: +{data.points}
                          </Typography>
                          <Typography variant="body2" color="primary" sx={{ fontWeight: 'bold' }}>
                            Total Points: {data.cumulativePoints}
                          </Typography>
                        </Paper>
                      );
                    }
                    return null;
                  }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="cumulativePoints" 
                  stroke="#1976d2" 
                  strokeWidth={3}
                  dot={{ r: 6, fill: '#1976d2' }}
                  activeDot={{ r: 8 }}
                  name="Ranking Points"
                />
              </LineChart>
            </ResponsiveContainer>
            <Typography variant="caption" color="textSecondary" sx={{ display: 'block', textAlign: 'center', mt: 2 }}>
              Lower placement number = better result (1st place is the best)
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Upcoming Tournaments Section */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
            Upcoming Eligible Tournaments
          </Typography>

          {upcomingTournaments.length === 0 ? (
            <Typography color="textSecondary">No upcoming eligible tournaments</Typography>
          ) : (
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>Date</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Tournament</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Type</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Location</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {upcomingTournaments.map((tournament) => (
                    <TableRow 
                      key={tournament.tournament_id} 
                      hover
                      sx={{ cursor: 'pointer' }}
                      onClick={() => navigate(`/tournaments/${tournament.tournament_id}`)}
                    >
                      <TableCell>{formatDate(tournament.date)}</TableCell>
                      <TableCell sx={{ fontWeight: 'semibold' }}>{tournament.tournament_name}</TableCell>
                      <TableCell>{tournament.competition_type}</TableCell>
                      <TableCell>{tournament.location || 'TBD'}</TableCell>
                      <TableCell>
                        {tournament.is_registered ? (
                          <Chip label="Registered" color="success" size="small" />
                        ) : (
                          <Chip label="Not Registered" color="default" size="small" />
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Tournament History Section */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
            Tournament History
          </Typography>

          {tournamentResults.length === 0 ? (
            <Typography color="textSecondary">No tournament results recorded yet</Typography>
          ) : (
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>Date</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Tournament</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Type</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Placement</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Points Earned</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {tournamentResults.map((result) => (
                    <TableRow key={result.result_id} hover>
                      <TableCell>{formatDate(result.date)}</TableCell>
                      <TableCell sx={{ fontWeight: 'semibold' }}>{result.tournament_name}</TableCell>
                      <TableCell>{result.competition_type}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          {result.placement === 1 && '🥇'}
                          {result.placement === 2 && '🥈'}
                          {result.placement === 3 && '🥉'}
                          {result.placement}
                          {result.placement === 1 ? 'st' : result.placement === 2 ? 'nd' : result.placement === 3 ? 'rd' : 'th'}
                        </Box>
                      </TableCell>
                      <TableCell sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                        +{result.points_awarded}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      <FencerEditDialog
        open={dialogOpen}
        fencer={fencer}
        clubs={clubs}
        onClose={() => setDialogOpen(false)}
        onSubmit={handleUpdateFencer}
      />
    </Container>
  );
};

export default FencerDetailPage;
