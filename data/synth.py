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
    clubs = unique_clubs(club_no)

    for i in range(n):

        ugender = random.randint(0,1)
        uweapon = random.choice(weapons)

        # fencer_id
        uid = random.randint(0,99999)

        if uid in used_id:
            while uid in used_id:
                uid = random.randint(0,99999)

        res["fencer_id"].append(uid)

        # name (first + last)
        uname = fake_name(ugender).split()
        res["first_name"].append(uname[0])
        res["last_name"].append(uname[1])
        res["dob"].append(fake_dob(12,60))
        res["gender"].append(ugender)
        res["weapon"].append(uweapon)



        res["club_id"].append(random.choice(clubs))


    df = pd.DataFrame(res)

    return df


# running
df = create_d(1000, 5)

df.to_csv("synth_data.csv")





        
        