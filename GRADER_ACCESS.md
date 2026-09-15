# AllFence - Grader / Reviewer Access

## Live Demo

**URL:** _add your deployed Vercel URL here after deploying_

No login is required - the app is open access. Every page loads directly.

## About AllFence

AllFence is a fencing tournament management system that tracks:
- **Tournaments**: Browse fencing tournaments with brackets, results, and standings
- **Fencers**: Individual fencer profiles with performance statistics and rankings
- **Rankings**: Rankings by age bracket (U11, U13, U15, Cadet, Junior, Senior) and weapon (Foil, Epee, Sabre)
- **Clubs**: Club profiles with member rosters and club rankings
- **Data Structure**: Live-rendered documentation of the database schema, entity relationships, and API endpoints

## Navigation

The sidebar provides access to all sections:
- **Home** - Overview and quick stats
- **Tournaments** - Browse tournaments and their results
- **Fencers** - Search and view fencer profiles
- **Rankings** - Rankings leaderboard with filtering, plus a progress-over-time chart
- **Club Rankings** - Club performance leaderboard
- **Clubs** - Club directory and details
- **Data Structure** - System architecture, addressing the INFO 202 metadata/schema-documentation requirement directly in the UI

## Notes for Graders

- This is a **read-only public demo**: the backend rejects all write requests
  (creating tournaments, recording results, season simulation) by design, since
  there's no authentication gating them. See the README's "Deployment" section
  for why.
- The data is realistic synthetic data: 15 clubs, 600 fencers, 100 completed
  tournaments with recorded results and rankings.
- To see the full read/write functionality (tournament creation, result
  recording, season simulation), clone the repo and run it locally per the
  README's "Installation & Setup" section.

## Support

For any issues accessing the system, please contact the developer.
