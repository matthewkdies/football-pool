import { ScoreboardGame, TeamSummary } from '../../types';
import { GameStatusBadge } from './GameStatusBadge';
import { Trophy, User } from 'lucide-react';

interface GameCardProps {
  game: ScoreboardGame;
  winningTeamAbbrs: string[];
  ownerMap: Record<string, string>;
  claimedTeamAbbr?: string | null;
}

export function GameCard({
  game,
  winningTeamAbbrs,
  ownerMap,
  claimedTeamAbbr,
}: GameCardProps) {
  const isStarted = game.status !== 'STATUS_SCHEDULED';

  const renderTeamSection = (team: TeamSummary, score: number) => {
    const isWinningPot = winningTeamAbbrs.includes(team.abbreviation);
    const isUserTeam = claimedTeamAbbr === team.abbreviation;
    const ownerName = ownerMap[team.abbreviation];

    return (
      <div
        className={`flex flex-col items-center flex-1 p-2.5 rounded-xl transition-all ${
          isWinningPot
            ? 'bg-success/15 border border-success/30 shadow-xs'
            : isUserTeam
            ? 'bg-primary/10 border border-primary/30'
            : 'bg-base-200/50 hover:bg-base-200'
        }`}
      >
        {/* Team Logo */}
        <div className="relative w-14 h-14 sm:w-16 sm:h-16 flex items-center justify-center mb-2">
          <img
            src={`/static/${team.logo_url}`}
            alt={team.full_name}
            className="w-full h-full object-contain filter drop-shadow-sm"
            loading="lazy"
          />
          {isWinningPot && (
            <span
              className="absolute -top-1 -right-1 badge badge-success badge-xs p-1 shadow-sm"
              title="Currently meeting winning condition!"
            >
              <Trophy className="h-2.5 w-2.5 text-success-content" />
            </span>
          )}
        </div>

        {/* Team Names */}
        <div className="text-center w-full">
          <div className="font-bold text-xs sm:text-sm leading-tight truncate">
            {team.city}
          </div>
          <div className="font-semibold text-xs opacity-75 truncate">
            {team.name}
          </div>
        </div>

        {/* Score */}
        {isStarted && (
          <div className="text-2xl sm:text-3xl font-extrabold font-mono mt-1.5 text-base-content">
            {score}
          </div>
        )}

        {/* Owner Name Badge */}
        {ownerName ? (
          <div
            className={`mt-2 text-[11px] font-semibold px-2 py-0.5 rounded-full flex items-center gap-1 truncate max-w-full ${
              isUserTeam
                ? 'bg-primary text-primary-content shadow-xs'
                : 'bg-base-300 text-base-content/80'
            }`}
          >
            <User className="h-3 w-3 shrink-0" />
            <span className="truncate">{ownerName}</span>
          </div>
        ) : (
          <div className="mt-2 text-[10px] opacity-40 italic">Unassigned</div>
        )}
      </div>
    );
  };

  return (
    <div
      onClick={() => {
        if (game.espn_url) {
          window.open(game.espn_url, '_blank', 'noopener,noreferrer');
        }
      }}
      className="card bg-base-100 border border-base-content/10 shadow-md hover:shadow-xl hover:border-primary/40 transition-all cursor-pointer overflow-hidden group"
      title="Click to view ESPN Gamecast"
    >
      <div className="card-body p-3.5 sm:p-4">
        <div className="flex items-center justify-between gap-2">
          {/* Away Team */}
          {renderTeamSection(game.away_team, game.away_team_score)}

          {/* Center: Game Status & vs */}
          <div className="flex flex-col items-center justify-center px-1 shrink-0">
            <GameStatusBadge game={game} />
            <span className="text-[10px] font-bold opacity-30 mt-1 uppercase tracking-wider">
              VS
            </span>
          </div>

          {/* Home Team */}
          {renderTeamSection(game.home_team, game.home_team_score)}
        </div>
      </div>
    </div>
  );
}
