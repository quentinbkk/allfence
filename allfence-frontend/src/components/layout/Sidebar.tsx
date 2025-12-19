import React from 'react';
import { Box, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Typography } from '@mui/material';
import {
  EmojiEvents as TournamentIcon,
  People as FencersIcon,
  LeaderboardOutlined as RankingsIcon,
  Groups as ClubsIcon,
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

  return (
    <Box sx={{ width: 280, bgcolor: '#2c3e50', color: 'white', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, borderBottom: '1px solid #34495e' }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold', m: 0 }}>
          AllFence
        </Typography>
      </Box>
      <List sx={{ flex: 1, overflowY: 'auto' }}>
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
    </Box>
  );
};

export default Sidebar;
