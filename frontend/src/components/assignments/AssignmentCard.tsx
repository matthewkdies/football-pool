import { SeasonAssignmentResponse } from '../../types';
import { ExternalLink, User } from 'lucide-react';

interface AssignmentCardProps {
  assignment: SeasonAssignmentResponse;
  isUserTeam: boolean;
}

export function AssignmentCard({ assignment, isUserTeam }: AssignmentCardProps) {
  const { team, member } = assignment;

  const espnTeamUrl = `https://www.espn.com/nfl/team/_/name/${team.abbreviation.toLowerCase()}/${team.city.toLowerCase().replace(/\s+/g, '-')}-${team.name.toLowerCase().replace(/\s+/g, '-')}`;

  return (
    <div
      className={`card bg-base-100 border transition-all hover:shadow-lg ${
        isUserTeam
          ? 'border-primary shadow-md bg-primary/5'
          : 'border-base-content/10 shadow-xs'
      }`}
    >
      <div className="card-body p-4 flex flex-row items-center gap-4">
        {/* Team Logo link */}
        <a
          href={espnTeamUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="relative group shrink-0 w-14 h-14 p-1 rounded-xl bg-base-200 flex items-center justify-center hover:scale-105 transition-transform"
          title={`View ${team.full_name} on ESPN`}
        >
          <img
            src={`/static/${team.logo_url}`}
            alt={team.full_name}
            className="w-full h-full object-contain filter drop-shadow-xs"
            loading="lazy"
          />
          <ExternalLink className="absolute top-1 right-1 h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity text-base-content/70" />
        </a>

        {/* Team & Member Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5">
            <span className="font-extrabold text-sm sm:text-base truncate text-base-content">
              {team.city} {team.name}
            </span>
            <span className="badge badge-ghost badge-xs font-bold text-[10px] shrink-0">
              {team.abbreviation}
            </span>
          </div>

          {/* Owner Info */}
          <div className="flex items-center gap-1.5 mt-1.5">
            <User className="h-3.5 w-3.5 opacity-60 shrink-0" />
            <span className="text-xs sm:text-sm font-semibold truncate text-base-content/80">
              {member.full_name}
            </span>
            {isUserTeam && (
              <span className="badge badge-primary badge-xs font-bold shrink-0">
                You
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
