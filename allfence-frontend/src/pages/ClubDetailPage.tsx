import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Container,
  Grid,
  Typography,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Divider,
} from '@mui/material';
import {
  ArrowBack,
  People,
  EmojiEvents,
  TrendingUp,
  SportsMartialArts,
} from '@mui/icons-material';
import { useGetClubByIdQuery, useGetClubCumulativePointsQuery } from '../api/clubs';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, LineChart, Line, XAxis, YAxis, CartesianGrid } from 'recharts';

const WEAPON_COLORS = {
  Sabre: '#FF6B6B',
  Foil: '#4ECDC4',
  Epee: '#95E1D3',
};

const BRACKET_COLORS = [
  '#FF6B6B',
  '#4ECDC4',
  '#95E1D3',
  '#FFA07A',
  '#98D8C8',
  '#F7DC6F',
  '#BB8FCE',
];

const ClubDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: club, isLoading, error } = useGetClubByIdQuery(id!);
  const { data: cumulativePointsData, isLoading: isLoadingPoints } = useGetClubCumulativePointsQuery(id!);

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !club) {
    return (
      <Container sx={{ py: 4 }}>
        <Alert severity="error">Failed to load club details. Please try again later.</Alert>
        <Button onClick={() => navigate('/clubs')} sx={{ mt: 2 }}>
          Back to Clubs
        </Button>
      </Container>
    );
  }

  // Prepare bracket distribution data for pie chart
  const bracketData = club.bracket_distribution
    ? Object.entries(club.bracket_distribution)
        .map(([bracket, count]) => ({
          name: bracket,
          value: count,
        }))
        .sort((a, b) => {
          // Sort by age bracket order
          const order = ['U11', 'U13', 'U15', 'Cadet', 'Junior', 'Senior'];
          return order.indexOf(a.name) - order.indexOf(b.name);
        })
    : [];

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate('/clubs')}
          sx={{ mb: 2 }}
        >
          Back to Clubs
        </Button>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
            {club.club_name}
          </Typography>
          <Chip
            label={club.status}
            color={club.status === 'Active' ? 'success' : 'default'}
          />
        </Box>

        <Typography variant="body1" color="text.secondary">
          Club ID: {club.club_id}
          {club.start_year && ` • Founded in ${club.start_year}`}
          {club.weapon_club && ` • Primary weapon: ${club.weapon_club}`}
        </Typography>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <People sx={{ fontSize: 40, color: 'primary.main' }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {club.fencer_count}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Fencers
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <EmojiEvents sx={{ fontSize: 40, color: 'warning.main' }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {club.total_points?.toFixed(1) || '0'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Points
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <TrendingUp sx={{ fontSize: 40, color: 'success.main' }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {club.fencer_count > 0
                      ? ((club.total_points || 0) / club.fencer_count).toFixed(1)
                      : '0'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg Points/Fencer
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <SportsMartialArts sx={{ fontSize: 40, color: 'info.main' }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {club.weapon_club || 'Mixed'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Specialization
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Distribution Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Bracket Distribution Pie Chart */}
        {bracketData.length > 0 && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
                  Bracket Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={bracketData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {bracketData.map((entry, index) => (
                        <Cell
                          key={`cell-${entry.name}`}
                          fill={BRACKET_COLORS[index % BRACKET_COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Cumulative Points Over Season */}
        {!isLoadingPoints && cumulativePointsData && cumulativePointsData.length > 0 && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
                  Cumulative Points Over Time
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={cumulativePointsData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="date"
                      label={{ value: 'Tournament Date', position: 'insideBottom', offset: -5 }}
                      tick={{ fontSize: 10 }}
                      angle={-45}
                      textAnchor="end"
                      height={60}
                    />
                    <YAxis
                      label={{ value: 'Cumulative Points', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const data = payload[0].payload;
                          return (
                            <Paper sx={{ p: 1 }}>
                              <Typography variant="body2">
                                <strong>{data.tournament_name}</strong>
                              </Typography>
                              <Typography variant="body2">
                                Date: {data.date}
                              </Typography>
                              <Typography variant="body2">
                                Points Earned: {data.points_earned.toFixed(1)}
                              </Typography>
                              <Typography variant="body2">
                                <strong>Cumulative: {data.cumulative_points.toFixed(1)} pts</strong>
                              </Typography>
                            </Paper>
                          );
                        }
                        return null;
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="cumulative_points"
                      stroke="#8884d8"
                      strokeWidth={2}
                      dot={{ r: 3 }}
                      activeDot={{ r: 5 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* Member List */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
            Club Members ({club.members?.length || 0})
          </Typography>
          <Divider sx={{ mb: 2 }} />

          {club.members && club.members.length > 0 ? (
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow sx={{ bgcolor: 'grey.100' }}>
                    <TableCell sx={{ fontWeight: 'bold' }}>Rank</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Name</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Gender</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Weapon</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Brackets</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }} align="right">
                      Total Points
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {club.members.map((member, index) => (
                    <TableRow
                      key={member.fencer_id}
                      hover
                      sx={{
                        cursor: 'pointer',
                        '&:hover': { bgcolor: 'action.hover' },
                      }}
                      onClick={() => navigate(`/fencers/${member.fencer_id}`)}
                    >
                      <TableCell>
                        <Chip
                          label={`#${index + 1}`}
                          size="small"
                          color={index === 0 ? 'primary' : 'default'}
                        />
                      </TableCell>
                      <TableCell sx={{ fontWeight: 'medium' }}>
                        {member.full_name}
                      </TableCell>
                      <TableCell>
                        {member.gender === 'M' ? 'Male' : member.gender === 'F' ? 'Female' : member.gender}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={member.weapon}
                          size="small"
                          sx={{
                            bgcolor: WEAPON_COLORS[member.weapon as keyof typeof WEAPON_COLORS] || '#999',
                            color: 'white',
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        {member.brackets.join(', ')}
                      </TableCell>
                      <TableCell align="right" sx={{ fontWeight: 'bold' }}>
                        {member.total_points.toFixed(1)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" color="text.secondary">
                No members found in this club
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Container>
  );
};

export default ClubDetailPage;
