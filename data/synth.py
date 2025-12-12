import pandas as pd
import numpy as np
from faker import Faker
from datetime import date, timedelta
import random 

def fake_name(gender: bool):
    """ 
    gender = 0 --> Female
    gender = 1 --> Male

    returns string in format "{first_name} {last_name}" 


    """
    if gender > 1 or gender < 0:
        raise ValueError("gender needs to be a boolean value")


    fake = Faker()

    if gender == 0:
        return fake.name_female()
    else:
        return fake.name_male()
    
def fake_dob(min_age=18, max_age=90):
    today = date.today()
    start_date = today - timedelta(days=max_age * 365)
    end_date = today - timedelta(days=min_age * 365)

    random_days = random.randint(0, (end_date - start_date).days)
    return start_date + timedelta(days=random_days)

def fake_dob_for_bracket(bracket: str):
    """Generate DOB for specific age bracket"""
    today = date.today()
    
    # Age ranges for each bracket
    bracket_ages = {
        "U11": (7, 10),
        "U13": (11, 12),
        "U15": (13, 14),
        "Cadet": (15, 16),
        "Junior": (17, 19),
        "Senior": (20, 65)
    }
    
    min_age, max_age = bracket_ages.get(bracket, (20, 65))
    start_date = today - timedelta(days=max_age * 365 + 364)
    end_date = today - timedelta(days=min_age * 365)
    
    random_days = random.randint(0, (end_date - start_date).days)
    return start_date + timedelta(days=random_days)

used_ids = set()
id_map = {}

def gen_unique_id():
    while True:
        uid = random.randint(0,99999)
        if uid not in used_ids:
            used_ids.add(uid)
            return f"{uid:05d}"
        
weapons = ["Sabre", "Foil", "Epee"]

def unique_clubs(n: int):
    res = []

    for i in range(n):
        res.append(f"Club_{i+1}")

    return res



def create_d(n: int, club_no: int):
    """
    Create synthetic fencer data with equal distribution across:
    - All 6 age brackets (U11, U13, U15, Cadet, Junior, Senior)
    - All 3 weapons (Sabre, Foil, Epee)
    - Both genders (Male, Female)
    """
    res = {"fencer_id":[],
           "first_name":[],
           "last_name":[],
           "dob":[],
           "gender":[],
           "weapon":[],
           "club_id":[]
           }
    
    # fencer_id
    used_id = set()
    weapons = ["Sabre", "Foil", "Epee"]
    brackets = ["U11", "U13", "U15", "Cadet", "Junior", "Senior"]
    clubs = unique_clubs(club_no)

    # Calculate how many fencers per combination for equal distribution
    # 6 brackets × 3 weapons × 2 genders = 36 combinations
    fencers_per_combo = n // 36
    remainder = n % 36
    
    combo_index = 0
    for bracket in brackets:
        for weapon in weapons:
            for gender in [0, 1]:  # 0=Female, 1=Male
                # Add extra fencer for first 'remainder' combinations
                count = fencers_per_combo + (1 if combo_index < remainder else 0)
                combo_index += 1
                
                for _ in range(count):
                    # Generate unique fencer_id
                    uid = random.randint(0, 99999)
                    while uid in used_id:
                        uid = random.randint(0, 99999)
                    used_id.add(uid)
                    
                    res["fencer_id"].append(uid)
                    
                    # Generate name based on gender
                    uname = fake_name(gender).split()
                    res["first_name"].append(uname[0])
                    res["last_name"].append(uname[1])
                    
                    # Generate DOB for specific bracket
                    res["dob"].append(fake_dob_for_bracket(bracket))
                    
                    res["gender"].append(gender)
                    res["weapon"].append(weapon)
                    res["club_id"].append(random.choice(clubs))

    df = pd.DataFrame(res)
    return df


# running - Generate 3600 fencers for perfect distribution
# 3600 = 100 fencers per combination (6 brackets × 3 weapons × 2 genders)
df = create_d(3600, 5)

# Save to csv directory
import os
csv_dir = os.path.join(os.path.dirname(__file__), "csv")
os.makedirs(csv_dir, exist_ok=True)
csv_path = os.path.join(csv_dir, "synth_data.csv")
df.to_csv(csv_path, index=False)
print(f"Saved synthetic data to: {csv_path}")
print(f"Total fencers: {len(df)}")
print("\nDistribution by bracket:")
# Calculate bracket from ages for verification
from datetime import date
def calc_bracket(dob):
    age = (date.today() - dob).days // 365
    if age <= 10: return "U11"
    elif age <= 12: return "U13"
    elif age <= 14: return "U15"
    elif age <= 16: return "Cadet"
    elif age <= 19: return "Junior"
    else: return "Senior"

df['bracket'] = df['dob'].apply(calc_bracket)
print(df.groupby(['bracket', 'weapon', 'gender']).size().unstack(fill_value=0))
print(f"\nFencers per bracket: {df['bracket'].value_counts().sort_index()}")





        
        