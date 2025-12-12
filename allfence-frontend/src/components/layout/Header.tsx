import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box, Chip } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { logout } from '../../store/slices/authSlice';

export const Header: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  return (
    <AppBar position="static" sx={{ bgcolor: '#1976d2' }}>
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            ⚔️ AllFence
          </Typography>
          {user && (
            <Chip
              label={user.is_admin ? '👑 Admin' : user.username}
              size="small"
              sx={{ bgcolor: user.is_admin ? '#ffd700' : 'rgba(255,255,255,0.2)', color: user.is_admin ? '#000' : '#fff' }}
            />
          )}
        </Box>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Button color="inherit" onClick={() => navigate('/')}>
            Home
          </Button>
          <Button color="inherit" onClick={() => navigate('/tournaments')}>
            Tournaments
          </Button>
          <Button color="inherit" onClick={() => navigate('/fencers')}>
            Fencers
          </Button>
          <Button color="inherit" onClick={() => navigate('/rankings')}>
            Rankings
          </Button>
          {isAuthenticated ? (
            <Button color="inherit" onClick={handleLogout} sx={{ ml: 2, border: '1px solid white' }}>
              Logout
            </Button>
          ) : (
            <Button color="inherit" onClick={() => navigate('/login')} sx={{ ml: 2, border: '1px solid white' }}>
              Login
            </Button>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
