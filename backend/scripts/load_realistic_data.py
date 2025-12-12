"""
Load realistic fencing data into database and generate tournament history
- Loads clubs and fencers from CSV
- Generates ~4 completed tournaments per fencer on average
- Creates realistic tournament results
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime, timedelta
import random
from src.database import get_session_context
from src.models import Club, Fencer, Tournament, TournamentResult, Ranking, Season
from src.enums import WeaponType, AgeBracket, CompetitionType, Gender
from src.tournament_points import calculate_points
from src.ranking import calculate_age, eligible_brackets

def clear_database():
    """Clear all existing data"""
    print("🗑️  Clearing existing data...")
    with get_session_context() as session:
        # Delete in correct order due to foreign keys
        session.query(TournamentResult).delete()
        session.query(Ranking).delete()
        session.query(Tournament).delete()
        session.query(Fencer).delete()
        session.query(Club).delete()
        session.query(Season).delete()
        session.commit()
    print("✅ Database cleared")


def load_clubs():
    """Load clubs from CSV"""
    print("\n📍 Loading clubs...")
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                            'data', 'csv', 'realistic_clubs.csv')
    
    clubs_df = pd.read_csv(csv_path)
    
    with get_session_context() as session:
        for _, row in clubs_df.iterrows():
            club = Club(
                club_id=str(row['club_id']),
                club_name=row['club_name'],
                start_year=int(row['founded_year']),
                weapon_club=row['primary_weapon'],
                status='Active'
            )
            session.add(club)
        session.commit()
    
    print(f"✅ Loaded {len(clubs_df)} clubs")
    return len(clubs_df)


def load_fencers():
    """Load fencers from CSV"""
    print("\n👥 Loading fencers...")
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                            'data', 'csv', 'realistic_fencers.csv')
    
    fencers_df = pd.read_csv(csv_path)
    fencers_df['dob'] = pd.to_datetime(fencers_df['dob']).dt.date
    
    with get_session_context() as session:
        for _, row in fencers_df.iterrows():
            fencer = Fencer(
                fencer_id=int(row['fencer_id']),
                first_name=row['first_name'],
                last_name=row['last_name'],
                dob=row['dob'],
                gender=row['gender'],
                weapon=row['weapon'],
                club_id=str(row['club_id'])  # Convert to string to match Club model
            )
            session.add(fencer)
        session.commit()
    
    print(f"✅ Loaded {len(fencers_df)} fencers")
    return len(fencers_df)


def initialize_rankings():
    """Rankings are automatically created by Fencer model"""
    print("\n📊 Rankings auto-initialized by Fencer model")
    with get_session_context() as session:
        count = session.query(Ranking).count()
        print(f"✅ {count} rankings created")


def generate_tournament_history(avg_tournaments_per_fencer=4):
    """
    Generate historical tournaments with realistic results
    Creates enough tournaments so each fencer has ~4 completed tournaments on average
    """
    print(f"\n🏆 Generating tournament history ({avg_tournaments_per_fencer} tournaments/fencer avg)...")
    
    with get_session_context() as session:
        fencers = session.query(Fencer).all()
        total_fencers = len(fencers)
        
        # Group fencers by weapon and bracket
        fencer_groups = {}
        for fencer in fencers:
            age = calculate_age(fencer.dob)
            brackets = eligible_brackets(age)
            if not brackets:
                continue
            
            bracket = brackets[0]
            key = (fencer.weapon, bracket)
            if key not in fencer_groups:
                fencer_groups[key] = []
            fencer_groups[key].append(fencer)
        
        print(f"   Fencer groups: {len(fencer_groups)}")
        
        # Competition type distribution
        comp_types = [
            ('Local', 0.40),
            ('Regional', 0.35),
            ('National', 0.20),
            ('Championship', 0.04),
            ('International', 0.01)
        ]
        
        # Generate tournaments
        tournament_id = 1
        total_tournaments = 0
        total_results = 0
        
        # Date range: last 2 years
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=730)
        
        # Calculate how many tournaments we need
        # We want each fencer to participate in avg_tournaments_per_fencer tournaments
        # With varying participation rates (25%-85% based on competition type)
        # Average participation rate across all comp types ~ 48%
        avg_participation_rate = 0.48
        
        # Total tournament participations needed
        total_participations_needed = total_fencers * avg_tournaments_per_fencer
        
        # Estimate fencers per group to calculate tournaments needed per group
        avg_group_size = total_fencers / len(fencer_groups)
        
        # Tournaments needed per group
        participations_per_group = (avg_tournaments_per_fencer * avg_group_size)
        tournaments_per_group = int(participations_per_group / (avg_group_size * avg_participation_rate))
        tournaments_per_group = max(2, tournaments_per_group)  # At least 2 tournaments per group
        
        print(f"   Target: ~{tournaments_per_group} tournaments per weapon/bracket group")
        print(f"   Groups: {len(fencer_groups)}")
        
        for weapon, bracket in fencer_groups.keys():
            group_fencers = fencer_groups[(weapon, bracket)]
            if len(group_fencers) < 4:  # Skip small groups
                continue
            
            # Use fixed number of tournaments per group
            num_tournaments = tournaments_per_group
            
            for _ in range(num_tournaments):
                # Random date in the past 2 years
                days_ago = random.randint(30, 730)  # At least 30 days ago
                tournament_date = end_date - timedelta(days=days_ago)
                
                # Select competition type
                comp_type = random.choices(
                    [ct[0] for ct in comp_types],
                    weights=[ct[1] for ct in comp_types]
                )[0]
                
                # Participation rate based on competition type
                participation_rates = {
                    'Local': 0.25,
                    'Regional': 0.40,
                    'National': 0.60,
                    'Championship': 0.75,
                    'International': 0.85
                }
                
                # Select participants
                num_participants = int(len(group_fencers) * participation_rates[comp_type])
                num_participants = max(4, min(num_participants, len(group_fencers)))
                participants = random.sample(group_fencers, num_participants)
                
                # Create tournament
                tournament = Tournament(
                    tournament_name=f"{comp_type} {weapon} {bracket} #{tournament_id}",
                    date=tournament_date,
                    location=f"Venue {tournament_id}",
                    weapon=weapon,
                    bracket=bracket,
                    competition_type=comp_type,
                    gender=random.choice([None, 'M', 'F']),
                    status='Completed',
                    description=f"Historical {comp_type} tournament"
                )
                session.add(tournament)
                session.flush()
                
                # Generate results with realistic distribution
                placements = list(range(1, len(participants) + 1))
                random.shuffle(participants)
                
                for i, fencer in enumerate(participants):
                    placement = placements[i]
                    points = calculate_points(placement, comp_type)
                    
                    result = TournamentResult(
                        tournament_id=tournament.tournament_id,
                        fencer_id=fencer.fencer_id,
                        placement=placement,
                        points_awarded=points
                    )
                    session.add(result)
                    total_results += 1
                
                # Note: Rankings will be recalculated after all tournaments are generated
                
                tournament_id += 1
                total_tournaments += 1
                
                # Commit every 10 tournaments to avoid memory issues
                if total_tournaments % 10 == 0:
                    session.commit()
                    print(f"   Progress: {total_tournaments} tournaments, {total_results} results")
        
        session.commit()
        
        print(f"\n✅ Generated {total_tournaments} tournaments")
        print(f"✅ Created {total_results} results")
        print(f"   Average: {total_results / total_fencers:.1f} tournaments per fencer")


def recalculate_all_rankings():
    """Recalculate all rankings from tournament results"""
    print("\n🔄 Recalculating rankings from tournament results...")
    
    with get_session_context() as session:
        # Get all rankings
        rankings = session.query(Ranking).all()
        
        updated = 0
        for ranking in rankings:
            # Calculate actual points from tournament results
            actual_points = session.query(
                TournamentResult
            ).join(
                Tournament
            ).filter(
                TournamentResult.fencer_id == ranking.fencer_id,
                Tournament.bracket == ranking.bracket_name
            ).with_entities(
                TournamentResult.points_awarded
            ).all()
            
            total_points = sum(p[0] for p in actual_points if p[0])
            tournaments_count = len(actual_points)
            
            # Update ranking
            ranking.points = total_points
            ranking.tournaments_attended = tournaments_count
            updated += 1
        
        session.commit()
        print(f"✅ Recalculated {updated} rankings")


def main():
    """Main execution"""
    print("=" * 70)
    print("🎯 LOADING REALISTIC FENCING DATA")
    print("=" * 70)
    
    try:
        # Clear existing data
        clear_database()
        
        # Load new data
        num_clubs = load_clubs()
        num_fencers = load_fencers()
        
        # Initialize rankings
        initialize_rankings()
        
        # Generate tournament history
        generate_tournament_history(avg_tournaments_per_fencer=4)
        
        # Recalculate rankings from generated tournaments
        recalculate_all_rankings()
        
        print("\n" + "=" * 70)
        print("✨ DATA LOADING COMPLETE!")
        print("=" * 70)
        print(f"\n📊 Summary:")
        print(f"   Clubs: {num_clubs}")
        print(f"   Fencers: {num_fencers}")
        print(f"   Tournament history: Generated with ~4 tournaments/fencer")
        print(f"\n✅ Database is ready for use!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
