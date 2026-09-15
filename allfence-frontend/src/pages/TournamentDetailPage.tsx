import React from 'react';
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
} from '@mui/material';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import { useGetTournamentByIdQuery, useGetTournamentParticipantsQuery } from '../api/tournaments';
import { useGetRankingsQuery } from '../api/rankings';
import { LoadingSpinner, ErrorMessage, StatusBadge } from '../components/common';
import { formatDate } from '../utils/formatters';
import { TournamentStatus } from '../types';

export const TournamentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const tournamentId = parseInt(id || '0');

  const { data: tournament, isLoading, error, refetch } = useGetTournamentByIdQuery(tournamentId);
  const { data: participants = [] } = useGetTournamentParticipantsQuery(tournamentId);
  const { data: rankings = [] } = useGetRankingsQuery({ bracket: tournament?.bracket || '' });

  if (isLoading) return <LoadingSpinner />;
  if (error || !tournament) return <ErrorMessage message="Failed to load tournament" onRetry={refetch} />;

  // Enrich participants with rankings
  const enrichedParticipants = participants.map(p => {
    const ranking = rankings.find(r => r.fencer_id === p.fencer_id);
    return {
      ...p,
      current_rank: ranking?.rank || null,
      total_points: ranking?.total_points || 0,
    };
  });

  // Sort by placement if completed, otherwise by ranking
  const sortedParticipants = [...enrichedParticipants].sort((a, b) => {
    if (tournament.status === TournamentStatus.COMPLETED) {
      // Sort by placement for completed tournaments
      if (a.placement && b.placement) return a.placement - b.placement;
      if (a.placement) return -1;
      if (b.placement) return 1;
    }
    // Sort by ranking for non-completed tournaments
    if (a.current_rank && b.current_rank) return a.current_rank - b.current_rank;
    if (a.current_rank) return -1;
    if (b.current_rank) return 1;
    return 0;
  });

  // Get top 3 for completed tournaments
  const hasResults = sortedParticipants.some(p => p.placement && p.placement > 0);
  const top3 = hasResults ? sortedParticipants.filter(p => p.placement && p.placement <= 3).slice(0, 3) : [];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Button onClick={() => navigate('/tournaments')} sx={{ mb: 3 }}>
        ← Back to Tournaments
      </Button>

      {/* Tournament Header */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
            <div>
              <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                {tournament.tournament_name}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Created: {tournament.created_at ? formatDate(tournament.created_at) : 'N/A'}
              </Typography>
            </div>
            <StatusBadge status={tournament.status} />
          </Box>

          <Grid container spacing={3} sx={{ mt: 2 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                Date
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 'semibold' }}>
                {formatDate(tournament.date)}
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                Weapon
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 'semibold' }}>
                {tournament.weapon}
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                Bracket
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 'semibold' }}>
                {tournament.bracket}
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                Competition Type
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 'semibold' }}>
                {tournament.competition_type}
              </Typography>
            </Grid>

            {tournament.location && (
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                  Location
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 'semibold' }}>
                  {tournament.location}
                </Typography>
              </Grid>
            )}

            {tournament.gender && (
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                  Gender
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 'semibold' }}>
                  {tournament.gender}
                </Typography>
              </Grid>
            )}
          </Grid>

          {tournament.description && (
            <Box sx={{ mt: 4, p: 2, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                Description
              </Typography>
              <Typography variant="body1">{tournament.description}</Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Podium Section - Only for completed tournaments with results */}
      {tournament.status === TournamentStatus.COMPLETED && top3.length > 0 && (
        <Card sx={{ mb: 4, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
          <CardContent>
            <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 4, color: 'white', textAlign: 'center' }}>
              🏆 Final Results - Top 3
            </Typography>

            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-end', gap: 3, mb: 2 }}>
              {/* Second Place */}
              {top3[1] && (
                <Box sx={{ textAlign: 'center', width: 180 }}>
                  <Box
                    sx={{
                      width: 120,
                      height: 120,
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, #C0C0C0 0%, #E8E8E8 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      margin: '0 auto 16px',
                      border: '4px solid white',
                      boxShadow: '0 8px 16px rgba(0,0,0,0.3)',
                    }}
                  >
                    <Typography variant="h3" sx={{ fontWeight: 'bold', color: '#666' }}>2</Typography>
                  </Box>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'white', mb: 0.5 }}>
                    {top3[1].full_name}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)', mb: 1 }}>
                    {top3[1].club_name || 'No Club'}
                  </Typography>
                  <Box sx={{
                    backgroundColor: 'rgba(255,255,255,0.2)',
                    borderRadius: 2,
                    padding: 1,
                    backdropFilter: 'blur(10px)'
                  }}>
                    <Typography variant="h5" sx={{ fontWeight: 'bold', color: 'white' }}>
                      {top3[1].points_awarded} pts
                    </Typography>
                  </Box>
                </Box>
              )}

              {/* First Place */}
              {top3[0] && (
                <Box sx={{ textAlign: 'center', width: 200, mb: 4 }}>
                  <EmojiEventsIcon sx={{ fontSize: 50, color: '#FFD700', mb: 1 }} />
                  <Box
                    sx={{
                      width: 150,
                      height: 150,
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      margin: '0 auto 16px',
                      border: '5px solid white',
                      boxShadow: '0 12px 24px rgba(0,0,0,0.4)',
                    }}
                  >
                    <Typography variant="h2" sx={{ fontWeight: 'bold', color: '#fff' }}>1</Typography>
                  </Box>
                  <Typography variant="h5" sx={{ fontWeight: 'bold', color: 'white', mb: 0.5 }}>
                    {top3[0].full_name}
                  </Typography>
                  <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.95)', mb: 1 }}>
                    {top3[0].club_name || 'No Club'}
                  </Typography>
                  <Box sx={{
                    backgroundColor: 'rgba(255,255,255,0.25)',
                    borderRadius: 2,
                    padding: 1.5,
                    backdropFilter: 'blur(10px)'
                  }}>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'white' }}>
                      {top3[0].points_awarded} pts
                    </Typography>
                  </Box>
                </Box>
              )}

              {/* Third Place */}
              {top3[2] && (
                <Box sx={{ textAlign: 'center', width: 180 }}>
                  <Box
                    sx={{
                      width: 110,
                      height: 110,
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, #CD7F32 0%, #E6A157 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      margin: '0 auto 16px',
                      border: '4px solid white',
                      boxShadow: '0 8px 16px rgba(0,0,0,0.3)',
                    }}
                  >
                    <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'white' }}>3</Typography>
                  </Box>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'white', mb: 0.5 }}>
                    {top3[2].full_name}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)', mb: 1 }}>
                    {top3[2].club_name || 'No Club'}
                  </Typography>
                  <Box sx={{
                    backgroundColor: 'rgba(255,255,255,0.2)',
                    borderRadius: 2,
                    padding: 1,
                    backdropFilter: 'blur(10px)'
                  }}>
                    <Typography variant="h5" sx={{ fontWeight: 'bold', color: 'white' }}>
                      {top3[2].points_awarded} pts
                    </Typography>
                  </Box>
                </Box>
              )}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Participants Section */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
              {tournament.status === TournamentStatus.COMPLETED && hasResults
                ? `All Results (${participants.length})`
                : `Registered Participants (${participants.length})`}
            </Typography>
          </Box>

          {participants.length === 0 ? (
            <Typography color="textSecondary">No participants registered yet</Typography>
          ) : (
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
                  <TableRow>
                    {tournament.status === TournamentStatus.COMPLETED && hasResults && (
                      <TableCell sx={{ fontWeight: 'bold', width: 80 }}>Place</TableCell>
                    )}
                    <TableCell sx={{ fontWeight: 'bold' }}>Name</TableCell>
                    <TableCell>Club</TableCell>
                    <TableCell>Weapon</TableCell>
                    {tournament.status !== TournamentStatus.COMPLETED && (
                      <TableCell sx={{ fontWeight: 'bold' }}>Initial Rank</TableCell>
                    )}
                    {(tournament.status === TournamentStatus.COMPLETED || hasResults) && (
                      <TableCell sx={{ fontWeight: 'bold' }}>Points Earned</TableCell>
                    )}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {sortedParticipants.map((participant) => {
                    const hasPlacement = participant.placement && participant.placement > 0;
                    const isTopThree = hasPlacement && participant.placement <= 3;

                    return (
                      <TableRow
                        key={participant.result_id}
                        hover
                        sx={{
                          backgroundColor: isTopThree
                            ? participant.placement === 1 ? 'rgba(255, 215, 0, 0.1)'
                            : participant.placement === 2 ? 'rgba(192, 192, 192, 0.1)'
                            : 'rgba(205, 127, 50, 0.1)'
                            : 'inherit'
                        }}
                      >
                        {tournament.status === TournamentStatus.COMPLETED && hasResults && (
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography sx={{
                                fontWeight: isTopThree ? 'bold' : 'semibold',
                                fontSize: isTopThree ? '1.1rem' : '1rem'
                              }}>
                                {hasPlacement ? participant.placement : '-'}
                              </Typography>
                              {participant.placement === 1 && <span style={{ fontSize: '1.2rem' }}>🥇</span>}
                              {participant.placement === 2 && <span style={{ fontSize: '1.2rem' }}>🥈</span>}
                              {participant.placement === 3 && <span style={{ fontSize: '1.2rem' }}>🥉</span>}
                            </Box>
                          </TableCell>
                        )}
                        <TableCell sx={{ fontWeight: 'semibold' }}>{participant.full_name}</TableCell>
                        <TableCell>{participant.club_name || 'N/A'}</TableCell>
                        <TableCell>{participant.weapon}</TableCell>
                        {tournament.status !== TournamentStatus.COMPLETED && (
                          <TableCell>
                            <Typography
                              sx={{
                                fontWeight: 'bold',
                                color: participant.current_rank ? 'primary.main' : 'text.secondary'
                              }}
                            >
                              {participant.current_rank ? `#${participant.current_rank}` : 'Unranked'}
                            </Typography>
                          </TableCell>
                        )}
                        {(tournament.status === TournamentStatus.COMPLETED || hasResults) && (
                          <TableCell>
                            <Typography sx={{
                              fontWeight: participant.points_awarded > 0 ? 'bold' : 'normal',
                              color: participant.points_awarded > 0 ? 'success.main' : 'text.secondary'
                            }}>
                              {participant.points_awarded || 0}
                            </Typography>
                          </TableCell>
                        )}
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>
    </Container>
  );
};

// Helper function for placement suffix
export function getPlacementSuffix(placement: number): string {
  const j = placement % 10;
  const k = placement % 100;
  if (j === 1 && k !== 11) return 'st';
  if (j === 2 && k !== 12) return 'nd';
  if (j === 3 && k !== 13) return 'rd';
  return 'th';
}

export default TournamentDetailPage;
