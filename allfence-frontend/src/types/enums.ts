// =====================================================
// WEAPON TYPES - What fencers compete with
// =====================================================
export enum WeaponType {
  SABRE = "Sabre",
  FOIL = "Foil",
  EPEE = "Epee"
}

// =====================================================
// AGE BRACKETS - Fencer age categories
// =====================================================
export enum AgeBracket {
  U11 = "U11",
  U13 = "U13",
  U15 = "U15",
  CADET = "Cadet",
  JUNIOR = "Junior",
  SENIOR = "Senior"
}

// =====================================================
// GENDER - Competitor gender
// =====================================================
export enum Gender {
  MALE = "M",
  FEMALE = "F"
}

// =====================================================
// COMPETITION TYPE - Tournament level/prestige
// =====================================================
export enum CompetitionType {
  LOCAL = "Local",
  REGIONAL = "Regional",
  NATIONAL = "National",
  CHAMPIONSHIP = "Championship",
  INTERNATIONAL = "International"
}

// =====================================================
// TOURNAMENT STATUS - What stage is tournament in?
// =====================================================
export enum TournamentStatus {
  UPCOMING = "Upcoming",
  REGISTRATION_OPEN = "Registration Open",
  IN_PROGRESS = "In Progress",
  COMPLETED = "Completed",
  CANCELLED = "Cancelled"
}

// =====================================================
// CLUB STATUS - Is the club active?
// =====================================================
export enum ClubStatus {
  ACTIVE = "Active",
  INACTIVE = "Inactive",
  PENDING = "Pending",
  SUSPENDED = "Suspended"
}
