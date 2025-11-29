# Setup Instructions

## Python Environment

This project uses SQLAlchemy for database management. The code has been tested with **Anaconda Python**.

### If using Anaconda/Jupyter:

Your Anaconda environment already has SQLAlchemy installed. Just use:
```bash
/opt/anaconda3/bin/python3 your_script.py
```

Or in Jupyter notebooks, import normally:
```python
from database import init_db
from models import Fencer, Club, Ranking
```

### If using system Python:

You'll need to install SQLAlchemy. Recommended approach is to use a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it (on macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install sqlalchemy pandas

# Now you can run scripts
python migrate_csv_to_db.py
```

## Quick Start

1. **Initialize the database:**
   ```python
   from database import init_db
   init_db()
   ```

2. **Migrate your CSV data:**
   ```bash
   python migrate_csv_to_db.py
   ```
   
   Or if using Anaconda:
   ```bash
   /opt/anaconda3/bin/python3 migrate_csv_to_db.py
   ```

3. **Run tests:**
   ```bash
   python test_models.py
   ```

4. **Start using in your code:**
   ```python
   from database import get_session_context
   from models import Fencer
   
   with get_session_context() as session:
       fencer = session.query(Fencer).filter_by(fencer_id=70196).first()
       print(fencer)
   ```

## Database File

The database is stored as a SQLite file: `fencing_management.db`

This file will be created automatically when you run `init_db()`.

## Dependencies

- **SQLAlchemy**: Database ORM (already installed in Anaconda)
- **pandas**: Data manipulation (already installed in Anaconda)

If you need to install manually:
```bash
pip install sqlalchemy pandas
```
