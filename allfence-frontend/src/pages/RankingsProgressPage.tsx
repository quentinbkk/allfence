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
  Paper,
  IconButton,
} from '@mui/material';
import { ArrowBack } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useGetTopFencersCumulativePointsQuery } from '../api/rankings';
import { LoadingSpinner, ErrorMessage } from '../components/common';
import { BRACKET_CHOICES, WEAPON_CHOICES } from '../utils/constants';
import { AgeBracket, WeaponType } from '../types';

// Color palette for the lines
const COLORS = [
  '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
  '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
];

export const RankingsProgressPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedBracket, setSelectedBracket] = useState<AgeBracket>(AgeBracket.SENIOR);
  const [selectedWeapon, setSelectedWeapon] = useState<WeaponType | ''>('');

  // Fetch cumulative points data for top 10 fencers
  const { data: fencersData = [], isLoading, error, refetch } = useGetTopFencersCumulativePointsQuery({
    bracket: selectedBracket,
    weapon: selectedWeapon || undefined,
    limit: 10,
  });

  // Transform data for recharts format
  // We need to create a unified date array and map each fencer's cumulative points
  const transformedData = React.useMemo(() => {
    if (!fencersData.length) return [];

    // Collect all unique dates from all fencers
    const allDatesSet = new Set<string>();
    fencersData.forEach(fencer => {
      fencer.data.forEach(point => {
        if (point.date) allDatesSet.add(point.date);
      });
    });

    // Sort dates
    const allDates = Array.from(allDatesSet).sort();

    // Create data points for each date
    return allDates.map(date => {
      const dataPoint: any = { date };

      // For each fencer, find their cumulative points at this date
      fencersData.forEach(fencer => {
        // Find the last data point on or before this date
        const relevantPoints = fencer.data.filter(p => p.date && p.date <= date);
        const cumulativePoints = relevantPoints.length > 0
          ? relevantPoints[relevantPoints.length - 1].cumulative_points
          : 0;
        
        dataPoint[fencer.fencer_name] = cumulativePoints;
      });

      return dataPoint;
    });
  }, [fencersData]);

  // Format date for display
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message="Failed to load rankings progress data" onRetry={refetch} />;

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
        <IconButton onClick={() => navigate('/rankings')} sx={{ color: 'primary.main' }}>
          <ArrowBack />
        </IconButton>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          📈 Rankings Progress Over Time
        </Typography>
      </Box>
      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 4, ml: 7 }}>
        Cumulative points for top 10 fencers
      </Typography>

      {/* Filters Card */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
            Filters
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Bracket</InputLabel>
                <Select
                  value={selectedBracket}
                  onChange={(e) => setSelectedBracket(e.target.value as AgeBracket)}
                  label="Bracket"
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
          </Grid>
        </CardContent>
      </Card>

      {/* Chart */}
      <Paper sx={{ p: 3 }}>
        {fencersData.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <Typography variant="h6" color="text.secondary">
              No data available for the selected filters
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Try selecting a different bracket or weapon
            </Typography>
          </Box>
        ) : (
          <>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
              Cumulative Points Progress
            </Typography>
            <ResponsiveContainer width="100%" height={500}>
              <LineChart
                data={transformedData}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  tickFormatter={formatDate}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis
                  label={{ value: 'Cumulative Points', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip
                  labelFormatter={formatDate}
                  formatter={(value: number) => [`${value} pts`, '']}
                />
                <Legend
                  wrapperStyle={{ paddingTop: '20px' }}
                  iconType="line"
                />
                {fencersData.map((fencer, index) => (
                  <Line
                    key={fencer.fencer_id}
                    type="monotone"
                    dataKey={fencer.fencer_name}
                    stroke={COLORS[index % COLORS.length]}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    activeDot={{ r: 5 }}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>

            {/* Legend with current standings */}
            <Box sx={{ mt: 4 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                Current Standings
              </Typography>
              <Grid container spacing={2}>
                {fencersData.map((fencer, index) => (
                  <Grid item xs={12} sm={6} md={4} key={fencer.fencer_id}>
                    <Card sx={{ borderLeft: `4px solid ${COLORS[index % COLORS.length]}` }}>
                      <CardContent>
                        <Typography variant="subtitle2" color="text.secondary">
                          #{index + 1}
                        </Typography>
                        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                          {fencer.fencer_name}
                        </Typography>
                        <Typography variant="h5" sx={{ color: COLORS[index % COLORS.length], fontWeight: 'bold' }}>
                          {fencer.current_points} pts
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {fencer.data.length} tournaments
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          </>
        )}
      </Paper>
    </Container>
  );
};

export default RankingsProgressPage;
