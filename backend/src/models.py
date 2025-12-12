"""
SQLAlchemy Database Models for Fencing Management System

This module defines the database models (tables) using SQLAlchemy ORM.
These models replace the previous class-based approach and provide automatic
database persistence while maintaining the same business logic methods.
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, Float, Index, Boolean
from sqlalchemy.orm import relationship, declarative_base, validates
from datetime import date as date_type, datetime, date
import pandas as pd
from typing import Dict, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from .ranking import calculate_age, eligible_brackets
from .enums import WeaponType, AgeBracket, Gender, CompetitionType, TournamentStatus, ClubStatus

# Base class for all models - required by SQLAlchemy
Base = declarative_base()


class Club(Base):
    """
    Club Model - Represents a fencing club/association
    
    This model stores information about clubs where fencers are registered.
    It has a one-to-many relationship with Fencer (many fencers can belong to one club).
    """
    # Table name in the database
    __tablename__ = 'clubs'
    
    # Primary key - unique identifier for each club
    # Using String to match your existing club_id format (e.g., "Club_1")
    club_id = Column(String, primary_key=True, index=True)
    
    # Club name (e.g., "Metropolitan Fencing Club")
    club_name = Column(String, nullable=False, index=True)
    
    # Year the club was founded (optional)
    start_year = Column(Integer, nullable=True)
    
    # Status of the club (e.g., "Active", "Inactive", "Pending")
    status = Column(String, nullable=True, index=True)
    
    # Primary weapon discipline for the club (optional)
    # Some clubs specialize in one weapon type
    weapon_club = Column(String, nullable=True)
    
    # Relationship: one club has many fencers
    # back_populates ensures bidirectional relationship
    # cascade='all, delete-orphan' means if club is deleted, fencers are too
    fencers = relationship("Fencer", back_populates="club", cascade="all, delete-orphan")
    
    # Add index for club lookups
    __table_args__ = (
        Index('idx_club_status', 'status'),
    )
    
    def __init__(self, club_id: str, club_name: str, start_year=None, status=None, weapon_club=None):
        """
        Initialize a new Club instance.
        
        Args:
            club_id: Unique identifier for the club (e.g., "Club_1")
            club_name: Name of the club
            start_year: Year club was founded (optional)
            status: Status of the club (optional)
            weapon_club: Primary weapon discipline (optional)
        """
        self.club_id = club_id
        self.club_name = club_name
        self.start_year = start_year
        self.status = status if status else ClubStatus.ACTIVE.value
        self.weapon_club = weapon_club
    
    @validates('status')
    def validate_status(self, key, value):
        """Validate club status"""
        if value and value not in ClubStatus.values():
            raise ValueError(f"Invalid club status: {value}. Must be one of {ClubStatus.values()}")
        return value
    
    def __str__(self):
        """
        String representation of the Club object.
        
        Returns:
            Formatted string with club information
        """
        return (f"{self.club_name} (ID: {self.club_id}), Founded: {self.start_year}, "
                f"Status: {self.status}, Primary Weapon: {self.weapon_club}")
    
    def to_dict(self) -> Dict:
        """
        Convert Club to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the club
        """
        return {
            'club_id': self.club_id,
            'club_name': self.club_name,
            'start_year': self.start_year,
            'status': self.status,
            'weapon_club': self.weapon_club,
            'fencer_count': len(self.fencers)
        }
    
    def assign_fencers(self, fencer):
        """
        Add a fencer to this club.
        
        This method establishes the relationship between a fencer and the club.
        The fencer's club_id is automatically updated when added to this club's fencers list.
        
        Args:
            fencer: Fencer object to add to the club
        """
        # SQLAlchemy relationship handles the bidirectional link automatically
        # When we set fencer.club = self, it's automatically added to self.fencers
        fencer.club = self
    
    def get_fencer_count(self):
        """
        Get the number of fencers in this club.
        
        Returns:
            Integer count of fencers
        """
        return len(self.fencers)
    
    def get_club_total_points(self, bracket_name=None):
        """
        Calculate total ranking points for all fencers in this club.
        
        Args:
            bracket_name: Optional bracket name to filter by. If None, sums all brackets.
        
        Returns:
            Total points for the club
        """
        total = 0
        for fencer in self.fencers:
            for ranking in fencer.rankings:
                if bracket_name is None or ranking.bracket_name == bracket_name:
                    total += ranking.points
        return total


class Season(Base):
    """
    Season Model - Represents a fencing season (e.g., 2024-2025)
    
    This model stores information about competitive seasons. Tournaments are linked
    to seasons to track historical performance and rankings over time.
    """
    # Table name in the database
    __tablename__ = 'seasons'
    
    # Primary key - auto-incrementing ID
    season_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Season name (e.g., "2024-2025", "2025-2026")
    name = Column(String, nullable=False, unique=True, index=True)
    
    # Start and end dates for the season
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Status: "Active", "Completed", "Upcoming"
    status = Column(String, nullable=False, default="Upcoming")
    
    # Optional description
    description = Column(String, nullable=True)
    
    # Relationship: one season has many tournaments
    tournaments = relationship("Tournament", back_populates="season")
    
    # Check constraint for valid status
    __table_args__ = (
        CheckConstraint("status IN ('Active', 'Completed', 'Upcoming')", name='check_season_status'),
    )
    
    def __init__(self, name: str, start_date, end_date, status: str = "Upcoming", description: str = None):
        """
        Initialize a new Season instance.
        
        Args:
            name: Season name (e.g., "2024-2025")
            start_date: Season start date
            end_date: Season end date
            status: Season status ("Active", "Completed", "Upcoming")
            description: Optional description
        """
        self.name = name
        self.start_date = start_date if isinstance(start_date, date_type) else pd.to_datetime(start_date).date()
        self.end_date = end_date if isinstance(end_date, date_type) else pd.to_datetime(end_date).date()
        self.status = status
        self.description = description
    
    def to_dict(self) -> Dict:
        """Convert Season to dictionary for JSON serialization"""
        # Only count completed tournaments in this season
        completed_count = sum(1 for t in self.tournaments if t.status == TournamentStatus.COMPLETED.value) if self.tournaments else 0
        
        return {
            'season_id': self.season_id,
            'name': self.name,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'status': self.status,
            'description': self.description,
            'tournament_count': completed_count
        }
    
    def __str__(self):
        """String representation of Season"""
        return f"Season {self.name} ({self.start_date} to {self.end_date}) - {self.status}"


class Fencer(Base):
    """
    Fencer Model - Represents an individual fencer
    
    This is the core model storing all fencer information including personal details,
    weapon discipline, and club affiliation. It has relationships with Club and Ranking.
    """
    # Table name in the database
    __tablename__ = 'fencers'
    
    # Primary key - unique identifier for each fencer
    fencer_id = Column(Integer, primary_key=True, index=True)
    
    # Personal information
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    
    # Date of birth - used to calculate age and eligible brackets
    dob = Column(Date, nullable=False)
    
    # Gender: 'M' for Male, 'F' for Female (or 'M'/'F' format)
    # Using CheckConstraint to ensure only valid values
    gender = Column(String(1), nullable=False, index=True)
    
    # Weapon discipline: "Sabre", "Foil", or "Epee"
    weapon = Column(String, nullable=False, index=True)
    
    # Foreign key - links to the clubs table
    # If club is deleted, set fencer's club_id to None (set null on delete)
    club_id = Column(String, ForeignKey('clubs.club_id', ondelete='SET NULL'), nullable=True, index=True)
    
    # Relationship: one fencer belongs to one club (many-to-one)
    # back_populates ensures bidirectional relationship with Club.fencers
    club = relationship("Club", back_populates="fencers")
    
    # Relationship: one fencer has one ranking (for their specific age bracket)
    # back_populates links to Ranking.fencer
    # cascade means if fencer is deleted, their ranking is deleted too
    rankings = relationship("Ranking", back_populates="fencer", cascade="all, delete-orphan")
    
    # Check constraint to ensure gender is valid
    # Add indexes for frequently queried columns
    __table_args__ = (
        CheckConstraint("gender IN ('M', 'F', '0', '1')", name='check_gender'),
        CheckConstraint("weapon IN ('Sabre', 'Foil', 'Epee')", name='check_weapon'),
        Index('idx_fencer_weapon_gender', 'weapon', 'gender'),
        Index('idx_fencer_club', 'club_id'),
    )
    
    def __init__(self, fencer_id: int, first_name: str, last_name: str, dob, gender: str, 
                 weapon: str, club_id: str = None):
        """
        Initialize a new Fencer instance.
        
        Args:
            fencer_id: Unique identifier for the fencer
            first_name: First name of the fencer
            last_name: Last name of the fencer
            dob: Date of birth (datetime, date, or string that can be parsed)
            gender: Gender ('M'/'F' or '0'/'1' format)
            weapon: Weapon discipline ("Sabre", "Foil", or "Epee")
            club_id: ID of the club this fencer belongs to (optional)
        """
        self.fencer_id = fencer_id
        self.first_name = first_name
        self.last_name = last_name
        
        # Convert dob to date object if it's a string or pandas Timestamp
        if isinstance(dob, str):
            self.dob = pd.to_datetime(dob).date()
        elif isinstance(dob, pd.Timestamp):
            self.dob = dob.date()
        elif isinstance(dob, date):
            self.dob = dob
        else:
            self.dob = dob
        
        # Normalize gender using enum validation
        self.gender = Gender.normalize(gender).value
        
        self.weapon = weapon
        self.club_id = club_id
        
        # Automatically assign rankings based on age after initialization
        # This calls the method that creates Ranking objects for eligible brackets
        self.assign_rankings_from_dob()
    
    @validates('weapon')
    def validate_weapon(self, key, value):
        """Validate weapon discipline"""
        if value not in WeaponType.values():
            raise ValueError(f"Invalid weapon: {value}. Must be one of {WeaponType.values()}")
        return value
    
    @validates('gender')
    def validate_gender(self, key, value):
        """Validate gender"""
        if value not in Gender.values():
            raise ValueError(f"Invalid gender: {value}. Must be one of {Gender.values()}")
        return value
    
    @validates('dob')
    def validate_dob(self, key, value):
        """Validate date of birth"""
        # Convert pandas Timestamp to date if needed
        value_date = value.date() if isinstance(value, pd.Timestamp) else value
        if isinstance(value_date, date) and value_date > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return value
    
    def __str__(self):
        """
        String representation of the Fencer object.
        
        Returns:
            Formatted string with fencer information
        """
        return (f"{self.first_name} {self.last_name}, Date of Birth: {self.dob}, "
                f"Gender: {self.gender}, Discipline: {self.weapon}")
    
    def to_dict(self, include_rankings: bool = True) -> Dict:
        """
        Convert Fencer to dictionary for JSON serialization.
        
        Args:
            include_rankings: Whether to include ranking data
        
        Returns:
            Dictionary representation of the fencer
        """
        age = calculate_age(self.dob)
        brackets = eligible_brackets(age)
        result = {
            'fencer_id': self.fencer_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'dob': self.dob.isoformat() if self.dob else None,
            'age': age,
            'bracket': brackets[0] if brackets else 'Senior',
            'gender': self.gender,
            'weapon': self.weapon,
            'club_id': self.club_id,
            'club_name': self.club.club_name if self.club else None
        }
        
        if include_rankings and self.rankings:
            result['rankings'] = [r.to_dict() for r in self.rankings]
            result['total_points'] = self.get_total_points()
        
        return result
    
    def assign_rankings_from_dob(self, today=None):
        """
        Automatically create Ranking object for the bracket this fencer belongs to.
        
        This method calculates the fencer's age and creates a Ranking entry for the
        specific bracket they belong to (U11, U13, U15, Cadet, Junior, or Senior).
        A fencer belongs to EXACTLY ONE bracket based on their age.
        
        IMPORTANT: This replaces the old behavior where fencers had rankings for
        all brackets they were old enough for. Now they only have a ranking for
        their specific age bracket.
        
        Args:
            today: Optional date to calculate age from (defaults to today)
                  Useful for testing or historical data
        
        Raises:
            ValueError: If dob is not set
        """
        if self.dob is None:
            raise ValueError("DOB must be set before assigning rankings.")
        
        # Calculate current age from date of birth
        age = calculate_age(self.dob, today)
        
        # Get the specific bracket(s) this fencer belongs to based on their exact age
        # Typically returns a list with one bracket name
        brackets = eligible_brackets(age)
        
        # If no bracket found (shouldn't happen with our age ranges), log a warning
        if not brackets:
            print(f"Warning: No bracket found for age {age} (fencer_id: {self.fencer_id})")
            return
        
        # A fencer should belong to exactly one bracket
        # Create ranking for that bracket only
        bracket_name = brackets[0]
        
        # Check if ranking for this bracket already exists
        existing_ranking = next(
            (r for r in self.rankings if r.bracket_name == bracket_name),
            None
        )
        
        # Only create if it doesn't exist yet (prevents duplicates)
        if existing_ranking is None:
            ranking = Ranking(
                fencer_id=self.fencer_id,
                bracket_name=bracket_name,
                points=0
            )
            # Add to the relationship (SQLAlchemy will handle persistence)
            self.rankings.append(ranking)
    
    def get_ranking_for_bracket(self, bracket_name: str):
        """
        Get the Ranking object for a specific bracket.
        
        Args:
            bracket_name: Name of the bracket (e.g., "U15", "Senior")
        
        Returns:
            Ranking object if found, None otherwise
        """
        return next(
            (r for r in self.rankings if r.bracket_name == bracket_name),
            None
        )
    
    def get_total_points(self):
        """
        Calculate total ranking points across all brackets.
        
        Returns:
            Sum of all points from all brackets
        """
        return sum(ranking.points for ranking in self.rankings)
    
    @property
    def full_name(self):
        """
        Property to get the full name of the fencer.
        
        Returns:
            First name and last name combined
        """
        return f"{self.first_name} {self.last_name}"


class Ranking(Base):
    """
    Ranking Model - Represents a fencer's ranking points in a specific bracket
    
    Each fencer has exactly ONE Ranking entry for their age-appropriate bracket.
    Brackets are: U11 (ages 0-10), U13 (ages 11-12), U15 (ages 13-14), 
    Cadet (ages 15-16), Junior (ages 17-19), or Senior (ages 20+).
    
    For example, a 16-year-old fencer would have a ranking only in the "Cadet" bracket.
    A 25-year-old fencer would have a ranking only in the "Senior" bracket.
    """
    # Table name in the database
    __tablename__ = 'rankings'
    
    # Primary key - auto-incrementing ID for each ranking entry
    ranking_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key - links to the fencers table
    # If fencer is deleted, delete their rankings (CASCADE delete)
    fencer_id = Column(Integer, ForeignKey('fencers.fencer_id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Bracket name: "U11", "U13", "U15", "Cadet", "Junior", or "Senior"
    # Each fencer belongs to exactly one bracket based on their age
    bracket_name = Column(String, nullable=False, index=True)
    
    # Current ranking points for this bracket
    # Defaults to 0 for new fencers
    points = Column(Integer, default=0, nullable=False)
    
    # Number of tournaments attended (for tracking participation)
    tournaments_attended = Column(Integer, default=0, nullable=False)
    
    # Relationship: many rankings belong to one fencer (many-to-one)
    # back_populates ensures bidirectional relationship with Fencer.rankings
    fencer = relationship("Fencer", back_populates="rankings")
    
    # Unique constraint: a fencer can only have one ranking per bracket
    # Since each fencer belongs to exactly one bracket, this also ensures
    # each fencer has only one ranking entry total
    # Add indexes for frequent queries
    __table_args__ = (
        UniqueConstraint('fencer_id', 'bracket_name', name='unique_fencer_bracket'),
        Index('idx_ranking_bracket_points', 'bracket_name', 'points'),
    )
    
    def __init__(self, fencer_id: int, bracket_name: str, points: int = 0, tournaments_attended: int = 0):
        """
        Initialize a new Ranking instance.
        
        Args:
            fencer_id: ID of the fencer this ranking belongs to
            bracket_name: Name of the bracket (e.g., "U15", "Senior")
            points: Initial points (defaults to 0)
            tournaments_attended: Number of tournaments attended (defaults to 0)
        """
        self.fencer_id = fencer_id
        self.bracket_name = bracket_name
        self.points = points
        self.tournaments_attended = tournaments_attended
    
    @validates('bracket_name')
    def validate_bracket(self, key, value):
        """Validate bracket name"""
        if value not in AgeBracket.values():
            raise ValueError(f"Invalid bracket: {value}. Must be one of {AgeBracket.values()}")
        return value
    
    @validates('points')
    def validate_points(self, key, value):
        """Validate points are non-negative"""
        if value < 0:
            raise ValueError("Points cannot be negative")
        return value
    
    def __str__(self):
        """
        String representation of the Ranking object.
        
        Returns:
            Formatted string with bracket name and points
        """
        return f"{self.bracket_name}: {self.points} pts"
    
    def to_dict(self) -> Dict:
        """
        Convert Ranking to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the ranking
        """
        return {
            'ranking_id': self.ranking_id,
            'fencer_id': self.fencer_id,
            'bracket_name': self.bracket_name,
            'points': self.points,
            'tournaments_attended': self.tournaments_attended or 0
        }
    
    def update_ranking(self, points: int):
        """
        Add points to the current ranking.
        
        This method is used when a fencer earns points from tournaments.
        Points are added to the existing total (not replaced).
        
        Args:
            points: Number of points to add (can be negative to subtract)
        
        Returns:
            self (for method chaining)
        
        Example:
            ranking.update_ranking(100)  # Adds 100 points
            ranking.update_ranking(-50)  # Subtracts 50 points
        """
        self.points += points
        return self
    
    def reset_ranking(self):
        """
        Reset ranking points to zero.
        
        Useful for seasonal resets or administrative corrections.
        """
        self.points = 0


class Tournament(Base):
    """
    Tournament Model - Represents a fencing competition/tournament
    
    This model stores information about tournaments including date, location,
    weapon type, bracket, and competition status/type. The competition_type
    affects how many points fencers earn (weighted point system).
    """
    # Table name in the database
    __tablename__ = 'tournaments'
    
    # Primary key - auto-incrementing ID for each tournament
    tournament_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Tournament name (e.g., "Regional Championships", "Spring Open")
    tournament_name = Column(String, nullable=False, index=True)
    
    # Date the tournament takes place
    date = Column(Date, nullable=False, index=True)
    
    # Location where tournament is held (optional)
    location = Column(String, nullable=True)
    
    # Weapon discipline: "Sabre", "Foil", or "Epee"
    weapon = Column(String, nullable=False, index=True)
    
    # Bracket: "U11", "U13", "U15", "Cadet", "Junior", or "Senior"
    bracket = Column(String, nullable=False, index=True)
    
    # Gender category: "M" (Male), "F" (Female), or None for mixed/open
    gender = Column(String(1), nullable=True, index=True)
    
    # Competition type/status that affects point weighting:
    # "Local", "Regional", "National", "Championship", "International"
    # Championship and International earn more points than typical Open competitions
    competition_type = Column(String, nullable=False, default="Regional", index=True)
    
    # Tournament status: "Upcoming", "Registration Open", "In Progress", "Completed", "Cancelled"
    status = Column(String, nullable=False, default="Upcoming", index=True)
    
    # Maximum number of participants (optional, None = unlimited)
    max_participants = Column(Integer, nullable=True)
    
    # Optional description or notes about the tournament
    description = Column(String, nullable=True)
    
    # Foreign key - links to the seasons table (optional for backwards compatibility)
    season_id = Column(Integer, ForeignKey('seasons.season_id', ondelete='SET NULL'), nullable=True, index=True)
    
    # Relationship: many tournaments belong to one season
    season = relationship("Season", back_populates="tournaments")
    
    # Relationship: one tournament has many results
    # cascade means if tournament is deleted, all its results are deleted too
    results = relationship("TournamentResult", back_populates="tournament", cascade="all, delete-orphan")
    
    # Check constraints to ensure valid values
    # Add indexes for frequently queried columns
    __table_args__ = (
        CheckConstraint("weapon IN ('Sabre', 'Foil', 'Epee')", name='check_tournament_weapon'),
        CheckConstraint("bracket IN ('U11', 'U13', 'U15', 'Cadet', 'Junior', 'Senior')", name='check_tournament_bracket'),
        CheckConstraint("gender IN ('M', 'F') OR gender IS NULL", name='check_tournament_gender'),
        CheckConstraint("competition_type IN ('Local', 'Regional', 'National', 'Championship', 'International')", name='check_competition_type'),
        CheckConstraint("status IN ('Upcoming', 'Registration Open', 'In Progress', 'Completed', 'Cancelled')", name='check_tournament_status'),
        Index('idx_tournament_weapon_bracket_status', 'weapon', 'bracket', 'status'),
        Index('idx_tournament_date_status', 'date', 'status'),
    )
    
    def __init__(self, tournament_name: str, date, weapon: str, bracket: str,
                 competition_type: str = "Regional", gender: str = None,
                 location: str = None, max_participants: int = None, 
                 description: str = None, status: str = "Upcoming", season_id: int = None):
        """
        Initialize a new Tournament instance.
        
        Args:
            tournament_name: Name of the tournament
            date: Date when tournament takes place (date object, Timestamp, or string)
            weapon: Weapon discipline ("Sabre", "Foil", or "Epee")
            bracket: Age bracket ("U11", "U13", "U15", "Cadet", "Junior", "Senior")
            competition_type: Type of competition affecting point weighting
                             ("Local", "Regional", "National", "Championship", "International")
            gender: Gender category ("M", "F", or None for mixed)
            location: Location of tournament (optional)
            max_participants: Maximum number of participants (optional)
            description: Additional notes or description (optional)
            status: Current status of tournament (default: "Upcoming")
            season_id: ID of the season this tournament belongs to (optional)
        """
        self.tournament_name = tournament_name
        # Convert date to date object if needed
        if isinstance(date, date_type):  # Already a date object
            self.date = date
        elif isinstance(date, pd.Timestamp):
            self.date = date.date()
        elif isinstance(date, str):
            self.date = pd.to_datetime(date).date()
        else:
            self.date = date
        self.weapon = weapon
        self.bracket = bracket
        self.competition_type = competition_type
        self.season_id = season_id
        self.gender = gender
        self.location = location
        self.max_participants = max_participants
        self.description = description
        self.status = status
    
    @validates('weapon')
    def validate_weapon(self, key, value):
        """Validate weapon discipline"""
        if value not in WeaponType.values():
            raise ValueError(f"Invalid weapon: {value}. Must be one of {WeaponType.values()}")
        return value
    
    @validates('bracket')
    def validate_bracket(self, key, value):
        """Validate bracket"""
        if value not in AgeBracket.values():
            raise ValueError(f"Invalid bracket: {value}. Must be one of {AgeBracket.values()}")
        return value
    
    @validates('gender')
    def validate_gender(self, key, value):
        """Validate gender"""
        if value and value not in Gender.values():
            raise ValueError(f"Invalid gender: {value}. Must be one of {Gender.values()}")
        return value
    
    @validates('competition_type')
    def validate_competition_type(self, key, value):
        """Validate competition type"""
        if value not in CompetitionType.values():
            raise ValueError(f"Invalid competition type: {value}. Must be one of {CompetitionType.values()}")
        return value
    
    @validates('status')
    def validate_status(self, key, value):
        """Validate tournament status"""
        if value not in TournamentStatus.values():
            raise ValueError(f"Invalid status: {value}. Must be one of {TournamentStatus.values()}")
        return value
    
    @validates('date')
    def validate_date(self, key, value):
        """Validate tournament date"""
        # Convert pandas Timestamp to date if needed
        value_date = value.date() if isinstance(value, pd.Timestamp) else value
        if isinstance(value_date, date) and value_date < date.today():
            import warnings
            warnings.warn(f"Tournament date {value_date} is in the past", UserWarning)
        return value
    
    def __str__(self):
        """
        String representation of the Tournament object.
        
        Returns:
            Formatted string with tournament information
        """
        gender_str = f" ({self.gender})" if self.gender else ""
        return (f"{self.tournament_name} - {self.weapon} {self.bracket}{gender_str} "
                f"({self.competition_type}) - {self.date}")
    
    def to_dict(self, include_results: bool = False) -> Dict:
        """
        Convert Tournament to dictionary for JSON serialization.
        
        Args:
            include_results: Whether to include participant results
        
        Returns:
            Dictionary representation of the tournament
        """
        result = {
            'tournament_id': self.tournament_id,
            'tournament_name': self.tournament_name,
            'date': self.date.isoformat() if self.date else None,
            'location': self.location,
            'weapon': self.weapon,
            'bracket': self.bracket,
            'gender': self.gender,
            'competition_type': self.competition_type,
            'status': self.status,
            'max_participants': self.max_participants,
            'participant_count': len(self.results),
            'is_full': self.is_full(),
            'description': self.description,
            'season_id': self.season_id
        }
        
        if include_results and self.results:
            result['results'] = [r.to_dict() for r in self.results]
        
        return result
    
    def is_full(self):
        """
        Check if tournament has reached maximum capacity.
        
        Returns:
            True if tournament is full, False otherwise
        """
        if self.max_participants is None:
            return False
        return len(self.results) >= self.max_participants
    
    def get_participant_count(self):
        """
        Get the number of registered participants.
        
        Returns:
            Integer count of participants
        """
        return len(self.results)
    
    def is_eligible_fencer(self, fencer):
        """
        Check if a fencer is eligible to participate in this tournament.
        
        Checks:
        - Fencer's weapon matches tournament weapon
        - Fencer's bracket matches tournament bracket
        - Fencer's gender matches tournament gender (if specified)
        - Tournament is not full
        - Tournament status allows registration
        
        Args:
            fencer: Fencer object to check eligibility
        
        Returns:
            Tuple (is_eligible: bool, reason: str)
        """
        # Check weapon match
        if fencer.weapon != self.weapon:
            return False, f"Fencer uses {fencer.weapon}, tournament is {self.weapon}"
        
        # Check bracket match
        # Get fencer's current bracket from their ranking
        if not fencer.rankings:
            return False, "Fencer has no ranking/bracket assignment"
        
        fencer_bracket_name = fencer.rankings[0].bracket_name
        if fencer_bracket_name != self.bracket:
            return False, f"Fencer is in {fencer_bracket_name} bracket, tournament is {self.bracket}"
        
        # Check gender match (if tournament specifies gender)
        if self.gender and fencer.gender != self.gender:
            return False, f"Fencer gender ({fencer.gender}) doesn't match tournament ({self.gender})"
        
        # Check if tournament is full
        if self.is_full():
            return False, "Tournament is full"
        
        # Check if tournament accepts registrations
        if self.status not in ["Upcoming", "Registration Open"]:
            return False, f"Tournament status is {self.status}, cannot register"
        
        return True, "Eligible"


class TournamentResult(Base):
    """
    TournamentResult Model - Represents a fencer's result in a specific tournament
    
    This model stores individual fencer results including placement and points awarded.
    Each fencer can only have one result per tournament (enforced by unique constraint).
    """
    # Table name in the database
    __tablename__ = 'tournament_results'
    
    # Primary key - auto-incrementing ID for each result
    result_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key - links to the tournaments table
    # If tournament is deleted, delete all its results (CASCADE delete)
    tournament_id = Column(Integer, ForeignKey('tournaments.tournament_id', ondelete='CASCADE'), nullable=False)
    
    # Foreign key - links to the fencers table
    # If fencer is deleted, delete all their results (CASCADE delete)
    fencer_id = Column(Integer, ForeignKey('fencers.fencer_id', ondelete='CASCADE'), nullable=False)
    
    # Placement/finish position (1 = first place, 2 = second place, etc.)
    placement = Column(Integer, nullable=False)
    
    # Points awarded from this tournament (calculated based on placement and competition type)
    points_awarded = Column(Integer, default=0, nullable=False)
    
    # Optional: Pool record (e.g., "5-2" for 5 wins, 2 losses)
    pool_record = Column(String, nullable=True)
    
    # Optional: Initial seeding/ranking before tournament
    seeding = Column(Integer, nullable=True)
    
    # Relationship: many results belong to one tournament
    tournament = relationship("Tournament", back_populates="results")
    
    # Relationship: many results belong to one fencer
    fencer = relationship("Fencer")
    
    # Unique constraint: a fencer can only have one result per tournament
    __table_args__ = (
        UniqueConstraint('tournament_id', 'fencer_id', name='unique_tournament_fencer'),
    )
    
    def __init__(self, tournament_id: int, fencer_id: int, placement: int,
                 points_awarded: int = 0, pool_record: str = None, seeding: int = None):
        """
        Initialize a new TournamentResult instance.
        
        Args:
            tournament_id: ID of the tournament this result belongs to
            fencer_id: ID of the fencer this result belongs to
            placement: Finish position (1 = first, 2 = second, etc.)
            points_awarded: Points earned from this tournament
            pool_record: Pool record string (e.g., "5-2")
            seeding: Initial seed position
        """
        self.tournament_id = tournament_id
        self.fencer_id = fencer_id
        self.placement = placement
        self.points_awarded = points_awarded
        self.pool_record = pool_record
        self.seeding = seeding
    
    @validates('placement')
    def validate_placement(self, key, value):
        """Validate placement is non-negative (0 is allowed for placeholders)"""
        if value < 0:
            raise ValueError("Placement cannot be negative")
        return value
    
    @validates('points_awarded')
    def validate_points_awarded(self, key, value):
        """Validate points are non-negative"""
        if value < 0:
            raise ValueError("Points awarded cannot be negative")
        return value
    
    def __str__(self):
        """
        String representation of the TournamentResult object.
        
        Returns:
            Formatted string with placement and points
        """
        placement_suffix = {1: "st", 2: "nd", 3: "rd"}.get(self.placement % 10 if self.placement not in [11, 12, 13] else 0, "th")
        return f"{self.placement}{placement_suffix} place: {self.points_awarded} pts"
    
    def to_dict(self) -> Dict:
        """
        Convert TournamentResult to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the result
        """
        return {
            'result_id': self.result_id,
            'tournament_id': self.tournament_id,
            'fencer_id': self.fencer_id,
            'fencer_name': f"{self.fencer.first_name} {self.fencer.last_name}" if self.fencer else None,
            'placement': self.placement,
            'points_awarded': self.points_awarded,
            'pool_record': self.pool_record,
            'seeding': self.seeding
        }


class User(Base):
    """
    User Model - Represents system users with authentication
    
    This model stores user credentials and roles for admin access.
    """
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def set_password(self, password: str):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verify the user's password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self) -> Dict:
        """Convert User to dictionary (excluding password)"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
