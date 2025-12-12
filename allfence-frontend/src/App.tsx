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
import LoginPage from './pages/LoginPage';
import NotFoundPage from './pages/NotFoundPage';
import './App.css';

const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
  },
});

function App() {
  return (
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <Router>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<AppLayout />}>
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
              <Route path="/dev/season-simulation" element={<SeasonSimulationPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </Router>
      </ThemeProvider>
    </Provider>
  );
}

export default App;
