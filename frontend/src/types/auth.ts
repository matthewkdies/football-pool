import { TeamSummary } from './scoreboard';

export interface MemberResponse {
  id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  created_at: string;
}

export interface ClaimRequest {
  member_id: number;
}

export interface AuthMeResponse {
  claimed: boolean;
  member: MemberResponse | null;
  current_team: TeamSummary | null;
}
