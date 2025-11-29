# Bracket System Update

## Changes Made

### 1. Updated Bracket Definitions

Added two new brackets and fixed the eligibility logic:

- **U11**: Ages 0-10 (no change)
- **U13**: Ages 11-12 (no change)
- **U15**: Ages 13-14 (no change)
- **Cadet (U17)**: Ages 15-16 (NEW)
- **Junior (U20)**: Ages 17-19 (NEW)
- **Senior**: Ages 20+ (no change)

### 2. Fixed Eligibility Logic

**Before:** Fencers had rankings for ALL brackets they were old enough for.
- Example: A 25-year-old had rankings for U11, U13, U15, and Senior

**After:** Fencers have rankings for ONLY their specific age bracket.
- Example: A 25-year-old has ONLY a Senior ranking
- Example: A 16-year-old has ONLY a Cadet ranking
- Example: A 13-year-old has ONLY a U15 ranking

### 3. Files Updated

- `ranking.py`: Updated `AGE_BRACKETS` and `eligible_brackets()` function
- `models.py`: Updated comments and documentation to reflect single-bracket system
- `fix_brackets.py`: Created migration script to fix existing data

## Migration Required

Since existing fencers in your database have multiple rankings (old system), you need to run the migration script:

```bash
/opt/anaconda3/bin/python3 fix_brackets.py
```

This script will:
1. Remove all existing rankings
2. Reassign each fencer to their correct single bracket based on current age
3. Show a distribution of fencers across brackets

## Testing

Test the new bracket logic:

```python
from ranking import eligible_brackets

print(eligible_brackets(10))   # ['U11']
print(eligible_brackets(13))   # ['U15']
print(eligible_brackets(16))   # ['Cadet']
print(eligible_brackets(18))   # ['Junior']
print(eligible_brackets(25))   # ['Senior']
```

## Impact

- New fencers will automatically get the correct single bracket
- Existing fencers need to be migrated using `fix_brackets.py`
- All queries and reports will now show one ranking per fencer
