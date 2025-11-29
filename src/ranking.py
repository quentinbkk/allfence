from datetime import date 

# Age bracket definitions: (bracket_name, min_age, max_age)
# Each fencer belongs to EXACTLY ONE bracket based on their age
AGE_BRACKETS = [
    ("U11",    0,  10),  # Ages 0-10 (inclusive)
    ("U13",   11,  12),  # Ages 11-12 (inclusive)
    ("U15",   13,  14),  # Ages 13-14 (inclusive)
    ("Cadet", 15,  16),  # Ages 15-16 (U17 equivalent, inclusive)
    ("Junior", 17,  19), # Ages 17-19 (U20 equivalent, inclusive)
    ("Senior", 20,  99), # Ages 20+ (inclusive, no upper limit)
]

def calculate_age(dob, today=None):
    """
    Calculate a person's age from their date of birth.
    
    Args:
        dob: Date of birth (date object or pandas Timestamp)
        today: Optional date to calculate age from (defaults to today)
    
    Returns:
        Integer age in years
    """
    if today is None:
        today = date.today()
    years = today.year - dob.year
    # Adjust if birthday hasn't occurred yet this year
    if (today.month, today.day) < (dob.month, dob.day):
        years -= 1
    return years

def eligible_brackets(age: int):
    """
    Returns the specific bracket(s) a fencer belongs to based on their exact age.
    
    IMPORTANT: This function returns ONLY the bracket(s) where the fencer's age
    falls within the age range. A fencer belongs to EXACTLY ONE bracket at a time.
    
    Args:
        age: The fencer's age in years
    
    Returns:
        List containing the bracket name (typically one bracket, but could be empty
        if age is out of range, or potentially multiple if there are overlapping ranges)
    
    Examples:
        age=10  -> ['U11']      (10 is within 0-10)
        age=13  -> ['U15']      (13 is within 13-14)
        age=16  -> ['Cadet']    (16 is within 15-16)
        age=18  -> ['Junior']   (18 is within 17-19)
        age=25  -> ['Senior']   (25 is within 20+)
    """
    result = []
    # Check each bracket to find which one(s) the age falls into
    for name, min_age, max_age in AGE_BRACKETS:
        # Check if age is within this bracket's range (inclusive)
        if min_age <= age <= max_age:
            result.append(name)
            # A fencer should only belong to one bracket, so break after finding it
            # (This assumes brackets don't overlap)
            break
    return result