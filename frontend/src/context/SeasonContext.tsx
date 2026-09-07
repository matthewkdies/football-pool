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
  const currentDefaultYear =
    new Date().getMonth() >= 6 ? new Date().getFullYear() : new Date().getFullYear() - 1;

  const [seasonsData, setSeasonsData] = useState<SeasonsResponse | null>(null);
  const [selectedSeason, setSelectedSeason] = useState<number>(currentDefaultYear);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [hasUserSelected, setHasUserSelected] = useState<boolean>(false);

  const handleSetSelectedSeason = useCallback((season: number) => {
    setHasUserSelected(true);
    setSelectedSeason(season);
  }, []);

  const refreshSeasons = useCallback(async () => {
    try {
      const data = await poolApi.getSeasons();
      setSeasonsData(data);
      if (!hasUserSelected) {
        setSelectedSeason(data.current_season);
      } else {
        setSelectedSeason((prev) => (data.tracked_seasons.includes(prev) ? prev : data.current_season));
      }
    } catch {
      // Fallback
      setSeasonsData({ current_season: currentDefaultYear, tracked_seasons: [2024, 2025, currentDefaultYear] });
      if (!hasUserSelected) {
        setSelectedSeason(currentDefaultYear);
      }
    } finally {
      setIsLoading(false);
    }
  }, [currentDefaultYear, hasUserSelected]);

  useEffect(() => {
    refreshSeasons();
  }, [refreshSeasons]);

  return (
    <SeasonContext.Provider
      value={{
        seasonsData,
        selectedSeason,
        setSelectedSeason: handleSetSelectedSeason,
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
