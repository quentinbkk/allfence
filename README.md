# AllFence - Fencing Management System

**INFO 202: Information Organization and Retrieval - Final Project**

A comprehensive web-based platform for managing fencing clubs, tournaments, rankings, and athlete data with advanced data retrieval and visualization capabilities.

---

## Project Overview

AllFence is a full-stack application designed to organize and retrieve fencing tournament data efficiently. The system implements structured data storage, relational database design, RESTful API architecture, and interactive data visualization to support club managers, athletes, and tournament organizers.

### Key Features

#### 1. **Athlete Management**
- Complete fencer profiles with personal information, club affiliation, weapon specialization
- Age bracket categorization (Youth, Cadet, Junior, Senior, Veteran)
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

#### 5. **Season Simulation** (Development Tool)
- Automated season generation with configurable parameters
- Batch tournament creation (100 tournaments per season)
- Realistic result simulation with randomized placements
- Complete ranking reset capability for testing

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
- `id` (INTEGER, Primary Key)
- `name` (TEXT, Unique, Required)
- `location` (TEXT)
- `contact_email` (TEXT)
- `contact_phone` (TEXT)

#### **2. fencers**
Athlete profiles with weapon and bracket classification
- `id` (INTEGER, Primary Key)
- `first_name` (TEXT, Required)
- `last_name` (TEXT, Required)
- `date_of_birth` (DATE, Required)
- `weapon` (TEXT, Required) - Values: 'Foil', 'Epee', 'Sabre'
- `bracket` (TEXT, Required) - Values: 'Youth', 'Cadet', 'Junior', 'Senior', 'Veteran'
- `club_id` (INTEGER, Foreign Key → clubs.id)

#### **3. tournaments**
Tournament metadata and configuration
- `id` (INTEGER, Primary Key)
- `name` (TEXT, Required)
- `date` (DATE, Required)
- `location` (TEXT, Required)
- `weapon` (TEXT, Required)
- `bracket` (TEXT, Required)
- `season_id` (INTEGER, Foreign Key → seasons.id)

#### **4. tournament_results**
Individual performance records
- `id` (INTEGER, Primary Key)
- `tournament_id` (INTEGER, Foreign Key → tournaments.id)
- `fencer_id` (INTEGER, Foreign Key → fencers.id)
- `placement` (INTEGER, Required)
- `points_earned` (INTEGER, Required)

#### **5. rankings**
Current ranking state for all fencers
- `id` (INTEGER, Primary Key)
- `fencer_id` (INTEGER, Foreign Key → fencers.id, Unique)
- `points` (INTEGER, Default: 0)
- `weapon` (TEXT, Required)
- `bracket` (TEXT, Required)
- `club_id` (INTEGER, Foreign Key → clubs.id)

#### **6. seasons**
Season definitions for tournament grouping
- `id` (INTEGER, Primary Key)
- `name` (TEXT, Unique, Required)
- `start_date` (DATE, Required)
- `end_date` (DATE, Required)

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

The backend exposes 20+ RESTful endpoints organized by resource type:

#### **Authentication** (`/api/auth`)
- `POST /login` - User authentication
- `POST /logout` - Session termination

#### **Fencers** (`/api/fencers`)
- `GET /` - List all fencers (filterable by club, weapon, bracket)
- `GET /{id}` - Get fencer details
- `GET /{id}/results` - Get tournament history
- `GET /{id}/upcoming-tournaments` - Get scheduled tournaments
- `POST /` - Create new fencer
- `PUT /{id}` - Update fencer
- `DELETE /{id}` - Delete fencer

#### **Clubs** (`/api/clubs`)
- `GET /` - List all clubs
- `GET /{id}` - Get club details
- `GET /{id}/fencers` - Get club members
- `POST /` - Create new club
- `PUT /{id}` - Update club
- `DELETE /{id}` - Delete club

#### **Tournaments** (`/api/tournaments`)
- `GET /` - List tournaments (filterable by status, weapon, bracket)
- `GET /{id}` - Get tournament details
- `POST /` - Create tournament
- `PUT /{id}` - Update tournament
- `DELETE /{id}` - Delete tournament

#### **Rankings** (`/api/rankings`)
- `GET /` - Get individual rankings (filterable by weapon, bracket)
- `GET /clubs` - Get club rankings (filterable by weapon)
- `GET /clubs/cumulative-points` - Get historical club performance data
- `POST /reset` - Reset all rankings (development)

#### **Seasons** (`/api/seasons`)
- `GET /` - List all seasons
- `GET /{id}` - Get season details
- `POST /` - Create season
- `POST /{id}/simulate` - Simulate season (development)

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
Default credentials: admin / admin
```

---

## 📖 Usage Guide

### Viewing Rankings
1. Navigate to **"Rankings"** from sidebar
2. Filter by weapon (Foil, Épée, Sabre) and bracket (Youth, Cadet, Junior, Senior, Veteran)
3. View individual fencer rankings with points and club affiliation
4. Click on any fencer to view detailed profile and tournament history

### Exploring Club Performance
1. Navigate to **"Club Rankings"** from sidebar
2. Select weapon type to view club-specific rankings
3. Review **"Club Rankings Over Time"** chart showing cumulative point progression
4. Compare performance across all clubs in unified timeline

### Managing Tournaments
1. Navigate to **"Tournaments"** from sidebar
2. View list of all tournaments (filterable by status)
3. Click on tournament to view details and participants
4. Create new tournaments via **"Create Tournament"** button

### Reviewing Data Structure
1. Navigate to **"Data Structure"** from sidebar
2. View **Database Schema** tab for table definitions
3. View **Entity Relationships** tab for relationship diagrams
4. View **API Endpoints** tab for complete API documentation

### Simulating Seasons (Development)
1. Navigate to **"Season Simulation"** from sidebar
2. Click **"Simulate Season"** to generate 100 tournaments with results
3. View updated rankings and statistics
4. Use **"Reset All Rankings"** to clear data and start fresh

---

## Sample Data

The database includes pre-populated realistic data:

- **15 Clubs** across California locations
- **600 Fencers** distributed across:
  - 3 weapons (Foil, Épée, Sabre)
  - 5 age brackets (Youth, Cadet, Junior, Senior, Veteran)
- **Variable tournament history** (generated via simulation)

Sample clubs include:
- Bay Area Fencing Club (San Francisco)
- Golden Gate Fencing Center (San Francisco)
- Peninsula Fencing Academy (Redwood City)
- Silicon Valley Fencing Center (San Jose)
- Mission Fencing Academy (San Francisco)

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
The database is pre-populated. To reset:
```bash
# Use Season Simulation page in UI to reset rankings
# Or manually delete: backend/data/database/fencing_management.db
# Run app.py to regenerate with schema only
```

### Code Quality
- TypeScript for type safety on frontend
- SQLAlchemy ORM for database abstraction
- Material-UI for consistent component design
- RTK Query for efficient data fetching and caching

---

## Project Structure

```
info_202_allfence/
├── allfence-frontend/          # React TypeScript frontend
│   ├── src/
│   │   ├── api/               # RTK Query API slices
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Page-level components
│   │   ├── store/             # Redux store configuration
│   │   └── types/             # TypeScript type definitions
│   ├── public/                # Static assets
│   └── package.json           # Frontend dependencies
│
├── backend/                    # Flask Python backend
│   ├── src/
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── database.py        # Database initialization
│   │   ├── tournament_management.py  # Tournament logic
│   │   ├── ranking.py         # Ranking calculations
│   │   └── ingestion.py       # Data import utilities
│   ├── app.py                 # Flask application entry point
│   ├── data/
│   │   └── database/          # SQLite database file
│   └── tests/                 # Backend unit tests
│
└── data/                       # Data generation scripts
    ├── synth.py               # Synthetic data generator
    └── csv/                   # CSV source files
```

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

<<<<<<< HEAD
### Import from Python

```python
from src.database import get_session_context
from src.models import Fencer, Tournament
from src.tournament_management import create_tournament

# Use the system
with get_session_context() as session:
    fencers = session.query(Fencer).all()
    # ... your code
```

### Run Scripts

```bash
# Import CSV data
python scripts/migrate_csv_to_db.py

# Fix bracket assignments
python scripts/fix_brackets.py

# Quick test
python tests/quick_test.py
```

## Features

- Database models for Fencers, Clubs, Rankings, Tournaments
- Automatic bracket assignment based on age
- Tournament management with weighted point system
- CSV import for fencers and tournament results
- Comprehensive test suite

## Documentation

See the `docs/` directory for detailed documentation:
- `README_PHASE1.md` - Database models overview
- `TOURNAMENT_SYSTEM.md` - Tournament system guide
- `TESTING_GUIDE.md` - How to test functionality
- `PHASE3_WEB_INTERFACE.md` - Next steps for web interface

## Requirements

- Python 3.8+
- SQLAlchemy
- pandas
- (See requirements.txt when created)

## Development

All core code is in `src/`. Tests are in `tests/`. Scripts in `scripts/` can be run directly.

For Phase 3 (Web Interface), see `docs/PHASE3_WEB_INTERFACE.md`.
=======
- UC Berkeley School of Information - INFO 202 Course Staff
- Flask and React communities for excellent documentation
- Material-UI and Recharts for visualization libraries
>>>>>>> f2f94a8 (Add complete AllFence fencing management with README)
