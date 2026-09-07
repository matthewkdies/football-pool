import { Search } from 'lucide-react';

interface AssignmentFiltersProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  selectedConference: string;
  onConferenceChange: (conf: string) => void;
}

export function AssignmentFilters({
  searchTerm,
  onSearchChange,
  selectedConference,
  onConferenceChange,
}: AssignmentFiltersProps) {
  return (
    <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 mb-6">
      {/* Search Input */}
      <div className="relative flex-1 max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 opacity-50" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Filter by owner or team name..."
          className="input input-sm sm:input-md input-bordered w-full pl-9 bg-base-100 text-sm"
        />
      </div>

      {/* Conference Filter Tabs */}
      <div className="tabs tabs-boxed bg-base-200 p-1 self-start sm:self-auto">
        {['ALL', 'AFC', 'NFC'].map((conf) => (
          <button
            key={conf}
            onClick={() => onConferenceChange(conf)}
            className={`tab tab-sm font-semibold transition-all ${
              selectedConference === conf ? 'tab-active !bg-primary !text-primary-content shadow-xs' : ''
            }`}
          >
            {conf === 'ALL' ? 'All Teams' : conf}
          </button>
        ))}
      </div>
    </div>
  );
}
