import { MemberResponse } from './auth';
import { TeamSummary } from './scoreboard';

export interface SeasonAssignmentResponse {
  id: number;
  season_year: number;
  member: MemberResponse;
  team: TeamSummary;
}

export interface WinningGameResponse {
  id: number;
  season_year: number;
  week: number;
  winnings: number;
  winning_type: string;
  team: TeamSummary;
  winning_owner_name: string;
}

export interface StandingItem {
  member: MemberResponse;
  team: TeamSummary;
  total_winnings: number;
}

export interface PoolResultsResponse {
  season_year: number;
  winning_games: WinningGameResponse[];
  standings: StandingItem[];
}

export interface PotResponse {
  season_year: number;
  amount: number;
}

export interface SeasonsResponse {
  current_season: number;
  tracked_seasons: number[];
}
