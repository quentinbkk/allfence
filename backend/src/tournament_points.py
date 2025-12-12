"""
Tournament Point Calculation System

This module handles the calculation of ranking points awarded to fencers
based on their tournament placement and the competition type/weighting.

The system uses a weighted point structure where more prestigious competitions
(Championships, International) award more points than typical Open competitions.
"""

# Base points awarded by placement (before weighting)
# These are the points for a "Regional" level competition
BASE_POINTS_BY_PLACEMENT = {
    1: 100,   # 1st place
    2: 75,    # 2nd place
    3: 50,    # 3rd place (typically tied for 3rd-4th)
    4: 30,    # 4th place
    5: 20,    # 5th-8th (tied)
    6: 20,    # 5th-8th (tied)
    7: 20,    # 5th-8th (tied)
    8: 20,    # 5th-8th (tied)
    9: 10,    # 9th-16th (tied)
    10: 10,
    11: 10,
    12: 10,
    13: 10,
    14: 10,
    15: 10,
    16: 10,
    17: 5,    # 17th-32nd (tied)
    32: 5,    # Any placement beyond 16th typically gets 5 points if they advance
}

# Competition type multipliers
# These multiply the base points to determine final points awarded
# Higher multipliers mean more prestigious competitions award more points
COMPETITION_TYPE_MULTIPLIERS = {
    "Local": 0.5,           # Local tournaments award 50% of base points
    "Regional": 1.0,        # Regional (default/base) tournaments award 100% of base points
    "National": 1.5,        # National tournaments award 150% of base points
    "Championship": 2.0,    # Championship competitions award 200% of base points
    "International": 2.5,   # International competitions award 250% of base points
}


def get_base_points(placement: int) -> int:
    """
    Get the base points for a given placement (before competition type weighting).
    
    Base points are for "Regional" level competitions. Higher placements get more points,
    with diminishing returns for lower placements.
    
    Args:
        placement: Finish position (1 = first place, 2 = second, etc.)
    
    Returns:
        Base points for that placement (integer)
    
    Examples:
        get_base_points(1)  # Returns 100
        get_base_points(5)  # Returns 20 (5th-8th tied)
        get_base_points(25) # Returns 5 (17th-32nd)
    """
    # For exact matches (top 16)
    if placement in BASE_POINTS_BY_PLACEMENT:
        return BASE_POINTS_BY_PLACEMENT[placement]
    
    # For placements beyond the defined table
    # Typically fencers who don't make it out of pools get 0 points
    if placement > 32:
        return 0
    
    # For placements 17-31, return 5 points (tied for 17th-32nd)
    if 17 <= placement <= 32:
        return 5
    
    # Should not reach here, but return 0 as default
    return 0


def get_competition_multiplier(competition_type: str) -> float:
    """
    Get the point multiplier for a competition type.
    
    The multiplier is applied to base points to determine final points awarded.
    More prestigious competitions have higher multipliers.
    
    Args:
        competition_type: Type of competition
                         ("Local", "Regional", "National", "Championship", "International")
    
    Returns:
        Multiplier value (float)
    
    Raises:
        ValueError: If competition_type is not recognized
    """
    if competition_type not in COMPETITION_TYPE_MULTIPLIERS:
        raise ValueError(
            f"Unknown competition type: {competition_type}. "
            f"Must be one of: {list(COMPETITION_TYPE_MULTIPLIERS.keys())}"
        )
    return COMPETITION_TYPE_MULTIPLIERS[competition_type]


def calculate_points(placement: int, competition_type: str) -> int:
    """
    Calculate the total points awarded for a given placement and competition type.
    
    This is the main function used to determine how many ranking points a fencer
    earns from a tournament. It combines base points with the competition type multiplier.
    
    Formula: Points = Base Points × Competition Multiplier (rounded to nearest integer)
    
    Args:
        placement: Finish position (1 = first place, 2 = second, etc.)
        competition_type: Type of competition affecting point weighting
                         ("Local", "Regional", "National", "Championship", "International")
    
    Returns:
        Total points awarded (integer, rounded)
    
    Examples:
        # Regional competition (1.0x multiplier)
        calculate_points(1, "Regional")      # Returns 100 (100 × 1.0)
        calculate_points(3, "Regional")      # Returns 50 (50 × 1.0)
        
        # Championship competition (2.0x multiplier)
        calculate_points(1, "Championship")  # Returns 200 (100 × 2.0)
        calculate_points(3, "Championship")  # Returns 100 (50 × 2.0)
        
        # Local competition (0.5x multiplier)
        calculate_points(1, "Local")         # Returns 50 (100 × 0.5)
    """
    # Get base points for this placement
    base_points = get_base_points(placement)
    
    # Get multiplier for this competition type
    multiplier = get_competition_multiplier(competition_type)
    
    # Calculate final points (rounded to nearest integer)
    final_points = int(round(base_points * multiplier))
    
    return final_points


def get_point_structure(competition_type: str = "Regional") -> dict:
    """
    Get the complete point structure for a given competition type.
    
    This function returns a dictionary showing how many points are awarded
    for each placement in a specific competition type. Useful for display
    or documentation.
    
    Args:
        competition_type: Type of competition
                         ("Local", "Regional", "National", "Championship", "International")
    
    Returns:
        Dictionary mapping placement to points awarded
        Format: {placement: points, ...}
    
    Example:
        structure = get_point_structure("Championship")
        print(structure[1])  # 200 (1st place in Championship)
    """
    structure = {}
    multiplier = get_competition_multiplier(competition_type)
    
    # Calculate points for each defined placement
    for placement in sorted(BASE_POINTS_BY_PLACEMENT.keys()):
        base_points = BASE_POINTS_BY_PLACEMENT[placement]
        structure[placement] = int(round(base_points * multiplier))
    
    return structure


def print_point_structure(competition_type: str = "Regional"):
    """
    Print a formatted table showing point structure for a competition type.
    
    Useful for displaying point systems to users or in documentation.
    
    Args:
        competition_type: Type of competition to display
    """
    structure = get_point_structure(competition_type)
    multiplier = get_competition_multiplier(competition_type)
    
    print(f"\nPoint Structure for {competition_type} Competitions (Multiplier: {multiplier}x)")
    print("=" * 60)
    print(f"{'Placement':<15} {'Base Points':<15} {'Final Points':<15}")
    print("-" * 60)
    
    # Group placements by point value for cleaner display
    points_to_placements = {}
    for placement, points in structure.items():
        if points not in points_to_placements:
            points_to_placements[points] = []
        points_to_placements[points].append(placement)
    
    # Sort by points (descending)
    for points in sorted(points_to_placements.keys(), reverse=True):
        placements = sorted(points_to_placements[points])
        base = get_base_points(placements[0])
        
        # Format placement range
        if len(placements) == 1:
            placement_str = f"{placements[0]}st"
            if placements[0] == 1:
                placement_str = "1st"
            elif placements[0] == 2:
                placement_str = "2nd"
            elif placements[0] == 3:
                placement_str = "3rd"
            elif placements[0] == 4:
                placement_str = "4th"
            else:
                placement_str = f"{placements[0]}th"
        else:
            placement_str = f"{min(placements)}th-{max(placements)}th (tied)"
        
        print(f"{placement_str:<15} {base:<15} {points:<15}")
    
    print("=" * 60)
