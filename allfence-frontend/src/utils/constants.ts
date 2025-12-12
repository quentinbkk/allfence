import { WeaponType, AgeBracket, Gender, CompetitionType } from '../types/enums';

export const WEAPON_CHOICES = Object.values(WeaponType);
export const BRACKET_CHOICES = Object.values(AgeBracket);
export const GENDER_CHOICES = Object.values(Gender);
export const COMPETITION_TYPE_CHOICES = Object.values(CompetitionType);

export const POINT_MULTIPLIERS: Record<CompetitionType, number> = {
  [CompetitionType.LOCAL]: 0.5,
  [CompetitionType.REGIONAL]: 1.0,
  [CompetitionType.NATIONAL]: 1.5,
  [CompetitionType.CHAMPIONSHIP]: 2.0,
  [CompetitionType.INTERNATIONAL]: 2.5,
};

export const BRACKET_AGE_RANGES: Record<AgeBracket, { min: number; max: number }> = {
  [AgeBracket.U11]: { min: 0, max: 10 },
  [AgeBracket.U13]: { min: 11, max: 12 },
  [AgeBracket.U15]: { min: 13, max: 14 },
  [AgeBracket.CADET]: { min: 15, max: 16 },
  [AgeBracket.JUNIOR]: { min: 17, max: 19 },
  [AgeBracket.SENIOR]: { min: 20, max: 120 },
};
