import { request } from './client';
import {
  PoolResultsResponse,
  PotResponse,
  SeasonAssignmentResponse,
  SeasonsResponse,
} from '../types';

export const poolApi = {
  /** Get current and tracked seasons */
  getSeasons: () => request<SeasonsResponse>('/api/pool/seasons'),

  /** Get team assignments for a specific season */
  getAssignments: (seasonYear?: number) => {
    const query = seasonYear ? `?season_year=${seasonYear}` : '';
    return request<SeasonAssignmentResponse[]>(`/api/pool/assignments${query}`);
  },

  /** Get weekly winners and dynamic standings */
  getResults: (seasonYear?: number) => {
    const query = seasonYear ? `?season_year=${seasonYear}` : '';
    return request<PoolResultsResponse>(`/api/pool/results${query}`);
  },

  /** Get pot amount for a season */
  getPot: (seasonYear?: number) => {
    const query = seasonYear ? `?season_year=${seasonYear}` : '';
    return request<PotResponse>(`/api/pool/pot${query}`);
  },
};
