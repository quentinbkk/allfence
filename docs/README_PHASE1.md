# Phase 1: SQLAlchemy Database Models - Complete ✅

This document explains the new database-backed architecture and how to use it.

## What Changed

### Before (Old Approach)
- Classes stored data in memory (dictionaries)
- No persistence - data lost when program ends
- Manual CSV reading/writing required
- Difficult to query and filter data

### After (New Approach)
- SQLAlchemy models automatically persist to database
- Data survives program restarts
- Easy querying with SQLAlchemy's query API
- Relationships automatically handled
- Ready for web deployment

## Files Created

### 1. `models.py` - Database Models
Contains three main models:
- **`Fencer`**: Represents a fencer with all personal information
- **`Club`**: Represents a fencing club
- **`Ranking`**: Represents a fencer's ranking points in a specific bracket

All business logic methods from your original classes are preserved:
- `Fencer.assign_rankings_from_dob()` - Automatically creates rankings based on age
- `Ranking.update_ranking()` - Adds points to a ranking
- `Club.assign_fencers()` - Links fencers to clubs

### 2. `database.py` - Database Configuration
Manages database connections and sessions:
- `init_db()` - Creates all database tables
- `get_session()` - Creates a database session for queries
- `reset_db()` - Deletes and recreates all tables (development only)

### 3. `ingestion.py` - Data Import Functions
Functions to load data into the database:
- `ingest_fencers_from_csv()` - Import fencers from CSV file
- `ingest_clubs_from_csv()` - Import clubs from CSV file
- Handles automatic club creation

### 4. `test_models.py` - Test Suite
Comprehensive tests showing how to use the models

### 5. `migrate_csv_to_db.py` - Migration Script
One-time script to migrate your existing CSV data to the database

## Quick Start

### Step 1: Install Dependencies
```bash
pip install sqlalchemy pandas
```

### Step 2: Initialize Database
```python
from database import init_db
init_db()  # Creates the database file: fencing_management.db
```

### Step 3: Migrate Your Data
```bash
python migrate_csv_to_db.py
```

### Step 4: Test It Works
```bash
python test_models.py
```

## How to Use

### Creating a Fencer

```python
from database import get_session_context
from models import Fencer
import pandas as pd

# Use context manager for automatic session cleanup
with get_session_context() as session:
    # Create a new fencer
    fencer = Fencer(
        fencer_id=12345,
        first_name="John",
        last_name="Doe",
        dob=pd.to_datetime('2003-03-02'),
        gender='M',
        weapon='Sabre',
        club_id="Club_1"
    )
    
    # Rankings are automatically created based on age!
    # No need to call assign_rankings_from_dob() manually
    
    # Add to session
    session.add(fencer)
    
    # Commit to save to database
    session.commit()
    
    print(f"Created fencer: {fencer}")
    print(f"Rankings: {len(fencer.rankings)} brackets")
```

### Querying Data

```python
from database import get_session_context
from models import Fencer, Ranking

with get_session_context() as session:
    # Find a fencer by ID
    fencer = session.query(Fencer).filter_by(fencer_id=70196).first()
    
    # Find all fencers with a specific weapon
    sabre_fencers = session.query(Fencer).filter_by(weapon='Sabre').all()
    
    # Get top 10 fencers in Senior bracket
    top_fencers = session.query(Ranking).filter_by(
        bracket_name="Senior"
    ).order_by(Ranking.points.desc()).limit(10).all()
    
    for ranking in top_fencers:
        print(f"{ranking.fencer.full_name}: {ranking.points} pts")
```

### Updating Rankings

```python
with get_session_context() as session:
    # Get a fencer
    fencer = session.query(Fencer).filter_by(fencer_id=70196).first()
    
    # Get their Senior ranking
    senior_ranking = fencer.get_ranking_for_bracket("Senior")
    
    # Add points
    senior_ranking.update_ranking(100)
    
    # Save changes
    session.commit()
```

### Using Relationships

```python
with get_session_context() as session:
    # Get a club
    club = session.query(Club).filter_by(club_id="Club_1").first()
    
    # Access all fencers in the club (automatic!)
    print(f"Club {club.club_name} has {len(club.fencers)} fencers:")
    for fencer in club.fencers:
        print(f"  - {fencer.full_name}")
    
    # Access a fencer's club (automatic!)
    fencer = session.query(Fencer).first()
    print(f"{fencer.full_name} belongs to {fencer.club.club_name}")
```

## Database File

- **Location**: `fencing_management.db` (SQLite database file)
- **Type**: SQLite (easy to use, file-based, no server needed)
- **Future**: Easy to migrate to PostgreSQL for production

## Key Differences from Old Code

### Old Way (Dictionary-based)
```python
# Store in dictionary
fencers = {}
fencer = FencerID("John", "Doe")
fencers[12345] = fencer

# Query (manual)
fencer = fencers[12345]  # Only works if you know the ID
```

### New Way (Database-based)
```python
# Store in database
with get_session_context() as session:
    fencer = Fencer(...)
    session.add(fencer)
    session.commit()

# Query (powerful!)
with get_session_context() as session:
    # Find by ID
    fencer = session.query(Fencer).filter_by(fencer_id=12345).first()
    
    # Find by name
    fencers = session.query(Fencer).filter_by(first_name="John").all()
    
    # Complex queries
    senior_fencers = session.query(Fencer).join(Ranking).filter(
        Ranking.bracket_name == "Senior",
        Ranking.points > 100
    ).all()
```

## Migration from Old Code

Your old ingestion function worked like this:
```python
res = fencer_ingestion("./data/synth_data.csv")
fencer = res[70196]
```

New way:
```python
from ingestion import ingest_fencers_from_csv
fencers_dict = ingest_fencers_from_csv("./data/synth_data.csv")
# OR query directly from database:
from database import get_session_context
with get_session_context() as session:
    fencer = session.query(Fencer).filter_by(fencer_id=70196).first()
```

## What's Preserved

✅ All your business logic methods  
✅ All your helper functions in `ranking.py`  
✅ Same data structure concepts  
✅ Same validation logic  

## What's Improved

✨ Automatic persistence  
✨ Powerful querying  
✨ Relationship handling  
✨ Data integrity (foreign keys, constraints)  
✨ Ready for web framework integration  

## Next Steps

1. ✅ **Phase 1 Complete** - Database models created
2. **Next**: Implement Tournament class and ranking point calculation
3. **Then**: Build web API (Flask/FastAPI)
4. **Finally**: Deploy to web

## Troubleshooting

### Database file not found
Run `init_db()` to create the database file.

### Import errors
Make sure SQLAlchemy is installed: `pip install sqlalchemy`

### Data already exists
The ingestion functions check for existing records and won't create duplicates.

### Want to start fresh
Run `reset_db()` (WARNING: deletes all data!)

## Questions?

Check the comments in the code files - every function and method is thoroughly documented!
