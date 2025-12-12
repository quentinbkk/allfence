import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Button,
  Paper,
  Divider,
  Avatar,
  LinearProgress,
} from '@mui/material';
import {
  EmojiEvents as TournamentIcon,
  People as FencersIcon,
  Groups as ClubsIcon,
  SportsMartialArts as RankingsIcon,
  Science as SimulationIcon,
  EmojiEventsOutlined as ClubRankingsIcon,
  ArrowForward as ArrowIcon,
} from '@mui/icons-material';
import { useGetTournamentsQuery } from '../api/tournaments';
import { useGetFencersQuery } from '../api/fencers';
import { useGetClubsQuery } from '../api/clubs';
import { TournamentStatus, ClubStatus } from '../types';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  
  // Fetch data for statistics
  const { data: tournaments, isLoading: loadingTournaments } = useGetTournamentsQuery({});
  const { data: fencers, isLoading: loadingFencers } = useGetFencersQuery({});
  const { data: clubs, isLoading: loadingClubs } = useGetClubsQuery();

  // Calculate statistics
  const completedTournaments = tournaments?.filter(t => t.status === TournamentStatus.COMPLETED).length || 0;
  const upcomingTournaments = tournaments?.filter(t => t.status === TournamentStatus.UPCOMING || t.status === TournamentStatus.REGISTRATION_OPEN).length || 0;
  const activeFencers = fencers?.length || 0;
  const activeClubs = clubs?.filter(c => c.status === ClubStatus.ACTIVE).length || 0;

  // Quick action cards
  const quickActions = [
    {
      title: 'View Tournaments',
      description: 'Browse all fencing competitions',
      icon: <TournamentIcon sx={{ fontSize: 48 }} />,
      color: '#1976d2',
      path: '/tournaments',
      stat: `${completedTournaments} Completed`,
    },
    {
      title: 'Fencer Rankings',
      description: 'Check current rankings by bracket',
      icon: <RankingsIcon sx={{ fontSize: 48 }} />,
      color: '#2e7d32',
      path: '/rankings',
      stat: `${activeFencers} Fencers`,
    },
    {
      title: 'Club Rankings',
      description: 'View club standings by weapon',
      icon: <ClubRankingsIcon sx={{ fontSize: 48 }} />,
      color: '#ed6c02',
      path: '/rankings/clubs',
      stat: `${activeClubs} Active Clubs`,
    },
    {
      title: 'Explore Fencers',
      description: 'Search and filter fencer profiles',
      icon: <FencersIcon sx={{ fontSize: 48 }} />,
      color: '#9c27b0',
      path: '/fencers',
      stat: 'Full Database',
    },
    {
      title: 'Browse Clubs',
      description: 'Discover club information',
      icon: <ClubsIcon sx={{ fontSize: 48 }} />,
      color: '#d32f2f',
      path: '/clubs',
      stat: 'With Statistics',
    },
    {
      title: 'Data Structure',
      description: 'View system architecture',
      icon: <SimulationIcon sx={{ fontSize: 48 }} />,
      color: '#0288d1',
      path: '/data-structure',
      stat: 'Academic Info',
    },
  ];

  // Weapon disciplines
  const weaponStats = [
    { weapon: 'Sabre', color: '#FF6B6B', count: fencers?.filter(f => f.weapon === 'Sabre').length || 0 },
    { weapon: 'Foil', color: '#4ECDC4', count: fencers?.filter(f => f.weapon === 'Foil').length || 0 },
    { weapon: 'Epee', color: '#95E1D3', count: fencers?.filter(f => f.weapon === 'Epee').length || 0 },
  ];

  const totalFencers = weaponStats.reduce((sum, w) => sum + w.count, 0);

  const isLoading = loadingTournaments || loadingFencers || loadingClubs;

  return (
    <Box sx={{ bgcolor: '#f5f7fa', minHeight: '100vh', py: 4 }}>
      <Container maxWidth="xl">
        {/* Hero Section */}
        <Paper
          sx={{
            p: 4,
            mb: 4,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            borderRadius: 2,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
            <Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold', mb: 1 }}>
                Welcome to AllFence
              </Typography>
              <Typography variant="h6" sx={{ opacity: 0.9, mb: 2 }}>
                Your comprehensive fencing management and ranking system
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  size="large"
                  endIcon={<ArrowIcon />}
                  onClick={() => navigate('/tournaments')}
                  sx={{
                    bgcolor: 'white',
                    color: '#667eea',
                    '&:hover': { bgcolor: '#f5f5f5' },
                    fontWeight: 'bold',
                  }}
                >
                  View Tournaments
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={() => navigate('/rankings')}
                  sx={{
                    borderColor: 'white',
                    color: 'white',
                    '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.1)' },
                  }}
                >
                  Check Rankings
                </Button>
              </Box>
            </Box>
            <Box
              sx={{
                width: 120,
                height: 120,
                bgcolor: 'rgba(255,255,255,0.2)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <svg
                width="80"
                height="80"
                viewBox="0 0 24 24"
                fill="white"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path d="M6.5 18c.828 0 1.5.672 1.5 1.5S7.328 21 6.5 21 5 20.328 5 19.5 5.672 18 6.5 18zm13-11c.828 0 1.5.672 1.5 1.5S20.328 10 19.5 10 18 9.328 18 8.5 18.672 7 19.5 7zM2 20l5.5-5.5L9 16l3-3 3.5 1.5L21 8.5l-1-1-5 5-3.5-1.5-3 3L7 12.5 2 18v2z" />
                <path d="M18.5 4c-.828 0-1.5.672-1.5 1.5s.672 1.5 1.5 1.5 1.5-.672 1.5-1.5S19.328 4 18.5 4zM8 13c-.828 0-1.5.672-1.5 1.5S7.172 16 8 16s1.5-.672 1.5-1.5S8.828 13 8 13z" />
              </svg>
            </Box>
          </Box>
        </Paper>

        {/* Statistics Overview */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                      {isLoading ? '...' : completedTournaments}
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      Completed Tournaments
                    </Typography>
                  </Box>
                  <TournamentIcon sx={{ fontSize: 48, opacity: 0.8 }} />
                </Box>
                {!isLoading && upcomingTournaments > 0 && (
                  <Typography variant="caption" sx={{ mt: 1, display: 'block', opacity: 0.8 }}>
                    +{upcomingTournaments} upcoming
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                      {isLoading ? '...' : activeFencers}
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      Active Fencers
                    </Typography>
                  </Box>
                  <FencersIcon sx={{ fontSize: 48, opacity: 0.8 }} />
                </Box>
                <Typography variant="caption" sx={{ mt: 1, display: 'block', opacity: 0.8 }}>
                  Across all disciplines
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                      {isLoading ? '...' : activeClubs}
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      Active Clubs
                    </Typography>
                  </Box>
                  <ClubsIcon sx={{ fontSize: 48, opacity: 0.8 }} />
                </Box>
                <Typography variant="caption" sx={{ mt: 1, display: 'block', opacity: 0.8 }}>
                  Competing nationwide
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', color: 'white' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                      3
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      Weapon Disciplines
                    </Typography>
                  </Box>
                  <RankingsIcon sx={{ fontSize: 48, opacity: 0.8 }} />
                </Box>
                <Typography variant="caption" sx={{ mt: 1, display: 'block', opacity: 0.8 }}>
                  Sabre, Foil, Epee
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Weapon Distribution */}
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 3 }}>
            Fencer Distribution by Weapon
          </Typography>
          <Grid container spacing={2}>
            {weaponStats.map((weapon) => (
              <Grid item xs={12} md={4} key={weapon.weapon}>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body1" sx={{ fontWeight: 'bold', color: weapon.color }}>
                      {weapon.weapon}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {weapon.count} fencers ({totalFencers > 0 ? ((weapon.count / totalFencers) * 100).toFixed(1) : 0}%)
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={totalFencers > 0 ? (weapon.count / totalFencers) * 100 : 0}
                    sx={{
                      height: 10,
                      borderRadius: 5,
                      bgcolor: '#e0e0e0',
                      '& .MuiLinearProgress-bar': {
                        bgcolor: weapon.color,
                      },
                    }}
                  />
                </Box>
              </Grid>
            ))}
          </Grid>
        </Paper>

        {/* Quick Actions */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 3 }}>
            Quick Access
          </Typography>
          <Grid container spacing={3}>
            {quickActions.map((action, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card
                  sx={{
                    height: '100%',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 6,
                    },
                  }}
                >
                  <CardActionArea onClick={() => navigate(action.path)} sx={{ height: '100%' }}>
                    <CardContent sx={{ textAlign: 'center', py: 4 }}>
                      <Avatar
                        sx={{
                          width: 72,
                          height: 72,
                          bgcolor: action.color,
                          margin: '0 auto',
                          mb: 2,
                        }}
                      >
                        {action.icon}
                      </Avatar>
                      <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
                        {action.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {action.description}
                      </Typography>
                      <Divider sx={{ my: 1 }} />
                      <Typography variant="caption" sx={{ color: action.color, fontWeight: 'bold' }}>
                        {action.stat}
                      </Typography>
                    </CardContent>
                  </CardActionArea>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* About Section */}
        <Paper sx={{ p: 4, bgcolor: '#fafafa' }}>
          <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 2 }}>
            About AllFence
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1, color: '#667eea' }}>
                Track Performance
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Monitor fencer progress throughout the season with detailed rankings, tournament results, and performance analytics.
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1, color: '#667eea' }}>
                Manage Data
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Comprehensive database of clubs, fencers, and tournaments with powerful filtering and search capabilities.
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1, color: '#667eea' }}>
                Visualize Insights
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Interactive charts and graphs showing rankings evolution, cumulative points, and competitive trends.
              </Typography>
            </Grid>
          </Grid>
          <Divider sx={{ my: 3 }} />
          <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
            Information Organization and Retrieval - Final Project
          </Typography>
        </Paper>
      </Container>
    </Box>
  );
};

export default HomePage;
