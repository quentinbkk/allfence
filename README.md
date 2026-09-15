# AllFence - Fencing Management System

**INFO 202: Information Organization and Retrieval - Final Project**

A comprehensive web-based platform for managing fencing clubs, tournaments, rankings, and athlete data with advanced data retrieval and visualization capabilities.

**🔗 Live demo:** _add your deployed Vercel URL here after deploying_ — a public, read-only showcase pre-loaded with realistic sample data (15 clubs, 600 fencers, 100 tournaments). See [Deployment](#deployment) below.

---

## Project Overview

AllFence is a full-stack application designed to organize and retrieve fencing tournament data efficiently. The system implements structured data storage, relational database design, RESTful API architecture, and interactive data visualization to support club managers, athletes, and tournament organizers.

### Key Features

#### 1. **Athlete Management**
- Complete fencer profiles with personal information, club affiliation, weapon specialization
- Age bracket categorization (U11, U13, U15, Cadet, Junior, Senior)
- Individual performance tracking and tournament history
- Ranking system with automatic point calculations

#### 2. **Club Management**
- Club profiles with contact information and location data
- Club-level rankings aggregating member performance
- Historical performance visualization with cumulative points over time
- Weapon-specific club statistics (Foil, Épée, Sabre)

#### 3. **Tournament System**
- Tournament creation with weapon, bracket, and location specifications
- Automated result recording and point assignment
- Tournament filtering by status (upcoming, completed)
- Individual tournament detail pages with participant lists

#### 4. **Ranking System**
- Real-time ranking calculations based on tournament results
- Multi-dimensional filtering (weapon type, age bracket)
- Club rankings with cumulative point tracking
- Individual fencer rankings with detailed breakdowns

#### 5. **Season Simulation** (Local Development Only)
- Automated season generation with configurable parameters
- Batch tournament creation (100 tournaments per season)
- Realistic result simulation with randomized placements
- Complete ranking reset capability for testing
- Only reachable with `DEMO_MODE=false` locally - the public deployment runs in
  read-only demo mode and disables every write endpoint (see [Deployment](#deployment))

#### 6. **Data Structure Documentation**
- Interactive database schema visualization
- Entity relationship diagrams
- Complete API endpoint documentation
- Sample data formats and response structures

#### 7. **Data Visualization**
- Line charts showing club performance over time
- Pie charts displaying bracket distribution
- Progress bars for weapon specialization
- Real-time statistics dashboard

---

## System Architecture

### Technology Stack

**Backend:**
- Python 3.11+
- Flask (REST API framework)
- SQLAlchemy (ORM)
- SQLite (Database)

**Frontend:**
- React 18 with TypeScript
- Redux Toolkit + RTK Query (State management)
- Material-UI (Component library)
- Recharts (Data visualization)
- Vite (Build tool)

### Database Schema

The system uses a relational SQLite database with 6 core tables:

#### **1. clubs**
Stores fencing club information
- `club_id` (TEXT, Primary Key)
- `club_name` (TEXT, Required)
- `start_year` (INTEGER)
- `status` (TEXT) - Values: 'Active', 'Inactive', 'Pending', 'Suspended'
- `weapon_club` (TEXT) - Club's primary weapon specialization, if any

#### **2. fencers**
Athlete profiles with weapon classification
- `fencer_id` (INTEGER, Primary Key)
- `first_name`, `last_name` (TEXT, Required)
- `dob` (DATE, Required) - Age and bracket are computed from this, not stored
- `gender` (TEXT, Required) - Values: 'M', 'F'
- `weapon` (TEXT, Required) - Values: 'Foil', 'Epee', 'Sabre'
- `club_id` (TEXT, Foreign Key → clubs.club_id)

#### **3. tournaments**
Tournament metadata and configuration
- `tournament_id` (INTEGER, Primary Key)
- `tournament_name` (TEXT, Required)
- `date` (DATE, Required)
- `location` (TEXT)
- `weapon` (TEXT, Required) - 'Foil', 'Epee', 'Sabre'
- `bracket` (TEXT, Required) - 'U11', 'U13', 'U15', 'Cadet', 'Junior', 'Senior'
- `gender` (TEXT) - 'M', 'F', or null for open
- `competition_type` (TEXT) - 'Local', 'Regional', 'National', 'Championship', 'International' (affects point weighting)
- `status` (TEXT) - 'Upcoming', 'Registration Open', 'In Progress', 'Completed', 'Cancelled'
- `max_participants` (INTEGER), `description` (TEXT)
- `season_id` (INTEGER, Foreign Key → seasons.season_id)

#### **4. tournament_results**
Individual performance records
- `result_id` (INTEGER, Primary Key)
- `tournament_id` (INTEGER, Foreign Key → tournaments.tournament_id)
- `fencer_id` (INTEGER, Foreign Key → fencers.fencer_id)
- `placement` (INTEGER, Required)
- `points_awarded` (INTEGER, Default: 0)
- `pool_record` (TEXT), `seeding` (INTEGER) - optional

#### **5. rankings**
Current ranking state - one row per fencer per age bracket
- `ranking_id` (INTEGER, Primary Key)
- `fencer_id` (INTEGER, Foreign Key → fencers.fencer_id)
- `bracket_name` (TEXT, Required) - 'U11', 'U13', 'U15', 'Cadet', 'Junior', or 'Senior'
- `points` (INTEGER, Default: 0)
- `tournaments_attended` (INTEGER, Default: 0)

#### **6. seasons**
Season definitions for tournament grouping
- `season_id` (INTEGER, Primary Key)
- `name` (TEXT, Unique, Required)
- `start_date`, `end_date` (DATE, Required)
- `status` (TEXT) - 'Active', 'Completed', 'Upcoming'
- `description` (TEXT)

The exact, always-current schema (including constraints and indexes) is also rendered live from the running app on the **Data Structure** page.

### Entity Relationships

```
clubs (1) ────< (Many) fencers
clubs (1) ────< (Many) rankings
fencers (1) ────< (Many) tournament_results
fencers (1) ───── (1) rankings
tournaments (1) ────< (Many) tournament_results
seasons (1) ────< (Many) tournaments
```

### API Architecture

The backend exposes RESTful endpoints organized by resource type (fencers, clubs,
tournaments, rankings, seasons), each supporting filtered `GET` reads plus
`POST`/`PUT`/`DELETE` mutations for tournament/fencer management, registration,
and result recording. The full, always-current endpoint list is rendered live
from the running app on the **Data Structure** page's "API Endpoints" tab.

**Read-only public deployment:** the live demo runs with `DEMO_MODE=true`
(see [Deployment](#deployment)), which rejects every non-`GET` request before
it reaches the database - this is a public showcase with pre-loaded sample
data, not an editable instance. Clone the repo and run it locally to use the
full read/write functionality.

### Data Flow & State Management

1. **Frontend Request** → RTK Query hook invoked
2. **API Call** → REST endpoint on Flask backend
3. **Data Retrieval** → SQLAlchemy ORM queries SQLite database
4. **Response** → JSON serialization and HTTP response
5. **Cache Update** → RTK Query updates Redux store
6. **UI Update** → React components re-render with new data

**Cache Invalidation Strategy:**
- Mutations automatically invalidate related tags
- Tags: `Fencer`, `Club`, `Tournament`, `Ranking`
- Manual invalidation on reset/simulation operations

---

## Information Organization Concepts

This project demonstrates key concepts from INFO 202:

### 1. **Metadata & Schema Design**
- Structured database schema with clear entity definitions
- Field-level constraints (data types, required fields, uniqueness)
- Documented relationships between entities
- Comprehensive data dictionary available in UI (`/data-structure`)

### 2. **Information Retrieval**
- Multi-parameter filtering (weapon, bracket, club, status)
- Indexed queries for fast retrieval
- RESTful API design for resource-based access
- Efficient querying with SQLAlchemy ORM

### 3. **Data Organization**
- Hierarchical structure (Seasons → Tournaments → Results)
- Normalized database design (3NF compliance)
- Foreign key relationships maintaining referential integrity
- Aggregated views for club rankings

### 4. **Ranking Algorithm**
- Point-based scoring system derived from tournament placements
- Cumulative calculations over time
- Weapon and bracket-specific rankings
- Club-level aggregation of member performance

### 5. **Data Visualization**
- Time-series analysis with cumulative line charts
- Distribution analysis with pie charts
- Comparative statistics across clubs and weapons
- Interactive dashboards for data exploration

---

## Installation & Setup

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- npm or yarn package manager

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize database (already populated with sample data):
```bash
# Database file: backend/data/database/fencing_management.db
# Contains: 15 clubs, 600 fencers, pre-generated tournaments
```

5. Start Flask server:
```bash
python app.py
# Server runs on http://localhost:5001
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd allfence-frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
# Application runs on http://localhost:5173
```

4. Access application:
```
Open browser to http://localhost:5173
```
No login is required - the app is open access. Mutating actions (creating
tournaments, recording results, season simulation) hit the backend directly;
set `DEMO_MODE=false` in `backend/.env` to enable them locally (see
[Deployment](#deployment) for why they're disabled by default).

---

## 📖 Usage Guide

### Viewing Rankings
1. Navigate to **"Rankings"** from sidebar
2. Filter by weapon (Foil, Épée, Sabre) and bracket (U11, U13, U15, Cadet, Junior, Senior)
3. View individual fencer rankings with points and club affiliation
4. Click on any fencer to view detailed profile and tournament history

### Exploring Club Performance
1. Navigate to **"Club Rankings"** from sidebar
2. Select weapon type to view club-specific rankings
3. Review the cumulative points chart showing club performance progression
4. Compare performance across all clubs in unified timeline

### Browsing Tournaments
1. Navigate to **"Tournaments"** from sidebar
2. View list of all tournaments (filterable by status, weapon, bracket)
3. Click on a tournament to view details, final standings, and participants

### Reviewing Data Structure
1. Navigate to **"Data Structure"** from sidebar
2. View **Database Schema** tab for table definitions
3. View **Entity Relationships** tab for relationship diagrams
4. View **API Endpoints** tab for complete API documentation

### Simulating Seasons (Local Development Only)
Not exposed in the UI - it's a backend admin capability, disabled entirely on the
public deployment (see [Deployment](#deployment)). To use it locally, set
`DEMO_MODE=false` in `backend/.env`, restart the backend, and either run
`python backend/scripts/simulate_season.py` or call the
`POST /api/seasons/{id}/simulate` and `POST /api/rankings/reset` endpoints directly.

---

## Sample Data

The database ships pre-populated with realistic synthetic data
(`backend/data/export/*.json`, built into `backend/data/database/fencing_management.db`
by `backend/scripts/build_demo_db.py` - see [Deployment](#deployment)):

- **15 Clubs** across major US cities (e.g. Chicago Athletic Club, Houston Fencing Club,
  Phoenix Salle d'Armes, Seattle United Fencing Academy)
- **600 Fencers** distributed across:
  - 3 weapons (Foil, Épée, Sabre)
  - 6 age brackets (U11, U13, U15, Cadet, Junior, Senior)
- **100 completed tournaments** with recorded results and rankings

---

## Academic Significance

This project fulfills INFO 202 course objectives by demonstrating:

1. **Database Design**: Normalized relational schema with well-defined entities and relationships
2. **API Design**: RESTful architecture following HTTP conventions and resource-based routing
3. **Metadata Management**: Comprehensive documentation of data structures and relationships
4. **Information Retrieval**: Efficient querying with multiple filtering dimensions
5. **Data Visualization**: Multiple chart types for temporal and comparative analysis
6. **User Interface**: Intuitive navigation and data exploration tools

The **Data Structure** page specifically addresses academic requirements by providing complete visibility into the system's information architecture, making it suitable for educational evaluation and demonstration.

---

## Development Notes

### Running Tests
```bash
cd backend
pytest tests/
```

### Database Migrations
The database ships pre-populated from `backend/data/export/*.json`. To rebuild it
from scratch (e.g. after editing the export files):
```bash
python backend/scripts/build_demo_db.py
```
This deletes and regenerates `backend/data/database/fencing_management.db`.

### Code Quality
- TypeScript for type safety on frontend
- SQLAlchemy ORM for database abstraction
- Material-UI for consistent component design
- RTK Query for efficient data fetching and caching

---

## Project Structure

```
allfence/
├── vercel.json                 # Single-deploy config (static frontend + Python API)
├── allfence-frontend/          # React + TypeScript frontend
│   ├── src/
│   │   ├── api/                # RTK Query API slices (read-only queries)
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Page-level components (route-level lazy-loaded)
│   │   ├── store/               # Redux store configuration
│   │   └── types/               # TypeScript type definitions
│   └── package.json            # Frontend dependencies
│
├── backend/                    # Flask Python backend
│   ├── src/
│   │   ├── models.py           # SQLAlchemy models
│   │   ├── database.py         # Database connection/session management
│   │   ├── tournament_management.py  # Tournament logic
│   │   ├── ranking.py          # Ranking calculations
│   │   └── ingestion.py        # Data import utilities
│   ├── app.py                  # Flask application entry point (also the Vercel API function)
│   ├── data/
│   │   ├── export/             # JSON data export - source of truth for demo data
│   │   └── database/           # Pre-built SQLite demo database (generated, checked in)
│   ├── scripts/
│   │   └── build_demo_db.py    # Rebuilds the demo database from data/export/
│   └── tests/                  # Backend unit tests
│
└── data/                       # Synthetic data generation scripts
    ├── synth.py                # Synthetic data generator
    └── csv/                    # CSV source files
```

---

## Deployment

The app is deployed as a single [Vercel](https://vercel.com) project: the React
build is served as static files and the Flask app runs as a Python serverless
function, both from the same domain (via `vercel.json`), so there's no CORS
setup and no separate backend URL to configure.

**This is a public, read-only demo.** With no login system, every endpoint is
reachable by anyone with the URL - so the backend runs with `DEMO_MODE=true`
(the default), which rejects every `POST`/`PUT`/`DELETE` request with a 403
before it touches the database. The demo data itself
(`backend/data/database/fencing_management.db`, built by
`backend/scripts/build_demo_db.py` from `backend/data/export/*.json`) is
committed to the repo and bundled read-only into the deployment.

### Deploy your own copy
1. Push this repo to GitHub.
2. In the [Vercel dashboard](https://vercel.com/new), import the repo - it will
   detect `vercel.json` and deploy both the frontend and the API automatically.
   No environment variables are required (`DEMO_MODE` defaults to `true`).
3. To update the demo data, edit `backend/data/export/*.json`, run
   `python backend/scripts/build_demo_db.py`, commit the regenerated `.db`
   file, and push.

### Running with full read/write access
This read-only mode only applies to the public deployment. To run the app
locally with tournaments, results, and season simulation enabled, set
`DEMO_MODE=false` in `backend/.env` (see `backend/.env.example`) and follow
the [Installation & Setup](#installation--setup) instructions above.

---

## 👨‍💻 Author

**Quentin Geoffroy**  
INFO 202: Information Organization and Retrieval  
Final Project - Fall 2025

---

## 📄 License

This project is submitted as academic coursework for UC Berkeley School of Information.

---

## 🙏 Acknowledgments

- UC Berkeley School of Information - INFO 202 Course Staff
- Flask and React communities for excellent documentation
- Material-UI and Recharts for visualization libraries

