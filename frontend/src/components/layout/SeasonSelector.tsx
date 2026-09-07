import { ChevronDown } from 'lucide-react';
import { useSeasons } from '../../context/SeasonContext';

export function SeasonSelector() {
  const { seasonsData, selectedSeason, setSelectedSeason } = useSeasons();

  if (!seasonsData || seasonsData.tracked_seasons.length <= 1) {
    return null;
  }

  const formatSeasonSpan = (year: number) => `${year}-${year + 1}`;
  const formatCompactSeasonSpan = (year: number) => `'${String(year).slice(-2)}-'${String(year + 1).slice(-2)}`;

  return (
    <div className="dropdown dropdown-end">
      <div
        tabIndex={0}
        role="button"
        className="btn btn-xs sm:btn-sm btn-outline gap-1 font-semibold px-2 sm:px-3"
      >
        <span className="sm:hidden">{formatCompactSeasonSpan(selectedSeason)}</span>
        <span className="hidden sm:inline">{formatSeasonSpan(selectedSeason)}</span>
        <ChevronDown className="h-3.5 w-3.5 sm:h-4 sm:w-4 opacity-70" />
      </div>
      <ul
        tabIndex={0}
        className="dropdown-content menu z-50 mt-2 p-2 shadow-xl bg-base-200 rounded-box w-36 border border-base-content/10"
      >
        {seasonsData.tracked_seasons.map((year) => (
          <li key={year}>
            <button
              className={`text-sm ${selectedSeason === year ? 'active font-bold' : ''}`}
              onClick={() => setSelectedSeason(year)}
            >
              {formatSeasonSpan(year)}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
