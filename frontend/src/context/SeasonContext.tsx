import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { SeasonsResponse } from '../types';
import { poolApi } from '../api/poolApi';

interface SeasonContextType {
  seasonsData: SeasonsResponse | null;
  selectedSeason: number;
  setSelectedSeason: (season: number) => void;
  isLoading: boolean;
  refreshSeasons: () => Promise<void>;
}

const SeasonContext = createContext<SeasonContextType | undefined>(undefined);

export function SeasonProvider({ children }: { children: ReactNode }) {
  const [seasonsData, setSeasonsData] = useState<SeasonsResponse | null>(null);
  const [selectedSeason, setSelectedSeason] = useState<number>(2025);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const refreshSeasons = useCallback(async () => {
    try {
      const data = await poolApi.getSeasons();
      setSeasonsData(data);
      setSelectedSeason((prev) => (data.tracked_seasons.includes(prev) ? prev : data.current_season));
    } catch {
      // Fallback
      setSeasonsData({ current_season: 2025, tracked_seasons: [2024, 2025] });
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshSeasons();
  }, [refreshSeasons]);

  return (
    <SeasonContext.Provider
      value={{
        seasonsData,
        selectedSeason,
        setSelectedSeason,
        isLoading,
        refreshSeasons,
      }}
    >
      {children}
    </SeasonContext.Provider>
  );
}

export function useSeasons(): SeasonContextType {
  const context = useContext(SeasonContext);
  if (!context) {
    throw new Error('useSeasons must be used within a SeasonProvider');
  }
  return context;
}
