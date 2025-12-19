/**
 * Main Application Component
 * 
 * This is the root component that sets up:
 * - Redux store for state management
 * - Material-UI theming
 * - React Router for page navigation
 * - Authentication-based routing (protected vs public routes)
 * 
 * Route Structure:
 * - /login: Public login page (no authentication required)
 * - All other routes: Protected by ProtectedRoute component (requires authentication)
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { Provider } from 'react-redux';
import { store } from './store/store';
import AppLayout from './components/layout/AppLayout';
import TournamentsPage from './pages/TournamentsPage';
import TournamentDetailPage from './pages/TournamentDetailPage';
import FencersPage from './pages/FencersPage';
import FencerDetailPage from './pages/FencerDetailPage';
import RankingsPage from './pages/RankingsPage';
import RankingsProgressPage from './pages/RankingsProgressPage';
import ClubRankingsPage from './pages/ClubRankingsPage';
import ClubsPage from './pages/ClubsPage';
import ClubDetailPage from './pages/ClubDetailPage';
import SeasonSimulationPage from './pages/SeasonSimulationPage';
import DataStructurePage from './pages/DataStructurePage';
import HomePage from './pages/HomePage';
import NotFoundPage from './pages/NotFoundPage';
import './App.css';

// Material-UI theme configuration
const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },   // Blue primary color
    secondary: { main: '#dc004e' },  // Pink secondary color
  },
});

function App() {
  return (
    // Redux Provider wraps entire app to provide state management
    <Provider store={store}>
      {/* Material-UI theme provider for consistent styling */}
      <ThemeProvider theme={theme}>
        {/* React Router for client-side navigation */}
        <Router>
          <Routes>
            {/* All routes are now public - no authentication required */}
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
              
              {/* Development-only route (not shown in sidebar UI) */}
              <Route path="/dev/season-simulation" element={<SeasonSimulationPage />} />
              
              {/* Catch-all route for 404 Not Found */}
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </Router>
      </ThemeProvider>
    </Provider>
  );
}

export default App;
