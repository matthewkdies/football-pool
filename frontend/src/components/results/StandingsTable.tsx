import { StandingItem } from '../../types';
import { useAuth } from '../../context/AuthContext';
import { Trophy } from 'lucide-react';

interface StandingsTableProps {
  standings: StandingItem[];
}

export function StandingsTable({ standings }: StandingsTableProps) {
  const { auth } = useAuth();

  const getRankBadge = (index: number) => {
    if (index === 0) return <span className="text-xl">🥇</span>;
    if (index === 1) return <span className="text-xl">🥈</span>;
    if (index === 2) return <span className="text-xl">🥉</span>;
    return <span className="font-mono font-bold text-xs opacity-60">#{index + 1}</span>;
  };

  return (
    <div className="card bg-base-100 border border-base-content/10 shadow-sm overflow-hidden">
      <div className="p-4 bg-base-200/50 border-b border-base-content/10 flex items-center justify-between">
        <div className="flex items-center gap-2 font-bold text-base">
          <Trophy className="h-5 w-5 text-warning" />
          <span>Season Leaderboard</span>
        </div>
        <span className="text-xs text-base-content/60">{standings.length} Members</span>
      </div>

      <div className="overflow-x-auto">
        <table className="table table-zebra table-sm sm:table-md w-full">
          <thead>
            <tr className="text-xs uppercase opacity-70">
              <th className="w-12 text-center">Rank</th>
              <th>Member</th>
              <th>Assigned Team</th>
              <th className="text-right">Total Winnings</th>
            </tr>
          </thead>
          <tbody>
            {standings.map((item, index) => {
              const isUser = auth?.claimed && auth.member?.id === item.member.id;

              return (
                <tr
                  key={item.member.id}
                  className={`transition-colors ${
                    isUser ? 'bg-primary/15 font-semibold hover:bg-primary/20' : 'hover:bg-base-200'
                  }`}
                >
                  <td className="text-center font-semibold">
                    {getRankBadge(index)}
                  </td>
                  <td>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm sm:text-base">
                        {item.member.full_name}
                      </span>
                      {isUser && (
                        <span className="badge badge-primary badge-xs font-semibold">
                          You
                        </span>
                      )}
                    </div>
                  </td>
                  <td>
                    <div className="flex items-center gap-2.5">
                      <img
                        src={`/static/${item.team.logo_url}`}
                        alt={item.team.full_name}
                        className="w-6 h-6 object-contain filter drop-shadow-xs"
                      />
                      <span className="text-xs sm:text-sm font-medium">
                        {item.team.city} {item.team.name}
                      </span>
                    </div>
                  </td>
                  <td className="text-right font-mono font-extrabold text-sm sm:text-base text-success">
                    ${item.total_winnings}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
