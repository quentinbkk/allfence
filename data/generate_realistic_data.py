"""
Generate realistic fencing dataset with:
- Specialized clubs (each focuses on one weapon)
- ~40 fencers per club across all age brackets
- Realistic club names
- Equal distribution across brackets and genders
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import date, timedelta
import random
import os

# Initialize Faker
fake = Faker()

# Realistic club name components
CLUB_PREFIXES = [
    "Metro", "City", "Capital", "Elite", "Premier", "Royal", "Golden",
    "Silver", "Olympic", "Champion", "Victory", "United", "Alliance",
    "Academy", "Institute", "Phoenix", "Dragon", "Eagle", "Lion",
    "Atlantic", "Pacific", "Mountain", "Valley", "River", "Lake"
]

CLUB_LOCATIONS = [
    "New York", "Boston", "Chicago", "San Francisco", "Los Angeles",
    "Seattle", "Denver", "Austin", "Miami", "Portland", "Philadelphia",
    "Washington", "Baltimore", "Detroit", "Minneapolis", "Atlanta",
    "Houston", "Dallas", "Phoenix", "San Diego"
]

CLUB_TYPES = [
    "Fencing Club", "Fencing Academy", "Fencing Center",
    "Salle d'Armes", "Fencing Institute", "Athletic Club"
]


def generate_club_name():
    """Generate a realistic club name"""
    style = random.choice([
        lambda: f"{random.choice(CLUB_LOCATIONS)} {random.choice(CLUB_TYPES)}",
        lambda: f"{random.choice(CLUB_PREFIXES)} {random.choice(CLUB_TYPES)}",
        lambda: f"{random.choice(CLUB_LOCATIONS)} {random.choice(CLUB_PREFIXES)} {random.choice(['Fencing Club', 'Fencing Academy'])}",
    ])
    return style()


def create_clubs(num_clubs=15):
    """
    Create clubs with weapon specializations
    Each weapon should have roughly equal representation
    """
    clubs = []
    weapons = ["Sabre", "Foil", "Epee"]
    used_names = set()
    
    for i in range(num_clubs):
        # Ensure equal distribution of weapons
        weapon = weapons[i % len(weapons)]
        
        # Generate unique club name
        name = generate_club_name()
        while name in used_names:
            name = generate_club_name()
        used_names.add(name)
        
        clubs.append({
            'club_id': i + 1,
            'club_name': name,
            'primary_weapon': weapon,
            'location': random.choice(CLUB_LOCATIONS),
            'founded_year': random.randint(1950, 2020)
        })
    
    return pd.DataFrame(clubs)


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


def create_fencers(clubs_df, fencers_per_club=40):
    """
    Create fencers distributed across clubs
    Each club gets ~40 fencers, specialized in their primary weapon
    Fencers are distributed across all age brackets and both genders
    """
    brackets = ["U11", "U13", "U15", "Cadet", "Junior", "Senior"]
    genders = ["M", "F"]
    
    fencers = []
    used_ids = set()
    fencer_id = 1
    
    for _, club in clubs_df.iterrows():
        weapon = club['primary_weapon']
        club_id = club['club_id']
        
        # For each club, create equal distribution across brackets and genders
        # 6 brackets × 2 genders = 12 combinations
        fencers_per_combo = fencers_per_club // 12
        remainder = fencers_per_club % 12
        
        combo_index = 0
        for bracket in brackets:
            for gender in genders:
                # Add extra fencer for first 'remainder' combinations
                count = fencers_per_combo + (1 if combo_index < remainder else 0)
                combo_index += 1
                
                for _ in range(count):
                    # Generate name based on gender
                    if gender == "M":
                        full_name = fake.name_male()
                    else:
                        full_name = fake.name_female()
                    
                    name_parts = full_name.split()
                    first_name = name_parts[0]
                    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else name_parts[0]
                    
                    # Generate DOB for bracket
                    dob = fake_dob_for_bracket(bracket)
                    
                    fencers.append({
                        'fencer_id': fencer_id,
                        'first_name': first_name,
                        'last_name': last_name,
                        'full_name': full_name,
                        'dob': dob,
                        'gender': gender,
                        'weapon': weapon,
                        'club_id': club_id,
                        'email': fake.email(),
                        'phone': fake.phone_number()
                    })
                    
                    fencer_id += 1
    
    return pd.DataFrame(fencers)


def main():
    """Generate and save realistic fencing data"""
    
    print("🎯 Generating Realistic Fencing Dataset...")
    print("=" * 60)
    
    # Generate 15 clubs (5 per weapon)
    num_clubs = 15
    print(f"\n📍 Creating {num_clubs} clubs with weapon specializations...")
    clubs_df = create_clubs(num_clubs)
    
    print("\nClubs by weapon:")
    print(clubs_df.groupby('primary_weapon')['club_name'].apply(list))
    
    # Generate fencers (~40 per club = 600 total)
    fencers_per_club = 40
    print(f"\n👥 Creating ~{fencers_per_club} fencers per club...")
    fencers_df = create_fencers(clubs_df, fencers_per_club)
    
    # Calculate actual bracket from age for verification
    def calc_bracket(dob):
        age = (date.today() - dob).days // 365
        if age <= 10: return "U11"
        elif age <= 12: return "U13"
        elif age <= 14: return "U15"
        elif age <= 16: return "Cadet"
        elif age <= 19: return "Junior"
        else: return "Senior"
    
    fencers_df['bracket'] = fencers_df['dob'].apply(calc_bracket)
    
    # Save to CSV
    csv_dir = os.path.join(os.path.dirname(__file__), "csv")
    os.makedirs(csv_dir, exist_ok=True)
    
    clubs_path = os.path.join(csv_dir, "realistic_clubs.csv")
    fencers_path = os.path.join(csv_dir, "realistic_fencers.csv")
    
    clubs_df.to_csv(clubs_path, index=False)
    fencers_df.to_csv(fencers_path, index=False)
    
    print(f"\n✅ Saved clubs to: {clubs_path}")
    print(f"✅ Saved fencers to: {fencers_path}")
    
    # Print statistics
    print("\n" + "=" * 60)
    print("📊 DATASET STATISTICS")
    print("=" * 60)
    
    print(f"\n🏛️  Total Clubs: {len(clubs_df)}")
    print("\nClubs per weapon:")
    print(clubs_df['primary_weapon'].value_counts().sort_index())
    
    print(f"\n👤 Total Fencers: {len(fencers_df)}")
    print(f"   Average per club: {len(fencers_df) / len(clubs_df):.1f}")
    
    print("\n🗡️  Fencers per weapon:")
    print(fencers_df['weapon'].value_counts().sort_index())
    
    print("\n🎂 Fencers per bracket:")
    print(fencers_df['bracket'].value_counts().sort_index())
    
    print("\n⚧  Fencers per gender:")
    print(fencers_df['gender'].value_counts())
    
    print("\n🏆 Distribution (Weapon × Bracket × Gender):")
    dist = fencers_df.groupby(['weapon', 'bracket', 'gender']).size()
    print(f"   Min: {dist.min()}, Max: {dist.max()}, Mean: {dist.mean():.1f}")
    
    print("\n" + "=" * 60)
    print("✨ Data generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
