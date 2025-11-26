from datetime import date 

AGE_BRACKETS = [
    ("U11",   0, 10),
    ("U13",  11, 12),
    ("U15",  13, 14),
    ("Senior", 15, 99),
]

def calculate_age(dob, today=None):
    if today is None:
        today = date.today()
    years = today.year - dob.year
    if (today.month, today.day) < (dob.month, dob.day):
        years -= 1
    return years

def eligible_brackets(age: int):
    """
    Returns all brackets where the fencer is old enough.
    If age=13 -> ['U15', 'Senior'] based on the table above.
    """
    result = []
    # assume brackets listed from youngest to oldest
    for name, min_age, max_age in AGE_BRACKETS:
        if age >= min_age:
            result.append(name)
    return result