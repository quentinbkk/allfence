"""
SQLAlchemy Database Models for Fencing Management System

This module defines the database models (tables) using SQLAlchemy ORM.
These models replace the previous class-based approach and provide automatic
database persistence while maintaining the same business logic methods.
"""

from sqlalchemy import Column, Integer, String, Date, ForeignKey, CheckConstraint, UniqueConstraint, Float
from sqlalchemy.orm import relationship, declarative_base
from datetime import date as date_type
import pandas as pd
from ranking import calculate_age, eligible_brackets

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
    club_id = Column(String, primary_key=True)
    
    # Club name (e.g., "Metropolitan Fencing Club")
    club_name = Column(String, nullable=False)
    
    # Year the club was founded (optional)
    start_year = Column(Integer, nullable=True)
    
    # Status of the club (e.g., "Active", "Inactive", "Pending")
    status = Column(String, nullable=True)
    
    # Primary weapon discipline for the club (optional)
    # Some clubs specialize in one weapon type
    weapon_club = Column(String, nullable=True)
    
    # Relationship: one club has many fencers
    # back_populates ensures bidirectional relationship
    # cascade='all, delete-orphan' means if club is deleted, fencers are too
    fencers = relationship("Fencer", back_populates="club", cascade="all, delete-orphan")
    
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
        self.status = status
        self.weapon_club = weapon_club
    
    def __str__(self):
        """
        String representation of the Club object.
        
        Returns:
            Formatted string with club information
        """
        return (f"{self.club_name} (ID: {self.club_id}), Founded: {self.start_year}, "
                f"Status: {self.status}, Primary Weapon: {self.weapon_club}")
    
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


class Fencer(Base):
    """
    Fencer Model - Represents an individual fencer
    
    This is the core model storing all fencer information including personal details,
    weapon discipline, and club affiliation. It has relationships with Club and Ranking.
    """
    # Table name in the database
    __tablename__ = 'fencers'
    
    # Primary key - unique identifier for each fencer
    fencer_id = Column(Integer, primary_key=True)
    
    # Personal information
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    
    # Date of birth - used to calculate age and eligible brackets
    dob = Column(Date, nullable=False)
    
    # Gender: 'M' for Male, 'F' for Female (or 'M'/'F' format)
    # Using CheckConstraint to ensure only valid values
    gender = Column(String(1), nullable=False)
    
    # Weapon discipline: "Sabre", "Foil", or "Epee"
    weapon = Column(String, nullable=False)
    
    # Foreign key - links to the clubs table
    # If club is deleted, set fencer's club_id to None (set null on delete)
    club_id = Column(String, ForeignKey('clubs.club_id', ondelete='SET NULL'), nullable=True)
    
    # Relationship: one fencer belongs to one club (many-to-one)
    # back_populates ensures bidirectional relationship with Club.fencers
    club = relationship("Club", back_populates="fencers")
    
    # Relationship: one fencer has one ranking (for their specific age bracket)
    # back_populates links to Ranking.fencer
    # cascade means if fencer is deleted, their ranking is deleted too
    rankings = relationship("Ranking", back_populates="fencer", cascade="all, delete-orphan")
    
    # Check constraint to ensure gender is valid
    __table_args__ = (
        CheckConstraint("gender IN ('M', 'F', '0', '1')", name='check_gender'),
        CheckConstraint("weapon IN ('Sabre', 'Foil', 'Epee')", name='check_weapon'),
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
        
        # Normalize gender: convert 0/1 to F/M if needed
        if gender == '0' or gender == 0:
            self.gender = 'F'
        elif gender == '1' or gender == 1:
            self.gender = 'M'
        else:
            self.gender = str(gender).upper()
        
        self.weapon = weapon
        self.club_id = club_id
        
        # Automatically assign rankings based on age after initialization
        # This calls the method that creates Ranking objects for eligible brackets
        self.assign_rankings_from_dob()
    
    def __str__(self):
        """
        String representation of the Fencer object.
        
        Returns:
            Formatted string with fencer information
        """
        return (f"{self.first_name} {self.last_name}, Date of Birth: {self.dob}, "
                f"Gender: {self.gender}, Discipline: {self.weapon}")
    
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
    fencer_id = Column(Integer, ForeignKey('fencers.fencer_id', ondelete='CASCADE'), nullable=False)
    
    # Bracket name: "U11", "U13", "U15", "Cadet", "Junior", or "Senior"
    # Each fencer belongs to exactly one bracket based on their age
    bracket_name = Column(String, nullable=False)
    
    # Current ranking points for this bracket
    # Defaults to 0 for new fencers
    points = Column(Integer, default=0, nullable=False)
    
    # Relationship: many rankings belong to one fencer (many-to-one)
    # back_populates ensures bidirectional relationship with Fencer.rankings
    fencer = relationship("Fencer", back_populates="rankings")
    
    # Unique constraint: a fencer can only have one ranking per bracket
    # Since each fencer belongs to exactly one bracket, this also ensures
    # each fencer has only one ranking entry total
    __table_args__ = (
        UniqueConstraint('fencer_id', 'bracket_name', name='unique_fencer_bracket'),
    )
    
    def __init__(self, fencer_id: int, bracket_name: str, points: int = 0):
        """
        Initialize a new Ranking instance.
        
        Args:
            fencer_id: ID of the fencer this ranking belongs to
            bracket_name: Name of the bracket (e.g., "U15", "Senior")
            points: Initial points (defaults to 0)
        """
        self.fencer_id = fencer_id
        self.bracket_name = bracket_name
        self.points = points
    
    def __str__(self):
        """
        String representation of the Ranking object.
        
        Returns:
            Formatted string with bracket name and points
        """
        return f"{self.bracket_name}: {self.points} pts"
    
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
    tournament_name = Column(String, nullable=False)
    
    # Date the tournament takes place
    date = Column(Date, nullable=False)
    
    # Location where tournament is held (optional)
    location = Column(String, nullable=True)
    
    # Weapon discipline: "Sabre", "Foil", or "Epee"
    weapon = Column(String, nullable=False)
    
    # Bracket: "U11", "U13", "U15", "Cadet", "Junior", or "Senior"
    bracket = Column(String, nullable=False)
    
    # Gender category: "M" (Male), "F" (Female), or None for mixed/open
    gender = Column(String(1), nullable=True)
    
    # Competition type/status that affects point weighting:
    # "Local", "Regional", "National", "Championship", "International"
    # Championship and International earn more points than typical Open competitions
    competition_type = Column(String, nullable=False, default="Regional")
    
    # Tournament status: "Upcoming", "Registration Open", "In Progress", "Completed", "Cancelled"
    status = Column(String, nullable=False, default="Upcoming")
    
    # Maximum number of participants (optional, None = unlimited)
    max_participants = Column(Integer, nullable=True)
    
    # Optional description or notes about the tournament
    description = Column(String, nullable=True)
    
    # Relationship: one tournament has many results
    # cascade means if tournament is deleted, all its results are deleted too
    results = relationship("TournamentResult", back_populates="tournament", cascade="all, delete-orphan")
    
    # Check constraints to ensure valid values
    __table_args__ = (
        CheckConstraint("weapon IN ('Sabre', 'Foil', 'Epee')", name='check_tournament_weapon'),
        CheckConstraint("bracket IN ('U11', 'U13', 'U15', 'Cadet', 'Junior', 'Senior')", name='check_tournament_bracket'),
        CheckConstraint("gender IN ('M', 'F') OR gender IS NULL", name='check_tournament_gender'),
        CheckConstraint("competition_type IN ('Local', 'Regional', 'National', 'Championship', 'International')", name='check_competition_type'),
        CheckConstraint("status IN ('Upcoming', 'Registration Open', 'In Progress', 'Completed', 'Cancelled')", name='check_tournament_status'),
    )
    
    def __init__(self, tournament_name: str, date, weapon: str, bracket: str,
                 competition_type: str = "Regional", gender: str = None,
                 location: str = None, max_participants: int = None, 
                 description: str = None, status: str = "Upcoming"):
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
        self.gender = gender
        self.location = location
        self.max_participants = max_participants
        self.description = description
        self.status = status
    
    def __str__(self):
        """
        String representation of the Tournament object.
        
        Returns:
            Formatted string with tournament information
        """
        gender_str = f" ({self.gender})" if self.gender else ""
        return (f"{self.tournament_name} - {self.weapon} {self.bracket}{gender_str} "
                f"({self.competition_type}) - {self.date}")
    
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
    
    def __str__(self):
        """
        String representation of the TournamentResult object.
        
        Returns:
            Formatted string with placement and points
        """
        placement_suffix = {1: "st", 2: "nd", 3: "rd"}.get(self.placement % 10 if self.placement not in [11, 12, 13] else 0, "th")
        return f"{self.placement}{placement_suffix} place: {self.points_awarded} pts"
