import {
  WeaponType,
  AgeBracket,
  Gender,
  CompetitionType,
  TournamentStatus,
  ClubStatus
} from './enums';

export { WeaponType, AgeBracket, Gender, CompetitionType, TournamentStatus, ClubStatus };

// =====================================================
// CLUB TYPE
// =====================================================
export interface Club {
  club_id: string;
  club_name: string;
  start_year?: number;
  status: ClubStatus;
  weapon_club?: WeaponType;
  fencer_count: number;
  total_points?: number;
  weapon_distribution?: {
    Sabre: number;
    Foil: number;
    Epee: number;
  };
  bracket_distribution?: Record<string, number>;
  members?: ClubMember[];
}

export interface ClubMember {
  fencer_id: number;
  full_name: string;
  dob?: string;
  gender: Gender;
  weapon: WeaponType;
  brackets: AgeBracket[];
  total_points: number;
}

// =====================================================
// RANKING TYPE
// =====================================================
export interface Ranking {
  ranking_id: number;
  fencer_id: number;
  bracket_name: AgeBracket;
  points: number;
  fencer?: Fencer;
}

export interface ClubRanking {
  rank: number;
  club_id: string;
  club_name: string;
  weapon_specialization: WeaponType;
  total_points: number;
  fencer_count: number;
  avg_points: number;
}

// =====================================================
// FENCER TYPE
// =====================================================
export interface Fencer {
  fencer_id: number;
  full_name: string;
  first_name: string;
  last_name: string;
  dob: string;
  age: number;
  bracket: AgeBracket; // Computed from age
  gender: Gender;
  weapon: WeaponType;
  club_id: string;
  club_name?: string;
  rankings: Ranking[];
  total_points?: number;
}

// =====================================================
// TOURNAMENT TYPE
// =====================================================
export interface Tournament {
  tournament_id: number;
  tournament_name: string;
  date: string;
  weapon: WeaponType;
  bracket: AgeBracket;
  competition_type: CompetitionType;
  gender?: Gender;
  location?: string;
  max_participants?: number;
  participant_count?: number;
  is_full?: boolean;
  description?: string;
  status: TournamentStatus;
  season_id?: number;
  created_at?: string;
}

// =====================================================
// TOURNAMENT RESULT TYPE
// =====================================================
export interface TournamentResult {
  result_id: number;
  tournament_id: number;
  fencer_id: number;
  placement: number;
  points_awarded: number;
}

// =====================================================
// FILTER TYPES
// =====================================================
export interface TournamentFilters {
  status?: TournamentStatus;
  weapon?: WeaponType;
  bracket?: AgeBracket;
  competition_type?: CompetitionType;
  search?: string;
}

export interface FencerFilters {
  weapon?: WeaponType;
  bracket?: AgeBracket;
  gender?: Gender;
  club_id?: string;
  search?: string;
}

// =====================================================
// API RESPONSE WRAPPER
// =====================================================
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: string;
}
