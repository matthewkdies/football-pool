import { WinningGameResponse } from '../../types';
import { Award, AlertCircle } from 'lucide-react';

interface WeeklyWinnersTableProps {
  winningGames: WinningGameResponse[];
}

export function WeeklyWinnersTable({ winningGames }: WeeklyWinnersTableProps) {
  if (winningGames.length === 0) {
    return (
      <div className="card bg-base-100 border border-base-content/10 p-8 text-center shadow-sm">
        <div className="flex flex-col items-center justify-center gap-2 text-base-content/60">
          <AlertCircle className="h-10 w-10 opacity-40 text-warning" />
          <h3 className="font-bold text-base">No winners recorded yet</h3>
          <p className="text-xs max-w-sm">
            Weekly results will appear here as games are finalized and resolution is computed every Tuesday!
          </p>
        </div>
      </div>
    );
  }

  const formatWinType = (type: string) => {
    switch (type) {
      case 'MOST':
        return 'Most Points';
      case 'LEAST':
        return 'Least Points';
      case 'FIFTY':
        return '50-Point Bonus';
      case 'PLAYOFF':
        return 'Playoff Win';
      case 'SUPER_BOWL':
        return 'Super Bowl';
      default:
        return type;
    }
  };

  return (
    <div className="card bg-base-100 border border-base-content/10 shadow-sm overflow-hidden">
      <div className="p-4 bg-base-200/50 border-b border-base-content/10 flex items-center justify-between">
        <div className="flex items-center gap-2 font-bold text-base">
          <Award className="h-5 w-5 text-primary" />
          <span>Weekly Payout Log</span>
        </div>
        <span className="text-xs text-base-content/60">{winningGames.length} Payouts</span>
      </div>

      <div className="overflow-x-auto">
        <table className="table table-zebra table-sm sm:table-md w-full">
          <thead>
            <tr className="text-xs uppercase opacity-70">
              <th className="w-16">Week</th>
              <th>Winning Team</th>
              <th>Owner</th>
              <th>Category</th>
              <th className="text-right">Payout</th>
            </tr>
          </thead>
          <tbody>
            {winningGames.map((game) => (
              <tr key={game.id} className="hover:bg-base-200">
                <td className="font-mono font-bold text-sm text-base-content/80">
                  W{game.week}
                </td>
                <td>
                  <div className="flex items-center gap-2.5">
                    <img
                      src={`/static/${game.team.logo_url}`}
                      alt={game.team.full_name}
                      className="w-6 h-6 object-contain"
                    />
                    <span className="font-bold text-sm">
                      {game.team.city} {game.team.name}
                    </span>
                  </div>
                </td>
                <td className="font-medium text-sm">
                  {game.winning_owner_name}
                </td>
                <td className="whitespace-nowrap">
                  <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-semibold border border-base-content/20 bg-base-200/60">
                    {formatWinType(game.winning_type)}
                  </span>
                </td>
                <td className="text-right font-mono font-bold text-success">
                  +${game.winnings}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
