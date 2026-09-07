import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { UserCheck, X } from 'lucide-react';

export function ClaimProfileModal() {
  const { isClaimModalOpen, closeClaimModal, members, claim, auth } = useAuth();
  const [selectedMemberId, setSelectedMemberId] = useState<number | ''>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  if (!isClaimModalOpen) return null;

  const handleClaim = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMemberId) return;

    setIsSubmitting(true);
    setError(null);
    try {
      await claim(Number(selectedMemberId));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to claim identity');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal modal-open backdrop-blur-sm z-[100]">
      <div className="modal-box relative max-w-md border border-base-content/10 shadow-2xl bg-base-200 z-[101]">
        <button
          onClick={closeClaimModal}
          className="btn btn-sm btn-circle btn-ghost absolute right-3 top-3"
          aria-label="Close"
        >
          <X className="h-4 w-4" />
        </button>

        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 bg-primary/10 text-primary rounded-xl">
            <UserCheck className="h-6 w-6" />
          </div>
          <div>
            <h3 className="text-xl font-bold">Claim Your Profile</h3>
            <p className="text-xs text-base-content/70">
              Join the family banter and see your team highlighted!
            </p>
          </div>
        </div>

        {auth?.claimed && auth.member && (
          <div className="alert alert-info py-2 mb-4 text-xs">
            <span>
              Currently claimed as <strong>{auth.member.full_name}</strong>
              {auth.current_team ? ` (${auth.current_team.full_name})` : ''}. You can switch anytime.
            </span>
          </div>
        )}

        {error && (
          <div className="alert alert-error py-2 mb-4 text-xs">
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleClaim} className="space-y-4">
          <div>
            <label className="label">
              <span className="label-text font-semibold">Select your name</span>
            </label>
            <select
              value={selectedMemberId}
              onChange={(e) => setSelectedMemberId(e.target.value ? Number(e.target.value) : '')}
              className="select select-bordered w-full bg-base-100"
              required
            >
              <option value="" disabled>
                -- Choose yourself from the roster --
              </option>
              {members.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.full_name}
                </option>
              ))}
            </select>
          </div>

          <div className="text-xs text-base-content/60 leading-relaxed">
            No password required! We save a secure session cookie to your browser so you stay recognized during game day.
          </div>

          <div className="modal-action mt-6">
            <button
              type="button"
              onClick={closeClaimModal}
              className="btn btn-ghost"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!selectedMemberId || isSubmitting}
              className="btn btn-primary"
            >
              {isSubmitting ? (
                <>
                  <span className="loading loading-spinner loading-xs"></span>
                  Claiming...
                </>
              ) : (
                'Claim Identity'
              )}
            </button>
          </div>
        </form>
      </div>
      <div className="modal-backdrop bg-black/40" onClick={closeClaimModal} />
    </div>
  );
}
