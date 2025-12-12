import React from 'react';
import { Box, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Typography, Divider } from '@mui/material';
import {
  EmojiEvents as TournamentIcon,
  People as FencersIcon,
  LeaderboardOutlined as RankingsIcon,
  Groups as ClubsIcon,
  Science as DevIcon,
  EmojiEventsOutlined as ClubRankingsIcon,
  AccountTree as DataStructureIcon,
  Home as HomeIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

export const Sidebar: React.FC = () => {
  const navigate = useNavigate();

  const menuItems = [
    { label: 'Home', icon: <HomeIcon />, path: '/' },
    { label: 'Tournaments', icon: <TournamentIcon />, path: '/tournaments' },
    { label: 'Fencers', icon: <FencersIcon />, path: '/fencers' },
    { label: 'Rankings', icon: <RankingsIcon />, path: '/rankings' },
    { label: 'Club Rankings', icon: <ClubRankingsIcon />, path: '/rankings/clubs' },
    { label: 'Clubs', icon: <ClubsIcon />, path: '/clubs' },
    { label: 'Data Structure', icon: <DataStructureIcon />, path: '/data-structure' },
  ];

  const devMenuItems = [
    { label: 'Season Simulation', icon: <DevIcon />, path: '/dev/season-simulation' },
  ];

  return (
    <Box sx={{ width: 280, bgcolor: '#2c3e50', color: 'white', overflowY: 'auto' }}>
      <Box sx={{ p: 2, borderBottom: '1px solid #34495e' }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold', m: 0 }}>
          AllFence
        </Typography>
      </Box>
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.path} disablePadding>
            <ListItemButton
              onClick={() => navigate(item.path)}
              sx={{
                '&:hover': { bgcolor: '#34495e' },
                color: 'white',
              }}
            >
              <ListItemIcon sx={{ color: 'white', minWidth: 40 }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider sx={{ bgcolor: '#34495e', my: 2 }} />
      <Box sx={{ px: 2, mb: 1 }}>
        <Typography variant="caption" sx={{ color: '#95a5a6', textTransform: 'uppercase' }}>
          Development
        </Typography>
      </Box>
      <List>
        {devMenuItems.map((item) => (
          <ListItem key={item.path} disablePadding>
            <ListItemButton
              onClick={() => navigate(item.path)}
              sx={{
                '&:hover': { bgcolor: '#34495e' },
                color: '#f39c12',
              }}
            >
              <ListItemIcon sx={{ color: '#f39c12', minWidth: 40 }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );
};

export default Sidebar;
