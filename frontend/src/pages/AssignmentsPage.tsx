import { useState, useEffect, useMemo } from 'react';
import { useSeasons } from '../context/SeasonContext';
import { useAuth } from '../context/AuthContext';
import { poolApi } from '../api/poolApi';
import { SeasonAssignmentResponse } from '../types';
import { AssignmentCard } from '../components/assignments/AssignmentCard';
import { AssignmentFilters } from '../components/assignments/AssignmentFilters';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { AlertCircle } from 'lucide-react';

export function AssignmentsPage() {
  const { selectedSeason } = useSeasons();
  const { auth } = useAuth();
  const [assignments, setAssignments] = useState<SeasonAssignmentResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedConference, setSelectedConference] = useState<string>('ALL');

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);

    poolApi
      .getAssignments(selectedSeason)
      .then((data) => {
        if (isMounted) setAssignments(data);
      })
      .catch((err: unknown) => {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Failed to load assignments');
        }
      })
      .finally(() => {
        if (isMounted) setIsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [selectedSeason]);

  // Known AFC and NFC team abbreviations for robust fallback
  const afcTeams = useMemo(() => new Set([
    'BUF', 'MIA', 'NE', 'NYJ',
    'BAL', 'CIN', 'CLE', 'PIT',
    'HOU', 'IND', 'JAX', 'TEN',
    'DEN', 'KC', 'LV', 'LAC',
  ]), []);

  // Filter assignments based on search term and conference
  const filteredAssignments = useMemo(() => {
    return assignments.filter((a) => {
      const matchesSearch =
        searchTerm === '' ||
        a.member.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        a.team.city.toLowerCase().includes(searchTerm.toLowerCase()) ||
        a.team.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        a.team.abbreviation.toLowerCase().includes(searchTerm.toLowerCase());

      const teamConf = a.team.conference || (afcTeams.has(a.team.abbreviation) ? 'AFC' : 'NFC');
      const matchesConference =
        selectedConference === 'ALL' || teamConf === selectedConference;

      return matchesSearch && matchesConference;
    });
  }, [assignments, searchTerm, selectedConference, afcTeams]);

  // Sort assignments alphabetically by team city
  const sortedAssignments = useMemo(() => {
    return [...filteredAssignments].sort((a, b) =>
      a.team.city.localeCompare(b.team.city)
    );
  }, [filteredAssignments]);

  if (isLoading) {
    return <LoadingSpinner message={`Loading assignments for ${selectedSeason}-${selectedSeason + 1}...`} />;
  }

  if (error) {
    return (
      <div className="alert alert-error max-w-xl mx-auto my-12 shadow-lg">
        <AlertCircle className="h-5 w-5" />
        <div>
          <h4 className="font-bold">Error loading assignments</h4>
          <p className="text-xs">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl sm:text-3xl font-black text-base-content">
          Team Assignments
        </h1>
        <p className="text-xs sm:text-sm text-base-content/70 mt-1">
          Each member is assigned an NFL franchise for the {selectedSeason}-{selectedSeason + 1} season.
        </p>
      </div>

      {/* Search & Filters */}
      <AssignmentFilters
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        selectedConference={selectedConference}
        onConferenceChange={setSelectedConference}
      />

      {/* Assignments Grid */}
      {sortedAssignments.length === 0 ? (
        <div className="card bg-base-100 border border-base-content/10 p-12 text-center shadow-sm">
          <p className="font-semibold text-base-content/70">
            No assignments match your search filter.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {sortedAssignments.map((a) => (
            <AssignmentCard
              key={a.id}
              assignment={a}
              isUserTeam={Boolean(auth?.claimed && auth.member?.id === a.member.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
