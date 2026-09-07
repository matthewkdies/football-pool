import { RefreshCw, DollarSign, Award, Clock } from 'lucide-react';
import { ScoreboardWeek } from '../../types';

interface ScoreboardHeaderProps {
  scoreboard: ScoreboardWeek;
  isRefreshing: boolean;
  lastUpdated: Date;
  onRefresh: () => void;
}

export function ScoreboardHeader({
  scoreboard,
  isRefreshing,
  lastUpdated,
  onRefresh,
}: ScoreboardHeaderProps) {
  const getRuleDescription = () => {
    switch (scoreboard.winning_type) {
      case 'MOST':
        return 'Highest scoring team wins the pot!';
      case 'LEAST':
        return 'Lowest scoring team wins the pot!';
      case 'PLAYOFF':
        return 'Every playoff game winner earns $10!';
      case 'SUPER_BOWL':
        return 'The Super Bowl Champion takes the grand $25 payout!';
      default:
        return 'Weekly payout rules apply!';
    }
  };

  const getWeekLabel = () => {
    if (scoreboard.season_type === 'POSTSEASON') {
      if (scoreboard.week === 5) return 'Super Bowl';
      if (scoreboard.week === 4) return 'Conference Championships';
      return `Playoffs · Round ${scoreboard.week}`;
    }
    if (scoreboard.season_type === 'PRESEASON') {
      return `Preseason · Week ${scoreboard.week}`;
    }
    return `Week ${scoreboard.week}`;
  };

  return (
    <div className="bg-base-200/80 border border-base-content/10 rounded-2xl p-4 sm:p-6 mb-6 shadow-sm">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        {/* Left: Week & Rules */}
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-1.5">
            <h1 className="text-2xl sm:text-3xl font-black text-base-content">
              {getWeekLabel()}
            </h1>
            <span className="badge badge-primary font-bold text-xs">
              {scoreboard.winning_type === 'MOST'
                ? 'Most Points Week'
                : scoreboard.winning_type === 'LEAST'
                ? 'Least Points Week'
                : scoreboard.winning_type}
            </span>
          </div>
          <p className="text-xs sm:text-sm text-base-content/70 flex items-center gap-1.5">
            <Award className="h-4 w-4 text-warning shrink-0" />
            <span>{getRuleDescription()}</span>
            <span className="opacity-50">·</span>
            <span className="text-success font-medium">50-Point Bonus active ($50)</span>
          </p>
        </div>

        {/* Right: Pot & Controls */}
        <div className="flex items-center justify-between sm:justify-end gap-3 shrink-0">
          {/* Pot Card */}
          <div className="flex items-center gap-2.5 bg-base-100 border border-base-content/10 px-4 py-2 rounded-xl shadow-xs">
            <div className="p-2 bg-success/15 text-success rounded-lg">
              <DollarSign className="h-5 w-5" />
            </div>
            <div>
              <div className="text-[10px] uppercase font-bold text-base-content/60">
                Rolling Pot
              </div>
              <div className="text-xl font-extrabold text-success font-mono leading-none">
                ${scoreboard.pot_amount}
              </div>
            </div>
          </div>

          {/* Refresh & Live Indicator */}
          <div className="flex flex-col items-end gap-1">
            <button
              onClick={onRefresh}
              disabled={isRefreshing}
              className="btn btn-sm btn-outline gap-1.5 shadow-xs"
              aria-label="Refresh scores"
            >
              <RefreshCw
                className={`h-3.5 w-3.5 ${isRefreshing ? 'animate-spin text-primary' : ''}`}
              />
              <span>{isRefreshing ? 'Refreshing...' : 'Refresh'}</span>
            </button>
            <div className="text-[10px] text-base-content/50 flex items-center gap-1">
              <Clock className="h-2.5 w-2.5" />
              <span>
                {lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
