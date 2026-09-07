import { useState, useEffect, useCallback } from 'react';
import { ScoreboardWeek } from '../types';
import { scoreboardApi } from '../api/scoreboardApi';

export function useScoreboard() {
  const [scoreboard, setScoreboard] = useState<ScoreboardWeek | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const fetchScoreboard = useCallback(async (showLoading = true) => {
    if (showLoading) setIsLoading(true);
    setError(null);
    try {
      const data = await scoreboardApi.getScoreboard();
      setScoreboard(data);
      setLastUpdated(new Date());
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch scoreboard');
    } finally {
      if (showLoading) setIsLoading(false);
    }
  }, []);

  const refresh = async () => {
    setIsRefreshing(true);
    setError(null);
    try {
      const data = await scoreboardApi.refreshScoreboard();
      setScoreboard(data);
      setLastUpdated(new Date());
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to refresh scoreboard');
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchScoreboard(true);

    // Adaptive auto-polling interval
    const intervalMs = 45000; // 45 seconds polling
    const timer = setInterval(() => {
      fetchScoreboard(false);
    }, intervalMs);

    return () => clearInterval(timer);
  }, [fetchScoreboard]);

  return {
    scoreboard,
    isLoading,
    isRefreshing,
    error,
    lastUpdated,
    refresh,
    reload: () => fetchScoreboard(true),
  };
}
