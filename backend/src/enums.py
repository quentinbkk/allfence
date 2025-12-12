"""
Enumeration Types for the Fencing Management System

This module defines all enumeration types used throughout the application
as a single source of truth. This provides:
- Type safety and validation
- IDE code completion
- Easy documentation
- Central place to update allowed values
"""

from enum import Enum


class WeaponType(str, Enum):
    """Fencing weapon disciplines"""
    SABRE = "Sabre"
    FOIL = "Foil"
    EPEE = "Epee"
    
    @classmethod
    def values(cls):
        """Return list of all valid values"""
        return [item.value for item in cls]


class AgeBracket(str, Enum):
    """Age-based competition brackets"""
    U11 = "U11"        # Ages 0-10
    U13 = "U13"        # Ages 11-12
    U15 = "U15"        # Ages 13-14
    CADET = "Cadet"    # Ages 15-16
    JUNIOR = "Junior"  # Ages 17-19
    SENIOR = "Senior"  # Ages 20+
    
    @classmethod
    def values(cls):
        """Return list of all valid values"""
        return [item.value for item in cls]


class Gender(str, Enum):
    """Gender categories"""
    MALE = "M"
    FEMALE = "F"
    
    @classmethod
    def values(cls):
        """Return list of all valid values"""
        return [item.value for item in cls]
    
    @classmethod
    def normalize(cls, value):
        """
        Normalize gender input (0/1 -> F/M or vice versa).
        
        Args:
            value: Gender value that could be 0, 1, 'M', 'F', 'Male', 'Female', etc.
        
        Returns:
            Normalized Gender enum value ('M' or 'F')
        """
        if value in (0, '0', 'F', 'Female', 'female', Gender.FEMALE):
            return Gender.FEMALE
        elif value in (1, '1', 'M', 'Male', 'male', Gender.MALE):
            return Gender.MALE
        else:
            raise ValueError(f"Invalid gender value: {value}. Must be 0/1, M/F, or Male/Female")


class CompetitionType(str, Enum):
    """Tournament competition types affecting point multipliers"""
    LOCAL = "Local"                      # 0.5x points
    REGIONAL = "Regional"                # 1.0x points (base)
    NATIONAL = "National"                # 1.5x points
    CHAMPIONSHIP = "Championship"        # 2.0x points
    INTERNATIONAL = "International"      # 2.5x points
    
    @classmethod
    def values(cls):
        """Return list of all valid values"""
        return [item.value for item in cls]


class TournamentStatus(str, Enum):
    """Tournament lifecycle statuses"""
    UPCOMING = "Upcoming"
    REGISTRATION_OPEN = "Registration Open"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    
    @classmethod
    def values(cls):
        """Return list of all valid values"""
        return [item.value for item in cls]
    
    @classmethod
    def accepts_registration(cls, status: 'TournamentStatus') -> bool:
        """Check if a tournament status allows new registrations"""
        return status in (cls.UPCOMING, cls.REGISTRATION_OPEN)
    
    @classmethod
    def can_record_results(cls, status: 'TournamentStatus') -> bool:
        """Check if results can be recorded for this status"""
        return status in (cls.IN_PROGRESS, cls.COMPLETED)


class ClubStatus(str, Enum):
    """Club operational status"""
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PENDING = "Pending"
    SUSPENDED = "Suspended"
    
    @classmethod
    def values(cls):
        """Return list of all valid values"""
        return [item.value for item in cls]
