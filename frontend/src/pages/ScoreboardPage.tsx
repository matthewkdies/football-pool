import { useEffect, useState, useMemo } from 'react';
import { useScoreboard } from '../hooks/useScoreboard';
import { useAuth } from '../context/AuthContext';
import { poolApi } from '../api/poolApi';
import { SeasonAssignmentResponse } from '../types';
import { ScoreboardHeader } from '../components/scoreboard/ScoreboardHeader';
import { GameCard } from '../components/scoreboard/GameCard';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { AlertCircle } from 'lucide-react';

export function ScoreboardPage() {
  const { scoreboard, isLoading, isRefreshing, error, lastUpdated, refresh } = useScoreboard();
  const { auth } = useAuth();
  const [assignments, setAssignments] = useState<SeasonAssignmentResponse[]>([]);

  // Fetch current season assignments to resolve owner names on game cards
  useEffect(() => {
    if (scoreboard?.season_year) {
      poolApi.getAssignments(scoreboard.season_year).then(setAssignments).catch(() => {});
    }
  }, [scoreboard?.season_year]);

  // Build team abbreviation -> owner full name map
  const ownerMap = useMemo(() => {
    const map: Record<string, string> = {};
    for (const a of assignments) {
      if (map[a.team.abbreviation]) {
        map[a.team.abbreviation] += `, ${a.member.full_name}`;
      } else {
        map[a.team.abbreviation] = a.member.full_name;
      }
    }
    return map;
  }, [assignments]);

  if (isLoading) {
    return <LoadingSpinner message="Loading live scoreboard..." />;
  }

  if (error || !scoreboard) {
    return (
      <div className="alert alert-error max-w-xl mx-auto my-12 shadow-lg">
        <AlertCircle className="h-5 w-5" />
        <div>
          <h4 className="font-bold">Could not load scoreboard</h4>
          <p className="text-xs">{error || 'Please try refreshing.'}</p>
        </div>
        <button onClick={refresh} className="btn btn-sm btn-outline">
          Retry
        </button>
      </div>
    );
  }

  // Sort games: in-progress first, then halftime, scheduled by kickoff, final last
  const sortedGames = [...scoreboard.games].sort((a, b) => {
    const statusOrder: Record<string, number> = {
      STATUS_IN_PROGRESS: 1,
      STATUS_HALFTIME: 2,
      STATUS_SCHEDULED: 3,
      STATUS_FINAL: 4,
    };
    const orderDiff = (statusOrder[a.status] || 5) - (statusOrder[b.status] || 5);
    if (orderDiff !== 0) return orderDiff;
    return new Date(a.gametime).getTime() - new Date(b.gametime).getTime();
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
      {/* Header Banner with Pot and Week Info */}
      <ScoreboardHeader
        scoreboard={scoreboard}
        isRefreshing={isRefreshing}
        lastUpdated={lastUpdated}
        onRefresh={refresh}
      />

      {/* Game Cards Grid */}
      {sortedGames.length === 0 ? (
        <div className="card bg-base-100 border border-base-content/10 p-12 text-center shadow-sm">
          <p className="font-semibold text-base-content/70">
            No games scheduled for this week yet.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4 gap-4">
          {sortedGames.map((game) => (
            <GameCard
              key={game.id}
              game={game}
              winningTeamAbbrs={scoreboard.pool_winning_team_abbrs}
              ownerMap={ownerMap}
              claimedTeamAbbr={auth?.current_team?.abbreviation}
            />
          ))}
        </div>
      )}
    </div>
  );
}
