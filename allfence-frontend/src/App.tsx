/**
 * Main Application Component
 *
 * This is the root component that sets up:
 * - Redux store for state management
 * - Material-UI theming
 * - React Router for page navigation
 *
 * This is a public, read-only demo - all routes are open and every page is
 * lazy-loaded so the initial bundle only ships the code a visitor's first
 * page actually needs.
 */

import { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { Provider } from 'react-redux';
import { Box, CircularProgress } from '@mui/material';
import { store } from './store/store';
import AppLayout from './components/layout/AppLayout';
import './App.css';

const TournamentsPage = lazy(() => import('./pages/TournamentsPage'));
const TournamentDetailPage = lazy(() => import('./pages/TournamentDetailPage'));
const FencersPage = lazy(() => import('./pages/FencersPage'));
const FencerDetailPage = lazy(() => import('./pages/FencerDetailPage'));
const RankingsPage = lazy(() => import('./pages/RankingsPage'));
const RankingsProgressPage = lazy(() => import('./pages/RankingsProgressPage'));
const ClubRankingsPage = lazy(() => import('./pages/ClubRankingsPage'));
const ClubsPage = lazy(() => import('./pages/ClubsPage'));
const ClubDetailPage = lazy(() => import('./pages/ClubDetailPage'));
const DataStructurePage = lazy(() => import('./pages/DataStructurePage'));
const HomePage = lazy(() => import('./pages/HomePage'));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));

// Material-UI theme configuration
const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },   // Blue primary color
    secondary: { main: '#dc004e' },  // Pink secondary color
  },
});

const PageFallback = () => (
  <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
    <CircularProgress />
  </Box>
);

function App() {
  return (
    // Redux Provider wraps entire app to provide state management
    <Provider store={store}>
      {/* Material-UI theme provider for consistent styling */}
      <ThemeProvider theme={theme}>
        {/* React Router for client-side navigation */}
        <Router>
          <Suspense fallback={<PageFallback />}>
            <Routes>
              <Route element={<AppLayout />}>
                {/* Main application pages */}
                <Route path="/" element={<HomePage />} />
                <Route path="/home" element={<HomePage />} />
                <Route path="/tournaments" element={<TournamentsPage />} />
                <Route path="/tournaments/:id" element={<TournamentDetailPage />} />
                <Route path="/fencers" element={<FencersPage />} />
                <Route path="/fencers/:id" element={<FencerDetailPage />} />
                <Route path="/rankings" element={<RankingsPage />} />
                <Route path="/rankings/progress" element={<RankingsProgressPage />} />
                <Route path="/rankings/clubs" element={<ClubRankingsPage />} />
                <Route path="/clubs" element={<ClubsPage />} />
                <Route path="/clubs/:id" element={<ClubDetailPage />} />
                <Route path="/data-structure" element={<DataStructurePage />} />

                {/* Catch-all route for 404 Not Found */}
                <Route path="*" element={<NotFoundPage />} />
              </Route>
            </Routes>
          </Suspense>
        </Router>
      </ThemeProvider>
    </Provider>
  );
}

export default App;
