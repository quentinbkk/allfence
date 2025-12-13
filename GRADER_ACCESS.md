# AllFence - Grader Access Instructions

## Login Credentials

**URL:** https://allfence.vercel.app

**Username:** `admin`  
**Password:** `admin123`

## About AllFence

AllFence is a comprehensive fencing tournament management system that tracks:
- **Tournaments**: View and manage fencing tournaments with brackets, results, and standings
- **Fencers**: Individual fencer profiles with performance statistics and rankings
- **Rankings**: National rankings by bracket (Senior, U20, U17, U14, U11) and weapon (Foil, Epee, Sabre)
- **Clubs**: Club profiles with member rosters and club rankings
- **Data Structure**: Visualization of the system architecture

## Features

### Authentication
- All pages require login to access
- Only users with accounts can view the system
- Admin access is granted to graders

### Rankings System
- Rankings calculated based on tournament performance
- Points awarded based on tournament category and placement
- Filters available for:
  - Age bracket (Senior, U20, U17, U14, U11)
  - Weapon type (Foil, Epee, Sabre)
  - Gender (Male, Female)

### Performance Tracking
- Cumulative ranking points over time
- Rankings progress visualization for top fencers
- Individual fencer performance graphs

### Club Management
- Club rankings based on total member points
- Club roster with detailed fencer information
- Performance statistics by club

## Navigation

The sidebar on the left provides access to all major sections:
- **Home**: Overview and quick stats
- **Tournaments**: Browse and view tournament details
- **Fencers**: Search and view fencer profiles
- **Rankings**: National rankings with filtering
- **Club Rankings**: Club performance leaderboard
- **Clubs**: Club directory and details
- **Data Structure**: System architecture diagram

## Notes for Graders

- The system uses **read-only production data**
- Season simulation is disabled in production (was available during development)
- Data includes ~600 fencers across 15 clubs
- All tournament results and rankings are pre-calculated
- The database resets to initial state after backend inactivity (Render free tier limitation)

## Support

For any issues accessing the system, please contact the developer.
