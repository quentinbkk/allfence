# Project Structure

## Directory Organization

```
info_202_allfence/
│
├── src/                          # Core application code (Python package)
│   ├── __init__.py              # Package initialization
│   ├── models.py                # Database models (Fencer, Club, Ranking, Tournament)
│   ├── database.py              # Database configuration and session management
│   ├── ranking.py               # Age bracket calculation functions
│   ├── tournament_points.py     # Point calculation system with weighted competitions
│   ├── tournament_management.py # Tournament CRUD operations and CSV import
│   └── ingestion.py             # Data import functions for CSV files
│
├── tests/                        # Test files
│   ├── test_models.py           # Tests for database models
│   ├── test_tournaments.py      # Tests for tournament system
│   └── quick_test.py            # Quick functionality demonstration
│
├── scripts/                      # Utility scripts (run from command line)
│   ├── migrate_csv_to_db.py     # Import CSV data into database
│   └── fix_brackets.py          # Fix bracket assignments for existing fencers
│
├── docs/                         # Documentation files
│   ├── README_PHASE1.md         # Phase 1 implementation documentation
│   ├── TOURNAMENT_SYSTEM.md     # Tournament system user guide
│   ├── TESTING_GUIDE.md         # How to test all functionality
│   ├── PHASE3_WEB_INTERFACE.md  # Next phase planning
│   └── ...                      # Other documentation files
│
├── data/                         # Data files directory
│   ├── csv/                     # CSV data files
│   │   ├── synth_data.csv       # Synthetic fencer data
│   │   └── sample_tournament_results.csv  # Sample tournament results
│   ├── database/                # Database files
│   │   └── fencing_management.db  # SQLite database file
│   └── synth.py                 # Script to generate synthetic data
│
├── classes.ipynb                # Original Jupyter notebook (for reference)
├── README.md                    # Main project README
├── PROJECT_STRUCTURE.md         # This file
└── .gitignore                   # Git ignore patterns
```

## How to Import

### From Command Line Scripts

Scripts in `scripts/` should add the parent directory to the path:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.database import init_db
from src.models import Fencer
```

### From Test Files

Tests in `tests/` follow the same pattern:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.database import get_session_context
```

### From Application Code

Within the `src/` package, use relative imports:

```python
from .database import get_session_context
from .models import Fencer, Tournament
```

### From External Code

If importing from outside the project:

```python
import sys
sys.path.insert(0, '/path/to/info_202_allfence')
from src.database import get_session_context
from src.models import Fencer
```

## File Paths

### Database Location
- Database file: `data/database/fencing_management.db`
- Configured in `src/database.py`
- Automatically created if it doesn't exist

### CSV Files
- Data CSV files: `data/csv/`
- Use relative paths from script location or absolute paths
- Example: `os.path.join(os.path.dirname(__file__), "..", "data", "csv", "file.csv")`

## Running Scripts

### Migration Script
```bash
python scripts/migrate_csv_to_db.py
```

### Fix Brackets
```bash
python scripts/fix_brackets.py
```

### Run Tests
```bash
python tests/quick_test.py
python tests/test_models.py
python tests/test_tournaments.py
```

## Adding New Files

### New Core Code
- Add to `src/` directory
- Use relative imports within the package
- Add to `src/__init__.py` if needed

### New Tests
- Add to `tests/` directory
- Follow naming convention: `test_*.py`
- Import from `src` package

### New Scripts
- Add to `scripts/` directory
- Add parent directory to path before importing
- Make executable if needed: `chmod +x script.py`

### New Documentation
- Add to `docs/` directory
- Use Markdown format (`.md`)
- Update README.md if needed

## Best Practices

1. **Never use absolute paths** - Always use relative paths or `os.path.join()`
2. **Import from src package** - Use `from src.module import ...` in scripts/tests
3. **Use relative imports** - Within `src/`, use `from .module import ...`
4. **Keep data separate** - All data files in `data/` directory
5. **Document changes** - Update this file if structure changes
