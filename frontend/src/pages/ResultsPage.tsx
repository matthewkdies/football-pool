import { useState, useEffect } from 'react';
import { useSeasons } from '../context/SeasonContext';
import { poolApi } from '../api/poolApi';
import { PoolResultsResponse, PotResponse } from '../types';
import { PotCard } from '../components/results/PotCard';
import { StandingsTable } from '../components/results/StandingsTable';
import { WeeklyWinnersTable } from '../components/results/WeeklyWinnersTable';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { AlertCircle } from 'lucide-react';

export function ResultsPage() {
  const { selectedSeason } = useSeasons();
  const [results, setResults] = useState<PoolResultsResponse | null>(null);
  const [pot, setPot] = useState<PotResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);

    Promise.all([
      poolApi.getResults(selectedSeason),
      poolApi.getPot(selectedSeason),
    ])
      .then(([resultsData, potData]) => {
        if (isMounted) {
          setResults(resultsData);
          setPot(potData);
        }
      })
      .catch((err: unknown) => {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Failed to load results');
        }
      })
      .finally(() => {
        if (isMounted) setIsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [selectedSeason]);

  if (isLoading) {
    return <LoadingSpinner message={`Loading results for ${selectedSeason}-${selectedSeason + 1}...`} />;
  }

  if (error || !results) {
    return (
      <div className="alert alert-error max-w-xl mx-auto my-12 shadow-lg">
        <AlertCircle className="h-5 w-5" />
        <div>
          <h4 className="font-bold">Error loading results</h4>
          <p className="text-xs">{error || 'Please try again later.'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl sm:text-3xl font-black text-base-content">
          Season Standings & Results
        </h1>
        <p className="text-xs sm:text-sm text-base-content/70 mt-1">
          Historical payouts, weekly winners, and cumulative leaderboards for {selectedSeason}-{selectedSeason + 1}.
        </p>
      </div>

      {/* Pot Banner */}
      <PotCard amount={pot?.amount ?? 10} seasonYear={selectedSeason} />

      {/* Tables Grid: Standings on the Left, Weekly Winners on the Right */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
        {/* Standings Leaderboard */}
        <div>
          <StandingsTable standings={results.standings} />
        </div>

        {/* Weekly Winners Log */}
        <div>
          <WeeklyWinnersTable winningGames={results.winning_games} />
        </div>
      </div>
    </div>
  );
}
