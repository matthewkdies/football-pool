export type GameStatus =
  | 'STATUS_SCHEDULED'
  | 'STATUS_IN_PROGRESS'
  | 'STATUS_HALFTIME'
  | 'STATUS_FINAL';

export type SeasonType = 'PRESEASON' | 'REGULAR_SEASON' | 'POSTSEASON';

export type WinningType = 'MOST' | 'LEAST' | 'FIFTY' | 'PLAYOFF' | 'SUPER_BOWL';

export interface TeamSummary {
  abbreviation: string;
  city: string;
  name: string;
  full_name: string;
  logo_url: string;
}

export interface ScoreboardGame {
  id: string;
  home_team: TeamSummary;
  home_team_score: number;
  away_team: TeamSummary;
  away_team_score: number;
  espn_url: string;
  gametime: string;
  status: GameStatus;
  display_clock?: string | null;
  quarter?: number | null;
}

export interface ScoreboardWeek {
  season_year: number;
  season_type: SeasonType;
  week: number;
  winning_type: WinningType;
  games: ScoreboardGame[];
  pool_winning_team_abbrs: string[];
  pot_amount: number;
  last_polled_at: string;
}
