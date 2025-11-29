# Fencing Management System

A comprehensive system for managing fencers, clubs, tournaments, and rankings.

## Project Structure

```
info_202_allfence/
├── src/                    # Core application code
│   ├── __init__.py
│   ├── models.py           # Database models (Fencer, Club, Ranking, Tournament)
│   ├── database.py         # Database configuration and session management
│   ├── ranking.py          # Ranking bracket calculations
│   ├── tournament_points.py # Point calculation system
│   ├── tournament_management.py # Tournament CRUD operations
│   └── ingestion.py        # Data import functions
│
├── tests/                  # Test files
│   ├── test_models.py      # Model tests
│   ├── test_tournaments.py # Tournament system tests
│   └── quick_test.py       # Quick functionality demo
│
├── scripts/                # Utility scripts
│   ├── migrate_csv_to_db.py # Import CSV data to database
│   └── fix_brackets.py     # Fix bracket assignments
│
├── docs/                   # Documentation
│   ├── README_PHASE1.md
│   ├── TOURNAMENT_SYSTEM.md
│   ├── TESTING_GUIDE.md
│   └── ... (other docs)
│
├── data/                   # Data files
│   ├── csv/                # CSV data files
│   │   ├── synth_data.csv
│   │   └── sample_tournament_results.csv
│   ├── database/           # Database files
│   │   └── fencing_management.db
│   └── synth.py            # Synthetic data generator
│
├── classes.ipynb           # Original notebook (for reference)
└── README.md               # This file
```

## Quick Start

### 1. Initialize Database

```bash
python -c "from src.database import init_db; init_db()"
```

### 2. Import Data

```bash
python scripts/migrate_csv_to_db.py
```

### 3. Run Tests

```bash
python tests/quick_test.py
# or
python tests/test_models.py
python tests/test_tournaments.py
```

## Usage

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

- ✅ Database models for Fencers, Clubs, Rankings, Tournaments
- ✅ Automatic bracket assignment based on age
- ✅ Tournament management with weighted point system
- ✅ CSV import for fencers and tournament results
- ✅ Comprehensive test suite

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
