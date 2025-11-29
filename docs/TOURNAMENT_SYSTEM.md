# Tournament System Documentation

## Overview

The tournament system allows you to:
- Create tournaments with different competition types (weighted point system)
- Register fencers for tournaments
- Record tournament results
- Automatically update fencer rankings based on results
- Import tournament results from CSV files

## Competition Types and Point Weighting

Tournaments are weighted based on their competition type. More prestigious competitions award more points:

| Competition Type | Multiplier | Example: 1st Place Points |
|-----------------|-----------|---------------------------|
| **Local**       | 0.5x      | 50 pts                    |
| **Regional**    | 1.0x      | 100 pts (base)            |
| **National**    | 1.5x      | 150 pts                   |
| **Championship**| 2.0x      | 200 pts                   |
| **International**| 2.5x    | 250 pts                   |

### Base Points by Placement

Before applying the multiplier, base points are:

- **1st place**: 100 pts
- **2nd place**: 75 pts
- **3rd place**: 50 pts
- **4th place**: 30 pts
- **5th-8th**: 20 pts (tied)
- **9th-16th**: 10 pts (tied)
- **17th-32nd**: 5 pts (tied)
- **Beyond 32nd**: 0 pts

## Usage Examples

### 1. Create a Tournament

```python
from tournament_management import create_tournament
import pandas as pd

# Create a Championship tournament
tournament = create_tournament(
    tournament_name="National Championships",
    date=pd.Timestamp('2024-06-20'),
    weapon="Sabre",
    bracket="Senior",
    competition_type="Championship",  # Higher point multiplier
    location="National Arena",
    max_participants=64
)
```

### 2. Register Fencers

```python
from tournament_management import register_fencer_for_tournament

# Register a fencer (automatically validates eligibility)
success, message = register_fencer_for_tournament(
    fencer_id=70196,
    tournament_id=tournament.tournament_id
)
print(message)  # "Fencer 70196 successfully registered"
```

### 3. Record Tournament Results

```python
from tournament_management import record_tournament_results

# Results dictionary: {fencer_id: placement}
results = {
    70196: 1,  # 1st place
    54354: 2,  # 2nd place
    20871: 3,  # 3rd place
}

# Set tournament status to "In Progress" first
tournament.status = "In Progress"
session.commit()

# Record results (automatically updates fencer rankings)
success, message = record_tournament_results(
    tournament_id=tournament.tournament_id,
    results_dict=results
)
```

### 4. Import Results from CSV

CSV file format:
```csv
fencer_id,placement
70196,1
54354,2
20871,3
```

Import the CSV:
```python
from tournament_management import import_tournament_results_from_csv

# Option 1: Import to existing tournament
success, message, tournament_id = import_tournament_results_from_csv(
    csv_file="./data/tournament_results.csv",
    tournament_id=tournament.tournament_id
)

# Option 2: Create tournament from CSV metadata
# CSV can include columns: tournament_name, date, weapon, bracket, competition_type
success, message, tournament_id = import_tournament_results_from_csv(
    csv_file="./data/tournament_results.csv"
)
```

## Point Calculation Examples

### Example 1: Regional Tournament
- 1st place in Regional (1.0x multiplier)
- Points = 100 × 1.0 = **100 pts**

### Example 2: Championship Tournament  
- 1st place in Championship (2.0x multiplier)
- Points = 100 × 2.0 = **200 pts**

### Example 3: International Tournament
- 3rd place in International (2.5x multiplier)
- Points = 50 × 2.5 = **125 pts**

### Example 4: Local Tournament
- 5th place in Local (0.5x multiplier)
- Points = 20 × 0.5 = **10 pts**

## Viewing Point Structures

```python
from tournament_points import print_point_structure

# Display point structure for any competition type
print_point_structure("Championship")
print_point_structure("International")
```

## Querying Tournaments

```python
from database import get_session_context
from models import Tournament

with get_session_context() as session:
    # Get all tournaments
    tournaments = session.query(Tournament).all()
    
    # Get upcoming tournaments
    from datetime import date
    upcoming = session.query(Tournament).filter(
        Tournament.date >= date.today(),
        Tournament.status.in_(["Upcoming", "Registration Open"])
    ).all()
    
    # Get Championship tournaments
    championships = session.query(Tournament).filter_by(
        competition_type="Championship"
    ).all()
```

## Tournament Results

```python
from tournament_management import get_tournament_results

# Get sorted results for a tournament
results = get_tournament_results(tournament_id)

for result in results:
    fencer = result.fencer
    print(f"{result.placement}. {fencer.full_name}: {result.points_awarded} pts")
```

## Eligibility Validation

Fencers are automatically validated when registering:
- ✅ Weapon must match tournament weapon
- ✅ Bracket must match tournament bracket  
- ✅ Gender must match (if tournament specifies gender)
- ✅ Tournament must not be full
- ✅ Tournament must accept registrations

## Files

- **`models.py`**: Tournament and TournamentResult models
- **`tournament_points.py`**: Point calculation system
- **`tournament_management.py`**: Tournament CRUD operations and CSV import
- **`test_tournaments.py`**: Comprehensive test suite

## Testing

Run the test suite:
```bash
/opt/anaconda3/bin/python3 test_tournaments.py
```

This tests:
- Point calculation with all competition types
- Tournament creation
- Fencer registration
- Results recording
- CSV import
- Tournament queries
