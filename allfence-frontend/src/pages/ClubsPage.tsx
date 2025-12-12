import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  CircularProgress,
  Container,
  Grid,
  Typography,
  Alert,
  Chip,
  Stack,
} from '@mui/material';
import {
  SportsMartialArts,
  EmojiEvents,
  People,
} from '@mui/icons-material';
import { useGetClubsQuery } from '../api/clubs';

const ClubsPage: React.FC = () => {
  const navigate = useNavigate();
  const { data: clubs, isLoading, error } = useGetClubsQuery();

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container sx={{ py: 4 }}>
        <Alert severity="error">Failed to load clubs. Please try again later.</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
          Clubs
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Browse all fencing clubs and their statistics
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {clubs?.map((club) => (
          <Grid item xs={12} sm={6} md={4} key={club.club_id}>
            <Card
              sx={{
                height: '100%',
                cursor: 'pointer',
                transition: 'all 0.3s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 6,
                },
              }}
              onClick={() => navigate(`/clubs/${club.club_id}`)}
            >
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
                  {club.club_name}
                </Typography>

                <Stack spacing={2}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <People color="action" />
                    <Typography variant="body2" color="text.secondary">
                      <strong>{club.fencer_count}</strong> fencers
                    </Typography>
                  </Box>

                  {club.weapon_club && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <SportsMartialArts color="action" />
                      <Typography variant="body2" color="text.secondary">
                        Primary weapon: <strong>{club.weapon_club}</strong>
                      </Typography>
                    </Box>
                  )}

                  {club.start_year && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <EmojiEvents color="action" />
                      <Typography variant="body2" color="text.secondary">
                        Founded: <strong>{club.start_year}</strong>
                      </Typography>
                    </Box>
                  )}

                  <Box sx={{ mt: 2 }}>
                    <Chip
                      label={club.status}
                      color={club.status === 'Active' ? 'success' : 'default'}
                      size="small"
                    />
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {clubs?.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="text.secondary">
            No clubs found
          </Typography>
        </Box>
      )}
    </Container>
  );
};

export default ClubsPage;
