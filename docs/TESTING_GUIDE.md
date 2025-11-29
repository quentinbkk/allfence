# Testing Guide - How to Test All Functionalities

This guide shows you how to test all the features of the fencing management system.

## Quick Start - Run the Test Suites

### 1. Test Basic Models and Database
```bash
/opt/anaconda3/bin/python3 test_models.py
```

This tests:
- Database initialization
- Fencer, Club, Ranking models
- Relationships
- CSV ingestion

### 2. Test Tournament System
```bash
/opt/anaconda3/bin/python3 test_tournaments.py
```

This tests:
- Point calculation
- Tournament creation
- Fencer registration
- Results recording
- CSV import

## Interactive Testing - Python Scripts

### Test 1: Create a Tournament and Record Results

Create a file `test_interactive.py`:

```python
from database import get_session_context, init_db
from models import Fencer, Tournament
from tournament_management import (
    create_tournament, register_fencer_for_tournament, 
    record_tournament_results, get_tournament_results
)
from tournament_points import calculate_points, print_point_structure
import pandas as pd

# Initialize database
init_db()

with get_session_context() as session:
    # Step 1: Create a tournament
    print("=== Creating Tournament ===")
    tournament = create_tournament(
        tournament_name="Test Championship",
        date=pd.Timestamp('2024-12-15'),
        weapon="Foil",
        bracket="Senior",
        competition_type="Championship",  # 2x points!
        location="Test Arena",
        status="Registration Open",
        session=session
    )
    session.commit()
    print(f"Created: {tournament.tournament_name}")
    print(f"Tournament ID: {tournament.tournament_id}")
    
    # Step 2: Find eligible fencers
    print("\n=== Finding Eligible Fencers ===")
    eligible_fencers = session.query(Fencer).filter_by(
        weapon="Foil"
    ).limit(5).all()
    
    print(f"Found {len(eligible_fencers)} Foil fencers")
    
    # Step 3: Register fencers
    print("\n=== Registering Fencers ===")
    registered = []
    for fencer in eligible_fencers:
        success, message = register_fencer_for_tournament(
            fencer.fencer_id,
            tournament.tournament_id,
            session=session
        )
        if success:
            print(f"✓ {fencer.full_name}: {message}")
            registered.append(fencer)
        else:
            print(f"✗ {fencer.full_name}: {message}")
    
    # Step 4: Show point structure
    print("\n=== Point Structure for Championship ===")
    print_point_structure("Championship")
    
    # Step 5: Record results
    print("\n=== Recording Results ===")
    tournament.status = "In Progress"
    session.commit()
    
    # Assign placements
    results_dict = {f.fencer_id: i+1 for i, f in enumerate(registered)}
    
    success, message = record_tournament_results(
        tournament.tournament_id,
        results_dict,
        session=session
    )
    print(message)
    
    # Step 6: View results and updated rankings
    print("\n=== Tournament Results ===")
    results = get_tournament_results(tournament.tournament_id, session=session)
    for result in results:
        fencer = session.query(Fencer).filter_by(fencer_id=result.fencer_id).first()
        ranking = fencer.rankings[0] if fencer.rankings else None
        print(f"{result.placement}. {fencer.full_name}: "
              f"{result.points_awarded} pts (Total ranking: {ranking.points if ranking else 0} pts)")
```

Run it:
```bash
/opt/anaconda3/bin/python3 test_interactive.py
```

### Test 2: Import Results from CSV

Create a CSV file `test_results.csv`:
```csv
fencer_id,placement
70196,1
54354,2
20871,3
```

Then test import:
```python
from tournament_management import import_tournament_results_from_csv
from tournament_management import create_tournament
from database import get_session_context
import pandas as pd

with get_session_context() as session:
    # Create tournament first
    tournament = create_tournament(
        tournament_name="CSV Test Tournament",
        date=pd.Timestamp.today(),
        weapon="Foil",
        bracket="Senior",
        competition_type="Regional",
        status="Registration Open",
        session=session
    )
    session.commit()
    print(f"Created tournament ID: {tournament.tournament_id}")
    
    # Import results
    success, message, tournament_id = import_tournament_results_from_csv(
        "./test_results.csv",
        tournament_id=tournament.tournament_id,
        session=session
    )
    print(f"Import: {message}")
```

### Test 3: Compare Point Systems

```python
from tournament_points import calculate_points

placements = [1, 2, 3, 5]
types = ["Local", "Regional", "National", "Championship", "International"]

print("\nComparing Points by Competition Type:")
print(f"{'Placement':<12}", end="")
for t in types:
    print(f"{t:<15}", end="")
print("\n" + "-" * 90)

for placement in placements:
    print(f"{placement}{'th':<10}", end="")
    for comp_type in types:
        points = calculate_points(placement, comp_type)
        print(f"{points:<15}", end="")
    print()
```

## Testing in Jupyter Notebook

You can also test interactively in a Jupyter notebook:

1. Open your `classes.ipynb` notebook
2. Add new cells:

```python
# Cell 1: Import everything
from database import get_session_context, init_db
from models import Fencer, Tournament, Ranking
from tournament_management import *
from tournament_points import *
import pandas as pd

init_db()
```

```python
# Cell 2: View point structures
print_point_structure("Regional")
print("\n")
print_point_structure("Championship")
```

```python
# Cell 3: Create a tournament
with get_session_context() as session:
    tournament = create_tournament(
        tournament_name="My Test Tournament",
        date=pd.Timestamp('2024-12-20'),
        weapon="Sabre",
        bracket="Senior",
        competition_type="National",
        session=session
    )
    session.commit()
    print(f"Created tournament: {tournament.tournament_name}")
    print(f"ID: {tournament.tournament_id}")
```

```python
# Cell 4: View fencers
with get_session_context() as session:
    fencers = session.query(Fencer).filter_by(weapon="Sabre").limit(10).all()
    for f in fencers:
        ranking = f.rankings[0] if f.rankings else None
        print(f"{f.full_name}: {f.weapon}, {f.rankings[0].bracket_name if ranking else 'No ranking'}, "
              f"{ranking.points if ranking else 0} pts")
```

```python
# Cell 5: Register a fencer
with get_session_context() as session:
    success, message = register_fencer_for_tournament(
        fencer_id=70196,  # Change to a real fencer ID
        tournament_id=1,   # Change to your tournament ID
        session=session
    )
    print(message)
```

## Test Querying Functions

### Find Top Ranked Fencers
```python
from database import get_session_context
from models import Ranking, Fencer

with get_session_context() as session:
    # Top 10 fencers in Senior bracket
    top_fencers = session.query(Ranking).filter_by(
        bracket_name="Senior"
    ).order_by(Ranking.points.desc()).limit(10).all()
    
    print("Top 10 Senior Fencers:")
    for i, ranking in enumerate(top_fencers, 1):
        fencer = ranking.fencer
        print(f"{i}. {fencer.full_name}: {ranking.points} pts ({fencer.weapon})")
```

### Find Tournaments by Type
```python
from database import get_session_context
from models import Tournament

with get_session_context() as session:
    # All Championship tournaments
    championships = session.query(Tournament).filter_by(
        competition_type="Championship"
    ).all()
    
    print("Championship Tournaments:")
    for t in championships:
        print(f"- {t.tournament_name} ({t.date})")
```

### View Tournament Results
```python
from tournament_management import get_tournament_results
from database import get_session_context

with get_session_context() as session:
    results = get_tournament_results(tournament_id=1, session=session)
    
    print("Tournament Results:")
    for result in results:
        fencer = result.fencer
        print(f"{result.placement}. {fencer.full_name}: {result.points_awarded} pts")
```

## Test CSV Import with Sample File

The system includes a sample CSV file:

```python
from tournament_management import import_tournament_results_from_csv
from tournament_management import create_tournament
from database import get_session_context
import pandas as pd

with get_session_context() as session:
    # Create tournament
    tournament = create_tournament(
        tournament_name="Sample CSV Tournament",
        date=pd.Timestamp.today(),
        weapon="Foil",
        bracket="Senior",
        competition_type="Championship",
        status="Registration Open",
        session=session
    )
    session.commit()
    
    # Import from sample file
    success, message, tournament_id = import_tournament_results_from_csv(
        "./data/sample_tournament_results.csv",
        tournament_id=tournament.tournament_id,
        session=session
    )
    print(message)
```

## Quick Test Checklist

- [ ] Run `test_models.py` - Verify basic database operations
- [ ] Run `test_tournaments.py` - Verify tournament system
- [ ] Create a tournament manually
- [ ] Register some fencers
- [ ] Record tournament results
- [ ] Verify rankings updated automatically
- [ ] Import results from CSV
- [ ] View point structures for different competition types
- [ ] Query top ranked fencers
- [ ] Create tournaments with different competition types and verify point differences

## Common Test Scenarios

### Scenario 1: Championship vs Regional Tournament
```python
# Create two tournaments with same results
# Compare that Championship awards 2x points
```

### Scenario 2: Eligibility Validation
```python
# Try to register fencer with wrong weapon - should fail
# Try to register fencer with wrong bracket - should fail
# Try to register to full tournament - should fail
```

### Scenario 3: Ranking Updates
```python
# Record tournament results
# Check that fencer rankings increased by correct amount
# Verify points match competition type multiplier
```

## Troubleshooting

If tests fail:
1. Make sure database is initialized: `init_db()`
2. Check that fencers exist in database
3. Verify fencer weapon/bracket matches tournament
4. Check tournament status allows registration/results

For help, check the test output messages - they're designed to be informative!
