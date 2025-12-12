import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  Chip,
  Card,
  CardContent,
} from '@mui/material';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import { useGetClubRankingsQuery, useGetAllClubsCumulativePointsQuery } from '../api/rankings';
import { WeaponType } from '../types';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const CHART_COLORS = [
  '#8884d8',
  '#82ca9d',
  '#ffc658',
  '#ff8042',
  '#a4de6c',
  '#d0ed57',
  '#83a6ed',
  '#8dd1e1',
  '#d084d0',
  '#ffbb28',
];

const ClubRankingsPage: React.FC = () => {
  const [selectedWeapon, setSelectedWeapon] = useState<WeaponType>(WeaponType.SABRE);

  const { data: rankings, isLoading, error } = useGetClubRankingsQuery({
    weapon: selectedWeapon,
  });

  const { data: cumulativeData, isLoading: isLoadingCumulative } = useGetAllClubsCumulativePointsQuery({
    weapon: selectedWeapon,
  });

  const handleWeaponChange = (_event: React.SyntheticEvent, newValue: WeaponType) => {
    setSelectedWeapon(newValue);
  };

  const getMedalColor = (rank: number): string => {
    switch (rank) {
      case 1:
        return '#FFD700'; // Gold
      case 2:
        return '#C0C0C0'; // Silver
      case 3:
        return '#CD7F32'; // Bronze
      default:
        return 'transparent';
    }
  };

  const getMedalEmoji = (rank: number): string => {
    switch (rank) {
      case 1:
        return '🥇';
      case 2:
        return '🥈';
      case 3:
        return '🥉';
      default:
        return '';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <EmojiEventsIcon fontSize="large" />
        Club Rankings
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        View rankings of clubs based on total points earned by their fencers in each weapon category
      </Typography>

      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={selectedWeapon}
          onChange={handleWeaponChange}
          variant="fullWidth"
          sx={{
            borderBottom: 1,
            borderColor: 'divider',
          }}
        >
          <Tab label="Sabre" value={WeaponType.SABRE} />
          <Tab label="Foil" value={WeaponType.FOIL} />
          <Tab label="Epee" value={WeaponType.EPEE} />
        </Tabs>

        <Box sx={{ p: 3 }}>
          {isLoading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              Error loading club rankings. Please try again.
            </Alert>
          )}

          {rankings && rankings.length === 0 && (
            <Alert severity="info">
              No club rankings available for {selectedWeapon} yet.
            </Alert>
          )}

          {rankings && rankings.length > 0 && (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell width="80px">
                      <strong>Rank</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Club Name</strong>
                    </TableCell>
                    <TableCell align="center">
                      <strong>Specialization</strong>
                    </TableCell>
                    <TableCell align="right">
                      <strong>Total Points</strong>
                    </TableCell>
                    <TableCell align="right">
                      <strong>Fencers</strong>
                    </TableCell>
                    <TableCell align="right">
                      <strong>Avg Points/Fencer</strong>
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {rankings.map((clubRank) => (
                    <TableRow
                      key={clubRank.club_id}
                      sx={{
                        backgroundColor: getMedalColor(clubRank.rank),
                        '&:hover': {
                          backgroundColor:
                            clubRank.rank <= 3
                              ? getMedalColor(clubRank.rank)
                              : 'action.hover',
                        },
                      }}
                    >
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="h6" component="span">
                            {clubRank.rank}
                          </Typography>
                          {clubRank.rank <= 3 && (
                            <Typography variant="h6" component="span">
                              {getMedalEmoji(clubRank.rank)}
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body1" fontWeight={clubRank.rank <= 3 ? 600 : 400}>
                          {clubRank.club_name}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Chip
                          label={clubRank.weapon_specialization}
                          size="small"
                          color={
                            clubRank.weapon_specialization === selectedWeapon
                              ? 'primary'
                              : 'default'
                          }
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Typography
                          variant="body1"
                          fontWeight={clubRank.rank <= 3 ? 600 : 400}
                          color="primary"
                        >
                          {clubRank.total_points.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="text.secondary">
                          {clubRank.fencer_count}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="text.secondary">
                          {clubRank.avg_points.toFixed(1)}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Box>
      </Paper>

      {/* Cumulative Points Over Time Chart */}
      {!isLoadingCumulative && cumulativeData && cumulativeData.length > 0 && (() => {
        // Merge all club data into a unified timeline
        const dateMap = new Map<string, any>();
        
        // Collect all unique dates and initialize with date property
        cumulativeData.forEach(club => {
          club.data.forEach(point => {
            if (!dateMap.has(point.date)) {
              dateMap.set(point.date, { date: point.date });
            }
          });
        });
        
        // Add each club's cumulative points to their respective dates
        cumulativeData.forEach(club => {
          let lastValue = 0;
          const sortedDates = Array.from(dateMap.keys()).sort();
          
          sortedDates.forEach(date => {
            const dataPoint = club.data.find(p => p.date === date);
            if (dataPoint) {
              lastValue = dataPoint.cumulative_points;
            }
            // Carry forward the last known value for continuity
            dateMap.get(date)![club.club_name] = lastValue;
          });
        });
        
        // Convert to array and sort by date
        const mergedData = Array.from(dateMap.values()).sort((a, b) => 
          a.date.localeCompare(b.date)
        );
        
        return (
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingUpIcon />
                Club Rankings Over Time - {selectedWeapon}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Cumulative points progression throughout the season
              </Typography>

              <ResponsiveContainer width="100%" height={500}>
                <LineChart data={mergedData} margin={{ top: 5, right: 30, left: 20, bottom: 80 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 11 }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis
                    label={{ value: 'Cumulative Points', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const sortedPayload = [...payload]
                          .filter((p: any) => p.value > 0)
                          .sort((a: any, b: any) => (b.value as number) - (a.value as number));
                        return (
                          <Paper sx={{ p: 2 }}>
                            <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
                              {payload[0].payload.date}
                            </Typography>
                            {sortedPayload.map((entry: any, index: number) => (
                              <Typography
                                key={index}
                                variant="body2"
                                sx={{ color: entry.color }}
                              >
                                {entry.name}: {(entry.value as number).toFixed(0)} pts
                              </Typography>
                            ))}
                          </Paper>
                        );
                      }
                      return null;
                    }}
                  />
                  <Legend
                    wrapperStyle={{ paddingTop: '20px' }}
                    iconType="line"
                  />
                  {cumulativeData.map((club, index) => (
                    <Line
                      key={club.club_id}
                      type="monotone"
                      dataKey={club.club_name}
                      stroke={CHART_COLORS[index % CHART_COLORS.length]}
                      strokeWidth={2}
                      dot={{ r: 3 }}
                      activeDot={{ r: 5 }}
                      name={club.club_name}
                      connectNulls
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        );
      })()}
    </Box>
  );
};

export default ClubRankingsPage;
