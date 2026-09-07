import { request } from './client';
import { ScoreboardWeek } from '../types';

export const scoreboardApi = {
  /** Fetch latest scoreboard from cache */
  getScoreboard: () => request<ScoreboardWeek>('/api/scoreboard'),

  /** Trigger an on-demand ESPN refresh and return updated scoreboard */
  refreshScoreboard: () =>
    request<ScoreboardWeek>('/api/scoreboard/refresh', {
      method: 'POST',
    }),
};
