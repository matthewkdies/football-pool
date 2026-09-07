import { ScoreboardGame } from '../../types';

interface GameStatusBadgeProps {
  game: ScoreboardGame;
}

export function GameStatusBadge({ game }: GameStatusBadgeProps) {
  if (game.status === 'STATUS_FINAL') {
    return (
      <div className="flex flex-col items-center">
        <span className="badge badge-neutral badge-sm font-bold tracking-wider text-[10px] px-1.5 py-0">
          FINAL
        </span>
      </div>
    );
  }

  if (game.status === 'STATUS_HALFTIME') {
    return (
      <div className="flex flex-col items-center">
        <span className="badge badge-warning badge-sm font-bold tracking-wider text-[10px] px-1.5 py-0 animate-pulse">
          HALF
        </span>
      </div>
    );
  }

  if (game.status === 'STATUS_IN_PROGRESS') {
    return (
      <div className="flex flex-col items-center gap-0.5">
        <span className="badge badge-error badge-sm font-bold tracking-wider text-[10px] px-1.5 py-0 text-white flex items-center gap-1 animate-pulse">
          <span className="w-1.5 h-1.5 rounded-full bg-white"></span>
          LIVE
        </span>
        <span className="text-[11px] font-mono font-bold text-base-content/80 whitespace-nowrap">
          {game.quarter ? `Q${game.quarter}` : ''} {game.display_clock || ''}
        </span>
      </div>
    );
  }

  // Scheduled / Queued
  const formatDate = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' });
    } catch {
      return '';
    }
  };

  const formatTime = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  return (
    <div className="flex flex-col items-center text-center whitespace-nowrap">
      <span className="text-[11px] sm:text-xs font-bold text-base-content/80">
        {formatDate(game.gametime)}
      </span>
      <span className="text-[10px] sm:text-[11px] font-mono text-base-content/60">
        {formatTime(game.gametime)}
      </span>
    </div>
  );
}
